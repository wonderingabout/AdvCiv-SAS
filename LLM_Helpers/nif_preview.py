#!/usr/bin/env python3
# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)

# <!-- custom: NifSkope shows Civ4's .nif models only in its window, so an agent chose Peat Works' model on 2026-11-08 from its textures alone.
# This draws still pictures instead, in the spirit of NifSkope's view: PyFFI reads the model, skinned meshes are posed by their bones, and numpy fills every pixel from its texture with a depth buffer and simple lighting, over a dark floor grid.
# A scene with its own camera, such as a religion-founding "movie", can also be seen through that camera at several moments of its keyframed animation.
# The first version filled each triangle with one colour, which showed shapes but blurred every texture; it is still no substitute for the game's lighting, particles or effects.
# See README_Art_Tools.md. (Claude code Opus 5.5 + GPT-6.1-Sol) -->

# <!-- custom: argparse parses the options; math builds the camera; os finds textures beside the model; time is patched for PyFFI; numpy rasterizes; PyFFI reads the .nif; PIL (Pillow) reads textures and saves the PNG. (Claude code Opus 5.5) -->
# <!-- custom: External clips are selected by KFM event code and applied to matching NIF nodes.
# Inspecting a clip reports visibility changes and skipped track types before rendering. (GPT-6.1-Sol) -->

import argparse
from collections import Counter
import math
import os
from pathlib import Path
import time

# <!-- custom: PyFFI 2.2.3, the latest release, still calls time.clock, removed in Python 3.8, and imports distutils, removed in 3.12 (setuptools provides it).
# Restore the first before importing it. (Claude code Opus 5.5 + GPT-6.1-Sol) -->
if not hasattr(time, "clock"):
	time.clock = time.perf_counter

# <!-- custom: numpy rasterizes, PyFFI reads the .nif and Pillow loads textures and saves the PNG; fail with the install command if one is missing. (Claude code Opus 5.5) -->
try:
	import numpy as np
	from pyffi.formats.kfm import KfmFormat
	from pyffi.formats.nif import NifFormat
	from PIL import Image, ImageDraw
except ImportError as exc:
	raise SystemExit("needs numpy, PyFFI and Pillow: py -m pip install numpy pyffi setuptools pillow (%s)" % exc)


def matrix_from(rotation, translation, scale):
	# <!-- custom: Gamebryo multiplies row vectors (p * M), so a 4x4 matrix holds scale times rotation on top and the translation in the bottom row. (Claude code Opus 5.5) -->
	m = np.identity(4)
	m[:3, :3] = scale * rotation
	m[3, :3] = translation
	return m


def node_matrix(node):
	r, t = node.rotation, node.translation
	return matrix_from(np.array([[r.m_11, r.m_12, r.m_13], [r.m_21, r.m_22, r.m_23], [r.m_31, r.m_32, r.m_33]]), (t.x, t.y, t.z), node.scale)


def quaternion_rows(w, x, y, z):
	# <!-- custom: Rotation matrix of a unit quaternion, transposed for Gamebryo's row vectors. (Claude code Opus 5.5) -->
	return np.array([[1 - 2 * (y * y + z * z), 2 * (x * y - w * z), 2 * (x * z + w * y)], [2 * (x * y + w * z), 1 - 2 * (x * x + z * z), 2 * (y * z - w * x)], [2 * (x * z - w * y), 2 * (y * z + w * x), 1 - 2 * (x * x + y * y)]]).T


def sample(keys, at, mix):
	if not keys:
		return None
	if at <= keys[0].time:
		return keys[0].value
	for before, after in zip(keys, keys[1:]):
		if at <= after.time:
			span = after.time - before.time
			return mix(before.value, after.value, (at - before.time) / span if span else 0.0)
	return keys[-1].value


# <!-- custom: Fish swam along straight lines, while in the game they leap in arcs.
# Fish_Normal stores each fish's path as about 15 quadratic (Bezier) position keys over 10 s and its turns as TBC rotation keys, and linear sampling joined them with straight segments and plain slerps.
# Evaluate them as Hermite curves instead.
# See README_Art_Tools.md. (Claude code Opus 5.5) -->
def vector(value):
	if isinstance(value, (int, float)):
		return np.array([float(value)])
	if hasattr(value, "w"):
		return np.array([value.w, value.x, value.y, value.z])
	return np.array([value.x, value.y, value.z])


def hermite(p0, p1, m0, m1, f):
	f2, f3 = f * f, f * f * f
	return (2 * f3 - 3 * f2 + 1) * p0 + (f3 - 2 * f2 + f) * m0 + (-2 * f3 + 3 * f2) * p1 + (f3 - f2) * m1


def tbc_tangents(times, points, keys, i):
	# <!-- custom: Kochanek-Bartels tangents, scaled for unevenly spaced keys; an end key uses its one neighbour. (Claude code Opus 5.5) -->
	tbc = getattr(keys[i], "tbc", None)
	t, b, c = (tbc.t, tbc.b, tbc.c) if tbc is not None else (0.0, 0.0, 0.0)
	last = len(points) - 1
	before = points[i] - points[i - 1] if i > 0 else points[min(i + 1, last)] - points[i]
	after = points[i + 1] - points[i] if i < last else before
	outgoing = (1 - t) * ((1 - c) * (1 + b) * before + (1 + c) * (1 - b) * after) / 2
	incoming = (1 - t) * ((1 + c) * (1 + b) * before + (1 - c) * (1 - b) * after) / 2
	if 0 < i < last:
		gap_before, gap_after = times[i] - times[i - 1], times[i + 1] - times[i]
		if gap_before + gap_after > 0:
			outgoing *= 2 * gap_after / (gap_before + gap_after)
			incoming *= 2 * gap_before / (gap_before + gap_after)
	return incoming, outgoing


def curve_sample(keys, at, interpolation, quaternion=False):
	# <!-- custom: Returns the value at time at as a numpy array: linear (1), quadratic (2) and TBC (3) keys are curves through each key.
	# PyFFI's names for quadratic tangents read backwards: in Fish_Normal, a key's backward value matches the direction of the segment leaving it and the next key's forward value the one arriving, in units of the whole segment.
	# For example, a fish rising from (-45,-11,-20) to (-17,-33,15) leaves with (19,-24,0) and arrives with (38,-18,0), so it leaves the bottom of its dive flat and rises in an arc.
	# Quaternions have no stored tangents, so a quadratic or TBC rotation uses TBC tangents on sign-aligned quaternions, then normalizes. (Claude code Opus 5.5) -->
	keys = list(keys)
	if not keys:
		return None
	times = [key.time for key in keys]
	points = [vector(key.value) for key in keys]
	if quaternion:
		for i in range(1, len(points)):
			if points[i] @ points[i - 1] < 0:
				points[i] = -points[i]
	if at <= times[0]:
		result = points[0]
	elif at >= times[-1]:
		result = points[-1]
	else:
		i = next(index for index in range(len(times) - 1) if at <= times[index + 1])
		span = times[i + 1] - times[i]
		f = (at - times[i]) / span if span else 0.0
		kind = int(interpolation)
		if kind == 2 and not quaternion:
			result = hermite(points[i], points[i + 1], vector(keys[i].backward), vector(keys[i + 1].forward), f)
		elif kind in (2, 3):
			result = hermite(points[i], points[i + 1], tbc_tangents(times, points, keys, i)[1], tbc_tangents(times, points, keys, i + 1)[0], f)
		else:
			result = points[i] * (1 - f) + points[i + 1] * f
	if quaternion:
		return result / np.linalg.norm(result)
	return float(result[0]) if result.shape == (1,) else result


def slerp(a, b, f):
	qa, qb = np.array([a.w, a.x, a.y, a.z]), np.array([b.w, b.x, b.y, b.z])
	if qa @ qb < 0:
		qb = -qb
	q = qa * (1 - f) + qb * f
	return q / np.linalg.norm(q)


# <!-- custom: Visibility is a step track.
# The Catapult's rock stays visible until its hide key, then stays hidden until the reload key. (GPT-6.1-Sol) -->
def bool_value(track, at):
	value = track.bool_value
	if track.data:
		for key in track.data.data.keys:
			if key.time > at:
				break
			value = key.value
	return bool(value)


def read_nif(path):
	data = NifFormat.Data()
	with path.open("rb") as handle:
		data.read(handle)
	return data


def read_kfm(path):
	# <!-- custom: PyFFI's Header reader refers to fields defined on Kfm instead.
	# Read that struct with the version from the file header. (GPT-6.1-Sol) -->
	with path.open("rb") as handle:
		prefix = b";Gamebryo KFM File Version "
		header = handle.readline(64).strip()
		version = KfmFormat.version_number(header[len(prefix):].decode("ascii")) if header.startswith(prefix) else None
		if version not in KfmFormat.versions.values():
			raise SystemExit("unrecognized KFM header in %s" % path)
		handle.seek(0)
		context = KfmFormat.Data()
		context.version = version
		data = KfmFormat.Kfm()
		data.read(handle, context)
		if handle.read(1):
			raise SystemExit("unread data at the end of %s" % path)
		return data


def kfm_path(kfm, reference):
	path = kfm.parent / reference.decode("latin-1").replace("\\", "/")
	if path.is_file():
		return path
	# <!-- custom: Match the game's case-insensitive asset paths on case-sensitive systems too. (GPT-6.1-Sol) -->
	current = Path(path.anchor) if path.is_absolute() else Path(".")
	parts = path.parts[1:] if path.is_absolute() else path.parts
	for part in parts:
		exact = current / part
		if exact.exists():
			current = exact
			continue
		match = next((entry for entry in current.iterdir() if entry.name.lower() == part.lower()), None)
		if match is None:
			raise SystemExit("missing asset referenced by %s: %s" % (kfm, path))
		current = match
	return current


def read_clip(path, index):
	sequences = [root for root in read_nif(path).roots if isinstance(root, NifFormat.NiControllerSequence)]
	if not 0 <= index < len(sequences):
		raise SystemExit("no controller sequence at index %d in %s (%d sequences)" % (index, path, len(sequences)))
	return sequences[index]


def clip_tracks(sequence, nodes=None):
	transforms, visibility, opacity, skipped = {}, {}, {}, Counter()
	print("%s: %.3f to %.3f s" % (sequence.name.decode("latin-1"), sequence.start_time, sequence.stop_time))
	for block in sequence.controlled_blocks:
		name, track = block.get_node_name(), block.interpolator
		if isinstance(track, NifFormat.NiBoolInterpolator) and block.get_controller_type() == b"NiVisController":
			if track.data and track.data.data.keys:
				states = ", ".join("%.3f s=%s" % (key.time, bool(key.value)) for key in track.data.data.keys)
			else:
				states = str(bool(track.bool_value))
			print("  visibility %s: %s" % (name.decode("latin-1"), states))
			visibility[name] = track
		elif isinstance(track, (NifFormat.NiTransformInterpolator, NifFormat.NiBSplineCompTransformInterpolator)):
			transforms[name] = track
		elif isinstance(track, NifFormat.NiFloatInterpolator) and block.get_controller_type() == b"NiAlphaController":
			opacity[name] = track
		else:
			skipped[type(track).__name__] += 1
	if nodes is not None:
		# <!-- custom: A clip can target a node absent from the chosen NIF variant.
		# Report missing targets so a partial pose is distinguishable from a fully matched clip. (GPT-6.1-Sol) -->
		missing = (transforms.keys() | visibility.keys() | opacity.keys()) - nodes
		if missing:
			print("  targets absent from model: %s" % ", ".join(name.decode("latin-1") for name in sorted(missing)))
		transforms = {name: track for name, track in transforms.items() if name in nodes}
		visibility = {name: track for name, track in visibility.items() if name in nodes}
		opacity = {name: track for name, track in opacity.items() if name in nodes}
	print("  %d transform tracks, %d visibility tracks, %d opacity tracks" % (len(transforms), len(visibility), len(opacity)))
	if skipped:
		print("  unsupported by renderer: %s" % ", ".join("%s (%d)" % item for item in sorted(skipped.items())))
	return transforms, visibility, opacity


def transform_data(node):
	controller = node.controller
	while controller is not None:
		if isinstance(controller, NifFormat.NiTransformController) and controller.interpolator is not None and getattr(controller.interpolator, "data", None) is not None:
			return controller.interpolator.data
		controller = controller.next_controller
	return None


def spline_sample(values, fraction):
	# <!-- custom: PyFFI decodes the compressed control points.
	# Evaluate the open uniform cubic spline because the control points are not sampled poses. (GPT-6.1-Sol) -->
	points = np.asarray(list(values), dtype=float)
	count = len(points)
	if not count:
		return None
	degree = min(3, count - 1)
	end = count - degree
	t = min(1, max(0, fraction)) * end
	span = min(count - 1, int(t) + degree)
	knots = np.clip(np.arange(count + degree + 1) - degree, 0, end)
	window = points[span - degree:span + 1].copy()
	for level in range(1, degree + 1):
		for j in range(degree, level - 1, -1):
			k = span - degree + j
			weight = (t - knots[k]) / (knots[k + degree + 1 - level] - knots[k])
			window[j] = (1 - weight) * window[j - 1] + weight * window[j]
	return window[-1]


def local_matrix(node, at, interpolator):
	# <!-- custom: At a given time, a node with keyframes takes its translation, rotation and scale from them, interpolated linearly at first (slerp for rotations), which was close enough for a still; curve_sample now follows their Bezier and TBC curves too, since animations showed the difference. (Claude code Opus 5.5 + GPT-6.1-Sol) -->
	data = None
	if isinstance(interpolator, NifFormat.NiBSplineCompTransformInterpolator):
		base = node_matrix(node)
		span = interpolator.stop_time - interpolator.start_time
		fraction = (at - interpolator.start_time) / span if span > 0 else 0
		translation = spline_sample(interpolator.get_translations(), fraction)
		quaternion = spline_sample(interpolator.get_rotations(), fraction)
		scale = spline_sample(interpolator.get_scales(), fraction)
		rotation = base[:3, :3] / max(node.scale, 1e-9)
		if quaternion is not None and np.linalg.norm(quaternion) > 1e-9:
			rotation = quaternion_rows(*(quaternion / np.linalg.norm(quaternion)))
		return matrix_from(rotation, translation if translation is not None else base[3, :3], scale if scale is not None else node.scale)
	if interpolator is not None:
		data = interpolator.data
	elif at is not None:
		data = transform_data(node)
	if data is None and interpolator is None:
		return node_matrix(node)
	base = node_matrix(node)
	# <!-- custom: A KF can store a constant instead of keys.
	# Gamebryo uses -FLT_MAX for an unset interpolator channel. (GPT-6.1-Sol) -->
	translation = curve_sample(data.translations.keys, at, data.translations.interpolation) if data else None
	if translation is None and interpolator is not None and interpolator.translation.x > -1e30:
		translation = interpolator.translation
	if translation is not None and not isinstance(translation, np.ndarray):
		translation = np.array([translation.x, translation.y, translation.z])
	rotation = None
	quaternion = None
	if data and data.rotation_type != 4 and len(data.quaternion_keys):
		quaternion = curve_sample(data.quaternion_keys, at, data.rotation_type, quaternion=True)
	elif interpolator is not None and interpolator.rotation.w > -1e30:
		quaternion = interpolator.rotation
	if quaternion is not None:
		if not isinstance(quaternion, np.ndarray):
			quaternion = np.array([quaternion.w, quaternion.x, quaternion.y, quaternion.z])
		rotation = quaternion_rows(*quaternion)
	if data and data.rotation_type == 4:
		angles = [curve_sample(group.keys, at, group.interpolation) for group in data.xyz_rotations]
		if all(angle is not None for angle in angles):
			# <!-- custom: Apply X, Y and Z in that order with row vectors.
			# Montezuma's root and shoulder poses distinguish this order from the reverse. (GPT-6.1-Sol) -->
			x, y, z = (angle / 2 for angle in angles)
			rotation = quaternion_rows(math.cos(x), math.sin(x), 0, 0) @ quaternion_rows(math.cos(y), 0, math.sin(y), 0) @ quaternion_rows(math.cos(z), 0, 0, math.sin(z))
	scale = curve_sample(data.scales.keys, at, data.scales.interpolation) if data else None
	if scale is None and interpolator is not None and interpolator.scale > -1e30:
		scale = interpolator.scale
	return matrix_from(rotation if rotation is not None else base[:3, :3] / max(node.scale, 1e-9), translation if translation is not None else base[3, :3], scale if scale is not None else node.scale)


def animation_range(blocks):
	starts, stops = [], []
	for block in blocks:
		if isinstance(block, NifFormat.NiTransformController):
			starts.append(block.start_time)
			stops.append(block.stop_time)
	return (min(starts), max(stops)) if starts else None


# <!-- custom: load_texture first read only a shape's base texture.
# slot now names another texturing slot too: the detail texture that holds the painted airframe under Civ4's mechanical shader, and the decal on the Civilopedia water surface. (Claude code Opus 5.5) -->
def team_color_base(shape):
	return any(isinstance(prop, NifFormat.NiTexturingProperty) and prop.has_base_texture and prop.base_texture.source and prop.base_texture.source.file_name.decode("latin-1").replace("\\", "/").rpartition("/")[2].lower().startswith("teamcolor") for prop in shape.properties)


def load_texture(shape, folder, cache, slot="base_texture"):
	for prop in shape.properties:
		if isinstance(prop, NifFormat.NiTexturingProperty) and getattr(prop, "has_" + slot) and getattr(prop, slot).source:
			# <!-- custom: The last part of the name rather than os.path.basename, which on Windows reads the name //eldercouncil.dds, in the Metsehaf Bet's model, as a network path with no file and drew only its shadow. (Claude code Opus 5.5) -->
			name = getattr(prop, slot).source.file_name.decode("latin-1").replace("\\", "/").rpartition("/")[2]
			if name not in cache:
				# <!-- custom: Civ4 finds a model's textures by name in its own folder, ignoring case, so look there the same way. (Claude code Opus 5.5) -->
				match = [entry for entry in os.listdir(folder) if entry.lower() == name.lower()]
				cache[name] = np.asarray(Image.open(os.path.join(folder, match[0])).convert("RGBA"), dtype=np.float32) / 255.0 if match else None
			return cache[name]
	return None


# <!-- custom: Added facing, the camera's right, up and toward rows that billboard nodes turn to; None leaves them as stored, for every preview but a plot's effects. (Claude code Opus 5.5) -->
def world_matrices(node, parent, out, at, transforms, look_targets=None, bound_names=None, facing=None):
	if bound_names is None:
		bound_names = set()
	track = transforms.get(node.name)
	if track is not None:
		# <!-- custom: KF tracks bind to one node by name.
		# The Persian Immortal has a second same-named BIP hierarchy with different bind transforms.
		# Animating both distorts the mesh. (GPT-6.1-Sol) -->
		if node.name in bound_names:
			track = None
		else:
			bound_names.add(node.name)
	matrix = local_matrix(node, at, track) @ parent
	if facing is not None and isinstance(node, NifFormat.NiBillboardNode):
		# <!-- custom: A billboard's cards lie flat at height 0 in the file and the engine turns them to the camera; left flat, the ground hid Fallout's glow and only its corners poked through hills, as gold bars. (Claude code Opus 5.5) -->
		matrix[:3, :3] = facing * np.linalg.norm(matrix[0, :3])
	if look_targets is not None and isinstance(node.controller, NifFormat.NiTransformController):
		look = node.controller.interpolator
		if isinstance(look, NifFormat.NiLookAtInterpolator) and look.unknown_short == 4 and id(look.look_at) in look_targets:
			# <!-- custom: The religion camera rig stores its position in the look-at interpolator's point track.
			# Its child NiCamera points along the rig's negative Z axis. (GPT-6.1-Sol) -->
			position_track = look.unknown_link_1
			if isinstance(position_track, NifFormat.NiPoint3Interpolator) and position_track.data:
				position = curve_sample(position_track.data.data.keys, at, position_track.data.data.interpolation)
				if position is not None:
					if not isinstance(position, np.ndarray):
						position = np.array((position.x, position.y, position.z))
					matrix[3] = np.append(position, 1) @ parent
			forward = look_targets[id(look.look_at)][3, :3] - matrix[3, :3]
			right = np.cross(forward, (0, 0, 1))
			if np.linalg.norm(right) > 1e-9:
				forward /= np.linalg.norm(forward)
				right /= np.linalg.norm(right)
				matrix[:3, :3] = (right, np.cross(right, forward), -forward)
	out[id(node)] = matrix
	if isinstance(node, NifFormat.NiNode):
		for child in node.children:
			if child is not None:
				world_matrices(child, matrix, out, at, transforms, look_targets, bound_names, facing)


def skinned_points(node, vertices, worlds):
	# <!-- custom: Apply the bind offset, pose the vertex in skeleton-root space, then apply the skin offset and the geometry's world transform.
	# Using world matrices avoids PyFFI's ancestor-chain lookup, which failed for the Persian Immortal.
	# The order matters for rotating the Bomber's propellers about their own hubs. (Claude code Opus 5.5 + GPT-6.1-Sol) -->
	skin = node.skin_instance
	root = worlds.get(id(skin.skeleton_root))
	if root is None:
		return np.zeros_like(vertices), np.ones(len(vertices), dtype=bool)
	to_world = np.linalg.inv(root) @ node_matrix(skin.data.skin_transform) @ worlds[id(node)]
	homogeneous = np.hstack([vertices, np.ones((len(vertices), 1))])
	posed = np.zeros((len(vertices), 3))
	weight_sum = np.zeros(len(vertices))
	for bone, bone_data in zip(skin.bones, skin.data.bone_list):
		if bone is None or id(bone) not in worlds:
			continue
		matrix = node_matrix(bone_data.skin_transform) @ worlds[id(bone)] @ to_world
		for weight in bone_data.vertex_weights:
			posed[weight.index] += weight.weight * (homogeneous[weight.index] @ matrix)[:3]
			weight_sum[weight.index] += weight.weight
	unweighted = weight_sum == 0
	posed[~unweighted] /= weight_sum[~unweighted][:, None]
	return posed, unweighted


def texture_scroll(node, slot, at):
	# <!-- custom: The water scene scrolls its base and decal textures independently.
	# Sample their embedded U/V translation keys in the texture's own slot. (GPT-6.1-Sol) -->
	offset = np.zeros(2)
	for prop in node.properties:
		if not isinstance(prop, NifFormat.NiTexturingProperty):
			continue
		controller = prop.controller
		while controller:
			if isinstance(controller, NifFormat.NiTextureTransformController) and controller.texture_slot == slot and controller.operation in (0, 1):
				track = controller.interpolator
				if isinstance(track, NifFormat.NiFloatInterpolator) and track.data:
					value = sample(track.data.data.keys, at, lambda a, b, f: a + (b - a) * f)
					if value is not None:
						offset[controller.operation] = value
			controller = controller.next_controller
	return offset


# <!-- custom: Fallout's cards add a texture of 247 188 79 times a key of 1 0.78 0.33, which is green 0.6 and blue 0.1 of red and about 0.8 of the game's strength; this per-channel factor fits a 56-screenshot in-game burst covering its whole 8 s loop (2026-11-09), whose light added green 0.63 and blue 0.2 of red, red saturating on bright ground.
# A first fit (1, 1.2, 1.8) to a 5 s burst measured against each pixel's tenth percentile rather than its darkest moment gave too yellow a green of 0.72. (Claude code Opus 5.5) -->
EFFECT_GLOW_TINT = np.array((1.25, 1.33, 2.5), dtype=np.float32)


# <!-- custom: How strongly the two sliding layers of a feature's water show: their stored alpha of 0.2 left the Oasis almost still, with no crossing lines, while an in-game burst (2026-11-09) shows them plainly.
# An even mix lit as the terrain is, at 0.4 opacity, averages 72 131 145 in the pool against the game's 72 127 136; 0.5 unlit gave a duller pool and spread the layer's outline over the dark rim. (Claude code Opus 5.5) -->
WATER_LAYER_MIX = 0.5
WATER_LAYER_OPACITY = 0.4
# <!-- custom: How far a scrolling feature's soil moves toward the ground's colour, its greens kept: the Oasis's rim had a darkest tenth of 104, now 114, against the game's 128, and a mean of 158 152 120, now 165 158 124, against 182 160 126.
# Lightening only the half-transparent texels barely moved it, to 109, as the rim is mostly painted opaque. (Claude code Opus 5.5) -->
GROUND_EDGE_LIGHTEN = 0.25


def scrolled_surface(node, folder, cache, texture, at, ground_colour):
	# <!-- custom: A plot feature's scrolling texture at time at, or at its start: each layer is shifted by its own keys and static offset, then the decal is laid over the base by its alpha.
	# The Oasis water slides two copies of oasis_water.dds in opposite directions, which makes the crossing lines seen in game; the rasterizer takes one texture per shape, so they are composited here. (Claude code Opus 5.5) -->
	prop = next((prop for prop in node.properties if isinstance(prop, NifFormat.NiTexturingProperty)), None)
	if prop is None:
		return texture
	# <!-- custom: plot_scene lights the terrain; imported here because it imports this module. (Claude code Opus 5.5) -->
	from plot_scene import map_light

	def placed(image, layer, slot):
		offset = texture_scroll(node, slot, at or 0.0)
		if layer.has_texture_transform:
			offset += (layer.translation.u, layer.translation.v)
		height, width = image.shape[:2]
		return np.roll(image, (-int(round(offset[1] * height)), -int(round(offset[0] * width))), axis=(0, 1))
	base = placed(texture, prop.base_texture, 0)
	decal = load_texture(node, folder, cache, "decal_0_texture") if prop.has_decal_0_texture else None
	if decal is None:
		lit = map_light(base)
		if ground_colour is not None:
			# <!-- custom: Graded, as a hard cut between soil and green texels drew blocky patches in the rim. (Claude code Opus 5.5) -->
			edge = np.clip((lit[..., 0:1] + 0.06 - lit[..., 1:2]) / 0.06, 0, 1) * GROUND_EDGE_LIGHTEN
			lit[..., :3] = lit[..., :3] * (1 - edge) + ground_colour * edge
		return lit
	decal = placed(decal, prop.decal_0_texture, 6)
	result = base.copy()
	result[..., :3] = base[..., :3] * (1 - WATER_LAYER_MIX) + decal[..., :3] * WATER_LAYER_MIX
	result[..., 3] = WATER_LAYER_OPACITY
	return map_light(result)


def glow_track(node):
	# <!-- custom: A card's animated self-illumination keys, or None; a survey of 59 installed mods found effect cards with no material and with other controllers chained before this one. (Claude code Opus 5.5) -->
	for prop in node.properties:
		controller = prop.controller if isinstance(prop, NifFormat.NiMaterialProperty) else None
		while controller is not None:
			if isinstance(controller, NifFormat.NiMaterialColorController) and controller.target_color == 3 and controller.interpolator is not None and controller.interpolator.data is not None:
				return controller.interpolator.data.data
			controller = controller.next_controller
	return None


def effect_surface(node, data, uvs, texture, blend, glow, at):
	# <!-- custom: A billboard effect's card, as Fallout's: a card whose self-illumination is animated adds light, at glow, a fraction of its brightest key; any other is haze, faded by its vertex alpha, which the first preview ignored and so drew Fallout's smoke as a hard-edged grey polygon.
	# Both ignore the depth buffer, as their NiZBufferProperty asks.
	# With a time at, as in a GIF, the card follows the file's own 8 s colour keys, which swell and fade each card on its own beat, and the haze scrolls; the keys may dip just below zero. (Claude code Opus 5.5) -->
	track = glow_track(node)
	if track is not None:
		colour = np.clip(curve_sample(track.keys, at, track.interpolation), 0, None) if at is not None else vector(max(track.keys, key=lambda key: key.value.x + key.value.y + key.value.z).value) * glow
		painted = texture.copy()
		painted[..., :3] *= colour.astype(np.float32) * EFFECT_GLOW_TINT
		return uvs, painted, "glow", 0.0
	if blend in ("add", "add-alpha"):
		return uvs, texture, "glow", 0.0
	if at is not None:
		uvs = uvs + texture_scroll(node, 0, at)
	if data.has_vertex_colors:
		uvs = np.column_stack([uvs, [colour.a for colour in data.vertex_colors]])
	return uvs, texture, "haze", 0.0


# <!-- custom: Added glow, a billboard effect's light fraction, and scrolling, for a plot feature's sliding textures; their defaults leave other previews unchanged. (Claude code Opus 5.5) -->
def collect(node, folder, cache, args, meshes, worlds, visibility, at, overlays=None, opacity=None, glow=None, scrolling=False):
	world = worlds[id(node)]
	# <!-- custom: Triangle strips too: the Peat bonus model has one NiTriStrips part, which the first version skipped. (Claude code Opus 5.5 + GPT-6.1-Sol) -->
	if isinstance(node, (NifFormat.NiTriShape, NifFormat.NiTriStrips)) and node.data:
		texture = load_texture(node, folder, cache)
		if texture is None and node.shader_name.startswith(b"TCiv4Mech"):
			# <!-- custom: Civ4's mechanical shader puts the painted airframe in the detail slot, even on the Bomber's non-shader variant. (GPT-6.1-Sol) -->
			texture = load_texture(node, folder, cache, "detail_texture")
		if team_color_base(node):
			# <!-- custom: Civ4 paints the player's colour through TeamColor.bmp, the base texture, and the unit's picture is decal 0, whose alpha shows where the colour comes through.
			# Drawing the base texture made Realism Invictus's Chivalric Knight's horse solid red, and leaving it out hid the BtS Warrior's body, so lay the decal over --team-color. (Claude code Opus 5.5) -->
			decal = load_texture(node, folder, cache, "decal_0_texture")
			if decal is not None:
				alpha = decal[..., 3:4]
				texture = np.concatenate([decal[..., :3] * alpha + np.array(args.team_color, dtype=np.float32) / 255 * (1 - alpha), np.ones_like(alpha)], axis=2)
		team = np.array(args.team_color, dtype=np.float32) / 255
		if texture is not None and node.shader_name.startswith(b"TCiv4Skinning") and b"NoTeamC" not in node.shader_name:
			# <!-- custom: The skinning shaders paint the player's colour where the base texture's alpha is low: the Champion's tabard came out grey-brown without it. (Claude code Opus 5.5) -->
			alpha = texture[..., 3:4]
			texture = np.concatenate([texture[..., :3] * alpha + team * (1 - alpha), np.ones_like(alpha)], axis=2)
		elif texture is not None and node.shader_name.startswith(b"TFlag"):
			# <!-- custom: A flag shader tints its picture with the player's colours, from PlayerColor01 and 02, which the game supplies and no file holds; the Champion's shield drew white. (Claude code Opus 5.5) -->
			texture = np.concatenate([texture[..., :3] * team, texture[..., 3:4]], axis=2)
		data = node.data
		# <!-- custom: Untextured shapes are usually hidden helpers; the Peat bonus model has two grey "Sphere" shapes the game does not draw, which the first render showed as pyramids. (Claude code Opus 5.5 + GPT-6.1-Sol) -->
		triangles = list(data.get_triangles())
		if (texture is not None or args.untextured) and triangles:
			vertices = np.array([(v.x, v.y, v.z) for v in data.vertices])
			points = (np.hstack([vertices, np.ones((len(vertices), 1))]) @ world)[:, :3]
			if node.skin_instance is not None:
				posed, unweighted = skinned_points(node, vertices, worlds)
				points = np.where(unweighted[:, None], points, posed)
			uvs = np.array([(uv.u, uv.v) for uv in data.uv_sets[0]]) if len(data.uv_sets) else np.zeros((len(vertices), 2))
			triangles = np.array([tuple(tri) for tri in triangles])
			# <!-- custom: Follow the shape's NiAlphaProperty: bit 0 blends, bit 9 tests against its threshold.
			# The first version cut every texel under half alpha, which dropped the Peat bonus's ground decal (blend and test, threshold 1). (Claude code Opus 5.5) -->
			alpha = [prop for prop in node.properties if isinstance(prop, NifFormat.NiAlphaProperty)]
			blend = bool(alpha and alpha[0].flags & 1)
			if blend and (alpha[0].flags & 0x1ff) in (1, 13):
				blend = "add" if (alpha[0].flags & 0x1ff) == 1 else "add-alpha"
			# <!-- custom: The BtS Walls' shadow quad multiplies what is under it (source factor zero, destination factor source colour); drawn as an ordinary blend, it was a pale square. (Claude code Opus 5.5) -->
			if blend and (alpha[0].flags & 0x1ff) == 0x43:
				blend = "multiply"
			threshold = alpha[0].threshold / 255.0 if alpha and alpha[0].flags & 0x200 else (0.5 if blend else -1.0)
			if scrolling and texture is not None:
				texture = scrolled_surface(node, folder, cache, texture, at, getattr(args, "ground_colour", None))
			if glow is not None and texture is not None and blend:
				uvs, texture, blend, threshold = effect_surface(node, data, uvs, texture, blend, glow, at)
			if texture is not None and opacity and node.name in opacity:
				# <!-- custom: The Fish clip animates material alpha on its splash rings, which otherwise stay bright through the whole clip. (GPT-6.1-Sol) -->
				track = opacity[node.name]
				value = sample(track.data.data.keys, at, lambda a, b, f: a + (b - a) * f) if track.data else track.float_value
				if value is not None and value > -1e30:
					texture = texture.copy()
					texture[:, :, 3] *= min(1, max(0, value * args.opacity_gain))
					blend = "add-alpha" if blend in ("add", "add-alpha") else True
					threshold = 0.0
			water = load_texture(node, folder, cache, "decal_0_texture") if overlays is not None and node.name.lower() == b"geometry_water surface" else None
			if water is not None:
				# <!-- custom: The upper Civilopedia water plane has a translucent decal over the opaque base texture.
				# Draw it after the fish so submerged geometry remains visible. (GPT-6.1-Sol) -->
				decal = next(prop.decal_0_texture for prop in node.properties if isinstance(prop, NifFormat.NiTexturingProperty) and prop.has_decal_0_texture)
				if decal.uv_set < len(data.uv_sets):
					uvs = np.array([(uv.u, uv.v) for uv in data.uv_sets[decal.uv_set]])
				if at is not None:
					uvs += texture_scroll(node, 6, at)
				overlays.append((points, uvs, triangles, water, True, 0.0))
			else:
				if overlays is not None and at is not None:
					uvs += texture_scroll(node, 0, at)
				meshes.append((points, uvs, triangles, texture, blend, threshold))
	if isinstance(node, NifFormat.NiNode):
		for child in node.children:
			if child is None:
				continue
			track = visibility.get(child.name)
			visible = bool_value(track, at) if track is not None else not (child.flags & 1)
			if visible:
				collect(child, folder, cache, args, meshes, worlds, visibility, at, overlays, opacity, glow, scrolling)


# <!-- custom: rasterize first drew opaque or alpha-blended triangles with affine texture coordinates.
# additive draws particles and effects that add light, perspective corrects texture coordinates for a Civilopedia scene's camera, and opacity_multiplier applies --water-opacity to the water overlay.
# The defaults keep earlier previews unchanged. (Claude code Opus 5.5) -->
# <!-- custom: The blends "glow" and "haze" are effect_surface's: unshaded and drawn over whatever is there, but only where something is, since past a lone plot they drew detached smudges on the backdrop, where in game a neighbouring plot would catch them.
# A third texture coordinate column is a haze card's vertex alpha. (Claude code Opus 5.5) -->
# <!-- custom: Added near, the camera's near distance: triangles crossing it are cut there, where they were skipped whole, as a Sevopedia scene's few large ground triangles left half the view black once the camera turned. (Claude code Opus 5.5) -->
def rasterize(meshes, project, width, height, shaded, color, depth, additive=False, perspective=False, opacity_multiplier=1, near=None):
	light = np.array([0.3, -0.5, 0.8])
	light /= np.linalg.norm(light)
	drawn = 0
	for points, uvs, triangles, texture, blend, threshold in meshes:
		if near is not None:
			points, uvs, triangles = clip_near(points, uvs, triangles, project(points)[2], near * 1.001)
		sx, sy, sz, usable = project(points)
		for i0, i1, i2 in triangles:
			if not (usable[i0] and usable[i1] and usable[i2]):
				continue
			x = np.array([sx[i0], sx[i1], sx[i2]])
			y = np.array([sy[i0], sy[i1], sy[i2]])
			area = (x[1] - x[0]) * (y[2] - y[0]) - (x[2] - x[0]) * (y[1] - y[0])
			if abs(area) < 1e-9:
				continue
			left, right = max(int(x.min()), 0), min(int(x.max()) + 1, width)
			top, bottom = max(int(y.min()), 0), min(int(y.max()) + 1, height)
			if left >= right or top >= bottom:
				continue
			gx, gy = np.meshgrid(np.arange(left, right) + 0.5, np.arange(top, bottom) + 0.5)
			w0 = ((x[1] - gx) * (y[2] - gy) - (x[2] - gx) * (y[1] - gy)) / area
			w1 = ((x[2] - gx) * (y[0] - gy) - (x[0] - gx) * (y[2] - gy)) / area
			w2 = 1.0 - w0 - w1
			inside = (w0 >= 0) & (w1 >= 0) & (w2 >= 0)
			if not inside.any():
				continue
			if perspective:
				# <!-- custom: Interpolate reciprocal depth and perspective-correct UVs when a shared scene camera projects planes behind a model. (GPT-6.1-Sol) -->
				w0, w1, w2 = w0 / sz[i0], w1 / sz[i1], w2 / sz[i2]
				z = np.divide(1, w0 + w1 + w2, out=np.zeros_like(w0), where=inside)
				w0, w1, w2 = w0 * z, w1 * z, w2 * z
			else:
				z = w0 * sz[i0] + w1 * sz[i1] + w2 * sz[i2]
			block = depth[top:bottom, left:right]
			visible = inside & np.isfinite(block) if blend in ("glow", "haze") else inside & (z < block)
			if not visible.any():
				continue
			shade = 1.0
			if shaded and blend not in ("glow", "haze"):
				normal = np.cross(points[i1] - points[i0], points[i2] - points[i0])
				norm = np.linalg.norm(normal)
				shade = 0.55 + 0.45 * abs(float(normal @ light) / norm) if norm else 1.0
			if texture is not None:
				u = (w0 * uvs[i0, 0] + w1 * uvs[i1, 0] + w2 * uvs[i2, 0]) % 1.0
				v = (w0 * uvs[i0, 1] + w1 * uvs[i1, 1] + w2 * uvs[i2, 1]) % 1.0
				h, w = texture.shape[:2]
				# <!-- custom: Blend the four nearest texels, as the game's filtering does; taking the nearest one made magnified textures blocky in large previews, while the game draws a leader larger with more of its texture's detail. (Claude code Opus 5.5) -->
				x, y = u * w - 0.5, v * h - 0.5
				x0, y0 = np.floor(x).astype(int), np.floor(y).astype(int)
				fx, fy = (x - x0)[:, :, None], (y - y0)[:, :, None]
				x0, x1, y0, y1 = x0 % w, (x0 + 1) % w, y0 % h, (y0 + 1) % h
				texel = (texture[y0, x0] * (1 - fx) + texture[y0, x1] * fx) * (1 - fy) + (texture[y1, x0] * (1 - fx) + texture[y1, x1] * fx) * fy
				visible &= texel[:, :, 3] > threshold
				rgb = texel[:, :, :3]
				opacity = texel[:, :, 3:4] if blend else np.ones(inside.shape + (1,))
				if uvs.shape[1] == 3:
					opacity = opacity * (w0 * uvs[i0, 2] + w1 * uvs[i1, 2] + w2 * uvs[i2, 2])[:, :, None]
			else:
				rgb = np.full(inside.shape + (3,), 0.6)
				opacity = np.ones(inside.shape + (1,))
			# <!-- custom: Blended texels mix with what is behind them; only mostly opaque ones hide later, farther triangles. (Claude code Opus 5.5) -->
			target = color[top:bottom, left:right]
			opacity *= opacity_multiplier
			add = additive or blend in ("add", "add-alpha", "glow")
			mixed = target * rgb if blend == "multiply" else rgb * shade * (1 if blend == "add" else opacity) + (target if add else target * (1.0 - opacity))
			target[visible] = mixed[visible]
			if not add and blend not in ("haze", "multiply", "water"):
				solid = visible & (opacity[:, :, 0] >= 0.5)
				block[solid] = z[solid]
			drawn += 1
	return drawn


def clip_near(points, uvs, triangles, distance, near):
	# <!-- custom: Cut each triangle crossing the near plane, adding the crossing points as vertices. (Claude code Opus 5.5) -->
	crossing = (distance[triangles] > near).sum(axis=1)
	mixed = np.flatnonzero((crossing > 0) & (crossing < 3))
	if not len(mixed):
		return points, uvs, triangles
	points, uvs = list(points), list(uvs)
	distance = list(distance)
	kept = list(triangles[crossing == 3])
	for corners in triangles[mixed]:
		polygon = []
		for k in range(3):
			a, b = int(corners[k]), int(corners[(k + 1) % 3])
			if distance[a] > near:
				polygon.append(a)
			if (distance[a] > near) != (distance[b] > near):
				f = (near - distance[a]) / (distance[b] - distance[a])
				points.append(points[a] + (points[b] - points[a]) * f)
				uvs.append(uvs[a] + (uvs[b] - uvs[a]) * f)
				distance.append(near)
				polygon.append(len(points) - 1)
		kept += [(polygon[0], polygon[k], polygon[k + 1]) for k in range(1, len(polygon) - 1)]
	return np.array(points), np.array(uvs), np.array(kept)


def particle_billboards(blocks, worlds, textures, at, right, up):
	# <!-- custom: Preview the religion scenes' constant-rate, additive box emitters with their original sprites.
	# Recreate recent births deterministically so rendering a single time does not depend on earlier frames. (GPT-6.1-Sol) -->
	cache = {}
	uvs = np.array(((0, 1), (1, 1), (1, 0), (0, 0)))
	triangles = ((0, 1, 2), (0, 2, 3))
	corners = np.array((-right - up, right - up, right + up, -right + up))
	for index, system in enumerate(blocks):
		if not isinstance(system, NifFormat.NiParticleSystem) or not system.world_space:
			continue
		controller = system.controller
		if not isinstance(controller, NifFormat.NiPSysEmitterCtlr) or not isinstance(controller.interpolator, NifFormat.NiFloatInterpolator) or controller.interpolator.data:
			continue
		rate = controller.interpolator.float_value
		if not 0 < rate <= 1000 or not any(isinstance(prop, NifFormat.NiAlphaProperty) and (prop.flags & 0x1ff) == 13 for prop in system.properties):
			continue
		emitter = next((m for m in system.modifiers if isinstance(m, NifFormat.NiPSysBoxEmitter) and id(m.emitter_object) in worlds), None)
		if emitter is None:
			continue
		texture = load_texture(system, textures, cache)
		if texture is None:
			continue
		world = worlds[id(emitter.emitter_object)]
		grow_fade = next((m for m in system.modifiers if isinstance(m, NifFormat.NiPSysGrowFadeModifier)), None)
		color_track = next((m.data.data.keys for m in system.modifiers if isinstance(m, NifFormat.NiPSysColorModifier) and m.data), ())
		visibility = controller.visibility_interpolator
		period = controller.stop_time - controller.start_time
		oldest = math.ceil((at - emitter.life_span - emitter.life_span_variation) * rate)
		for birth in range(oldest, math.floor(at * rate) + 1):
			born_at = birth / rate
			if period > 0 and (controller.flags & 6) == 0:
				born_at = controller.start_time + (born_at - controller.start_time) % period
			if visibility and not bool_value(visibility, born_at):
				continue
			rng = np.random.default_rng((index, birth % 2**32))
			age = at - birth / rate
			lifetime = emitter.life_span + rng.uniform(-1, 1) * emitter.life_span_variation
			if age >= lifetime:
				continue
			spread = rng.uniform(-0.5, 0.5, 3) * (emitter.width, emitter.height, emitter.depth)
			angle = emitter.declination + rng.uniform(-1, 1) * emitter.declination_variation
			azimuth = rng.uniform(0, 2 * math.pi)
			direction = np.array((math.sin(angle) * math.cos(azimuth), math.sin(angle) * math.sin(azimuth), math.cos(angle)))
			speed = emitter.speed + rng.uniform(-1, 1) * emitter.speed_variation
			center = (spread + direction * speed * age) @ world[:3, :3] + world[3, :3]
			radius = emitter.initial_radius
			if grow_fade:
				radius *= min(1, age / max(grow_fade.grow_time, 1e-9), (lifetime - age) / max(grow_fade.fade_time, 1e-9))
			if radius <= 0:
				continue
			opacity = sample(color_track, age / lifetime, lambda a, b, f: a.a * (1 - f) + b.a * f)
			if opacity is not None:
				opacity = opacity.a if hasattr(opacity, "a") else opacity
			sprite = texture.copy()
			sprite[:, :, 3] *= opacity if opacity is not None else 1
			yield center + radius * corners, uvs, triangles, sprite, True, 0.0


def scene_geometry(data, folder, args, at, transforms, visibility, overlays=None, opacity=None, cache=None, effect=None, scrolling=False):
	# <!-- custom: effect is a billboard effect's (facing, glow): the camera's right, up and toward rows, and its light as a fraction of the brightest key. (Claude code Opus 5.5) -->
	facing, glow = effect or (None, None)
	worlds = {}
	world_matrices(data.roots[0], np.identity(4), worlds, at, transforms, facing=facing)
	if at is not None and any(isinstance(block, NifFormat.NiLookAtInterpolator) for block in data.blocks):
		world_matrices(data.roots[0], np.identity(4), worlds, at, transforms, worlds.copy())
	meshes = []
	collect(data.roots[0], folder, {} if cache is None else cache, args, meshes, worlds, visibility, at, overlays, opacity, glow, scrolling)
	if not meshes:
		raise SystemExit("no drawable shapes")
	return worlds, meshes


# <!-- custom: render first took only the model, its time and its clip tracks.
# The added optional parameters carry what animated previews need: backdrop is a leader's separately drawn background, rest_geometry the resting pose that frames a moving subject, yaw_offset the camera turn for --orbit and --sway, environment a Civilopedia scene to place the model in, and opacity the clip's fade tracks.
# camera_source, a scene and its placed nodes, lends its camera to a scene without one: a vanilla-era leader background such as BtS's own Louis_XIV_BG.nif has none, and the leader's NIF holds it.
# Their defaults keep the plain still preview unchanged. (Claude code Opus 5.5) -->
def render(data, folder, args, at, use_camera, transforms, visibility, backdrop=None, rest_geometry=None, yaw_offset=0, environment=None, opacity=None, camera_source=None):
	worlds, meshes = scene_geometry(data, folder, args, at, transforms, visibility, opacity=opacity)
	if rest_geometry is not None:
		worlds, framing_meshes = rest_geometry
	else:
		framing_meshes = meshes
	camera_data = data
	if environment is not None:
		camera_data, (worlds, environment_meshes), overlays, animated_textures = environment
		if at is not None and animated_textures is not None:
			folder, cache = animated_textures
			overlays = []
			worlds, environment_meshes = scene_geometry(camera_data, folder, args, at, {}, {}, overlays, cache=cache)
		offset = np.array(args.model_offset)
		spin = math.radians(args.model_yaw or 0)
		turned = np.array([[math.cos(spin), math.sin(spin), 0], [-math.sin(spin), math.cos(spin), 0], [0, 0, 1]])
		meshes = environment_meshes + [((points @ turned) * args.model_scale + offset, *surface) for points, *surface in meshes]
	camera = next((b for b in camera_data.blocks if isinstance(b, NifFormat.NiCamera) and id(b) in worlds), None) if use_camera else None
	camera_worlds = worlds
	if camera is None and use_camera and camera_source is not None:
		camera_worlds = camera_source[1]
		camera = next((b for b in camera_source[0].blocks if isinstance(b, NifFormat.NiCamera) and id(b) in camera_worlds), None)
	if camera is None and (backdrop is not None or args.leader_background or environment is not None):
		raise SystemExit("the selected portrait or environment requires an embedded camera")
	if camera is not None:
		# <!-- custom: A Gamebryo camera looks along its local x axis, with y up and z right; its frustum, at distance 1, gives the view's edges, so the picture keeps its aspect (4:3 for the religion movies). (Claude code Opus 5.5) -->
		m = camera_worlds[id(camera)]
		forward, up, right = (m[k, :3] / np.linalg.norm(m[k, :3]) for k in range(3))
		position = m[3, :3]
		width = args.size * 2
		height = int(round(width * (camera.frustum_top - camera.frustum_bottom) / (camera.frustum_right - camera.frustum_left)))
		near = max(camera.frustum_near, 1e-3)
		left, right_edge = camera.frustum_left, camera.frustum_right
		top, bottom = camera.frustum_top, camera.frustum_bottom
		if backdrop is not None:
			# <!-- custom: Frame the resting bust over the separate backdrop so a gesture cannot pan or zoom the camera.
			# Leave space above the head and let the lower shoulders extend to the edge. (GPT-6.1-Sol) -->
			height, width = backdrop.shape[:2]
			points = np.vstack([mesh[0] for mesh in framing_meshes]) - position
			distances = points @ forward
			in_front = distances > near
			if not in_front.any():
				raise SystemExit("leaderhead geometry is behind its embedded camera")
			points, distances = points[in_front], distances[in_front]
			x = (points @ right) / distances
			y = (points @ up) / distances
			center = (x.min() + x.max()) / 2
			full_bust_span = max(np.ptp(x) / 1.08, np.ptp(y) * width / height)
			span = full_bust_span / 1.4
			left, right_edge = center - span / 2, center + span / 2
			vertical_span = span * height / width
			top = y.max() + 0.16 * vertical_span
			bottom = top - vertical_span
		if environment is not None and args.aspect:
			# <!-- custom: The Sevopedia's building pane is wider than the scene camera's 4:3, and the game keeps the camera's width, so the picture loses height. (Claude code Opus 5.5) -->
			middle, half = (top + bottom) / 2, (right_edge - left) / args.aspect / 2
			top, bottom = middle + half, middle - half
			height = int(round(width / args.aspect))
		if args.frame_shift_y:
			shift = args.frame_shift_y * (top - bottom)
			top += shift
			bottom += shift
		scene_pivot = np.array(args.scene_pivot if args.scene_pivot is not None else args.model_offset)
		if environment is not None and args.dolly not in (None, 1):
			position = scene_pivot + (position - scene_pivot) * args.dolly
		yaw_offset += args.turn
		view_yaw, view_pitch = (args.yaw or 0) + yaw_offset, args.pitch
		if args.scene_pivot is not None:
			position, forward, up, right = orbit_camera(position, forward, up, right, args.yaw or 0, args.pitch or 0, scene_pivot)
			view_yaw, view_pitch = yaw_offset, 0
		if (view_yaw or view_pitch) and (backdrop is not None or environment is not None):
			# <!-- custom: Rotate the camera around the subject at a fixed distance.
			# A leader's separately rendered backdrop stays fixed. (GPT-6.1-Sol) -->
			pivot = position + forward * np.median(distances) if backdrop is not None else np.array(args.model_offset)
			position, forward, up, right = orbit_camera(position, forward, up, right, view_yaw, view_pitch or 0, pivot)

		if environment is not None:
			# <!-- custom: Draw the scene's parts far to near: the coast scene lists its water before its sky, and the sky then covered the water's translucent texels, which write no depth, in white patches. (Claude code Opus 5.5) -->
			meshes[:len(environment_meshes)] = sorted(environment_meshes, key=lambda mesh: -np.linalg.norm(mesh[0] - position, axis=1).max())
			if args.scene_floor is not None:
				kept = []
				for index, mesh in enumerate(meshes):
					# <!-- custom: Flat parts stay: the water, which writes no depth so a shadow can lie on it, and a building's shadow quad, which the cut would remove. (Claude code Opus 5.5) -->
					if np.ptp(mesh[0][:, 2]) < 1:
						kept.append(mesh[:4] + ("water", mesh[5]) if index < len(environment_meshes) else mesh)
						continue
					points, uvs, triangles = clip_near(mesh[0], mesh[1], mesh[2], mesh[0][:, 2], args.scene_floor)
					above = (points[triangles][:, :, 2] >= args.scene_floor).all(axis=1)
					kept.append((points, uvs, triangles[above], *mesh[3:]))
				meshes = kept
				overlays = [overlay[:4] + ("water", overlay[5]) for overlay in overlays]
			if args.environment.stem.lower() == "ancientbattlefield":
				# <!-- custom: The land scene's sky came out darker than the game's: the top of the Champion's view had a median of 115 122 139 against 143 160 191 in screenshots of 2026-11-09.
				# Brightening its three sky layers by 1.3 gives 150 159 181.
				# Why the game's is brighter was not determined. (Claude code Opus 5.5) -->
				for k in range(len(environment_meshes)):
					if meshes[k][0][:, 2].max() > 700 and meshes[k][3] is not None:
						texture = meshes[k][3].copy()
						texture[..., :3] = np.clip(texture[..., :3] * 1.3, 0, 1)
						meshes[k] = meshes[k][:3] + (texture,) + meshes[k][4:]
			if args.scene_sky != 1:
				# <!-- custom: The coast scene's sky reaches far above its land; drawn at its texture's full opacity it was grey and white where the game's is mostly blue. (Claude code Opus 5.5) -->
				for k in range(len(environment_meshes)):
					if meshes[k][0][:, 2].max() > 100 and meshes[k][3] is not None:
						texture = meshes[k][3].copy()
						texture[..., 3] *= args.scene_sky
						meshes[k] = meshes[k][:3] + (texture,) + meshes[k][4:]

		def project(points):
			relative = points - position
			distance = relative @ forward
			usable = distance > near
			safe = np.where(usable, distance, 1.0)
			sx = ((relative @ right) / safe - left) / (right_edge - left) * width
			sy = (top - (relative @ up) / safe) / (top - bottom) * height
			return sx, sy, distance, usable
		color = backdrop.copy() if backdrop is not None else np.full((height, width, 3), args.clear_colour or (0, 0, 0), dtype=np.float32)
		depth = np.full((height, width), np.inf)
		# <!-- custom: Such scenes bake their lighting into textures, so they are drawn unshaded. (Claude code Opus 5.5) -->
		if environment is not None and args.scene_floor is not None:
			# <!-- custom: The water's translucent layer goes under the building: drawn last, it painted over the Drydock's shadow, which lies just above the water and writes no depth.
			# See README_Art_Tools.md. (Claude code Opus 5.5) -->
			count = len(environment_meshes)
			drawn = rasterize(meshes[:count], project, width, height, False, color, depth, perspective=True, near=near)
			drawn += rasterize(overlays, project, width, height, False, color, depth, perspective=True, opacity_multiplier=args.water_opacity)
			drawn += rasterize(meshes[count:], project, width, height, False, color, depth, perspective=True, near=near)
			return color, drawn, len(meshes)
		drawn = rasterize(meshes, project, width, height, False, color, depth, perspective=environment is not None, near=near if environment is not None else None)
		if environment is not None:
			drawn += rasterize(overlays, project, width, height, False, color, depth, perspective=True, opacity_multiplier=args.water_opacity)
		if args.particle_textures:
			particles = particle_billboards(data.blocks, worlds, args.particle_textures, at or 0.0, right, up)
			drawn += rasterize(particles, project, width, height, False, color, depth, additive=True)
		return color, drawn, len(meshes)
	return render_grid(meshes, framing_meshes, args, yaw_offset)


def grid_view(args, yaw_offset, plot):
	# <!-- custom: Orthographic camera: turn around the vertical axis (z is up in Civ4 models), then tilt down; screen x right, screen y up, depth into the screen. (Claude code Opus 5.5) -->
	yaw = math.radians((30 if args.yaw is None else args.yaw) + yaw_offset)
	# <!-- custom: A plot is seen from higher, as on the game's map; the model view's 25 degrees showed plots as thin slivers. (Claude code Opus 5.5) -->
	pitch = math.radians((40 if plot else 25) if args.pitch is None else args.pitch)
	turn = np.array([[math.cos(yaw), -math.sin(yaw), 0], [math.sin(yaw), math.cos(yaw), 0], [0, 0, 1]])
	tilt = np.array([[1, 0, 0], [0, math.sin(pitch), math.cos(pitch)], [0, math.cos(pitch), -math.sin(pitch)]])
	return tilt @ turn


def render_grid(meshes, framing_meshes, args, yaw_offset):
	# <!-- custom: render's orthographic view, split out so a plot preview can draw a ground without a model. (Claude code Opus 5.5) -->
	plot = getattr(args, "plot_ground", None)
	if plot is not None:
		# <!-- custom: On a plot, the model stands at its art define's fScale on the plot's centre, framed by the ground rather than by itself, without the floor grid. (Claude code Opus 5.5) -->
		ground_meshes, lift = plot
		meshes = ground_meshes + [(points * args.plot_model_scale + np.array([0, 0, lift]), *surface) for points, *surface in meshes]
		# <!-- custom: Effect cards do not frame the plot: Chronicles of Mankind's Sandstorm cards reach far past their plot and shrank it to a speck. (Claude code Opus 5.5) -->
		framing_meshes = [mesh for mesh in ground_meshes if mesh[4] not in ("glow", "haze")]
	view = grid_view(args, yaw_offset, plot is not None)
	model = np.vstack([mesh[0] for mesh in (framing_meshes if plot is not None else meshes)])
	flat = model @ view.T
	low, high = flat[:, :2].min(axis=0), flat[:, :2].max(axis=0)
	# <!-- custom: Draw at twice the size and shrink at the end, which smooths edges much as NifSkope's antialiasing does. (Claude code Opus 5.5) -->
	size = args.size * 2
	scale = size * 0.8 / max(high - low)
	offset = np.array([size / 2.0, size / 2.0]) - (low + high) / 2.0 * scale
	if args.orbit or args.sway or plot is not None:
		# <!-- custom: Use a yaw-independent radius for the orbit, so the view does not zoom as the model turns. (GPT-6.1-Sol) -->
		rest_points = np.vstack([mesh[0] for mesh in framing_meshes])
		center = (rest_points.min(axis=0) + rest_points.max(axis=0)) / 2
		radius = np.linalg.norm(rest_points - center, axis=1).max()
		scale = size * (0.95 if plot is not None else 0.8) / max(2 * radius, 1e-9)
		offset = size / 2.0 - (center @ view.T)[:2] * scale
	color = np.zeros((size, size, 3), dtype=np.float32)
	color[:] = (0.18, 0.18, 0.18)
	depth = np.full((size, size), np.inf)

	def project(points):
		screen = points @ view.T
		return screen[:, 0] * scale + offset[0], size - 1 - (screen[:, 1] * scale + offset[1]), screen[:, 2], np.ones(len(points), dtype=bool)
	if plot is not None:
		drawn = rasterize(meshes, project, size, size, True, color, depth)
		return color, drawn, len(meshes)
	# <!-- custom: A floor grid at the model's lowest point, like NifSkope's, about four cells across the model; the first draft mixed screen and model units and drew only a few stray lines. (Claude code Opus 5.5) -->
	floor_z = model[:, 2].min()
	extent = float(max(model[:, 0].max() - model[:, 0].min(), model[:, 1].max() - model[:, 1].min(), 1e-6))
	step = 10 ** math.floor(math.log10(extent / 4.0))
	step *= 5 if extent / step > 20 else 2 if extent / step > 8 else 1
	center = model[:, :2].mean(axis=0)
	reach = 3 * extent
	for k in np.arange(-reach, reach + step, step):
		for a, b in (((center[0] + k, center[1] - reach), (center[0] + k, center[1] + reach)), ((center[0] - reach, center[1] + k), (center[0] + reach, center[1] + k))):
			p = np.array([[a[0], a[1], floor_z], [b[0], b[1], floor_z]]) @ view.T
			x0, y0 = p[0, :2] * scale + offset
			x1, y1 = p[1, :2] * scale + offset
			n = int(max(abs(x1 - x0), abs(y1 - y0))) + 1
			xs = np.linspace(x0, x1, n).astype(int)
			ys = (size - 1 - np.linspace(y0, y1, n)).astype(int)
			inside = (xs >= 0) & (xs < size) & (ys >= 0) & (ys < size)
			color[ys[inside], xs[inside]] = (0.27, 0.27, 0.27)
	drawn = rasterize(meshes, project, size, size, True, color, depth)
	return color, drawn, len(meshes)


# <!-- custom: Moved out of main so a unit's default pose finds its idle the same way --clip does. (Claude code Opus 5.5) -->
def clip_entries(kfm, wanted):
	name = wanted.casefold()
	name = {"greet": "greeting", "agree": "affirmative", "disagree": "negative"}.get(name, name)
	entries = []
	for candidate in kfm.animations:
		stem = Path(candidate.kf_file_name.decode("latin-1").replace("\\", "/")).stem.casefold()
		# <!-- custom: Fall from Heaven's dragons have IdleA, IdleB and IdleC rather than Idle, so "idle" found only their fortify idles. (Claude code Opus 5.5) -->
		if stem == name or stem.endswith("_" + name) or (name == "idle" and stem.endswith("_md_idlea")):
			entries.append(candidate)
	# <!-- custom: "idle" matched HeavySpearman_MD_Idle, _MD_FortifyA_Idle and _MD_FortifyB_Idle, so the Immortal's idle needed its event number.
	# When several clips match, keep the one whose whole name after _MD_ is the requested name. (Claude code Opus 5.5) -->
	exact = [candidate for candidate in entries if Path(candidate.kf_file_name.decode("latin-1").replace("\\", "/")).stem.casefold().rpartition("_md_")[2] in (name, name + "a")]
	if len(entries) > 1 and len(exact) == 1:
		entries = exact
	return entries


def to_image(color):
	return Image.fromarray((np.clip(color, 0, 1) * 255).astype(np.uint8)).resize((color.shape[1] // 2, color.shape[0] // 2), Image.LANCZOS)


# <!-- custom: A unit's Sevopedia scene by domain, as the game's interface art names them, with the size its largest dimension is scaled to and a placement.
# The sizes come from the hand-fitted previews: the Immortal at 2.15x and the Houfnice at 2.2x both span about 340 units in the land scene, and the Bomber at 1x spans about 190 in the sky with its offset and pitch.
# Scene, size, offset, pitch, yaw and frame shift; land uses the Immortal's yaw and frame shift, without which a Warrior's head was cut off. (Claude code Opus 5.5) -->
DOMAIN_SCENES = {
	"DOMAIN_LAND": ("CIVILOPEDIA_ANCIENT_BATTLEGROUND", 340, (0, 0, 0), None, 12, 0.32),
	"DOMAIN_IMMOBILE": ("CIVILOPEDIA_ANCIENT_BATTLEGROUND", 340, (0, 0, 0), None, 12, 0.32),
	"DOMAIN_SEA": ("CIVILOPEDIA_WATER_ENVIRONMENT", 160, (0, -28, 0), None, 60, 0.1),
	"DOMAIN_AIR": ("CIVILOPEDIA_SKY_ENVIRONMENT", 190, (55, -70, -490), 20, None, 0),
}


# <!-- custom: A building's Sevopedia view: the land scene, or the coast scene for a building whose XML sets bWater; buildings have no domain, and no building is drawn in the sky.
# Fitted by eye to in-game screenshots (2026-11-09) of the expanded Sevopedia pane, with the camera's turn, pitch and distance matched against the coast's outline.
# art is what the art define's fScale times fInterfaceScale is multiplied by, as for a unit, up to a bounding sphere of reach, since the Drydock's fScale of 3 came out a third too large; it matched ten buildings within about 20%.
# pivot is the point the scene's camera turns around, and offset the model's place.
# sky keeps that fraction of the sky's opacity.
# aspect is the pane's shape.
# clear is the colour behind the coast scene, seen through its sky and water; without it the water was almost black and the sky grey.
# floor cuts away whatever of the scene or the building lies under the water: the cliff otherwise showed through it as orange islands, and in game a building's lower walls are hidden there, the Drydock's showing about 60% of its full height. (Claude code Opus 5.5) -->
BUILDING_SCENES = {
	False: {"scene": "CIVILOPEDIA_ANCIENT_BATTLEGROUND", "art": 1.5, "reach": 10000, "pivot": (0, 0, 0), "offset": (-335, -404, 0), "pitch": None, "yaw": 0, "shift": -0.1, "model_yaw": -12, "dolly": 1, "aspect": 1.68, "clear": (0, 0, 0), "floor": None, "sky": 1},
	True: {"scene": "CIVILOPEDIA_AMPHIB_ENVIRONMENT", "art": 0.9, "reach": 135, "pivot": (40, 40, 0), "offset": (245, 110, 5), "pitch": -17, "yaw": -50, "shift": -0.1, "model_yaw": -140, "dolly": 0.45, "aspect": 1.68, "clear": (60 / 255.0, 165 / 255.0, 225 / 255.0), "floor": 0, "sky": 0.45},
}


SEVOPEDIA_TURN_RATE = 2.6


def orbit_camera(position, forward, up, right, yaw_degrees, pitch_degrees, pivot):
	# <!-- custom: render's camera turn around a point, split out because a building's scene turns about one point before the view orbits the model at another. (Claude code Opus 5.5) -->
	yaw = math.radians(yaw_degrees) / 2
	pitch = -math.radians(pitch_degrees) / 2
	turn = quaternion_rows(math.cos(pitch), *(right * math.sin(pitch))) @ quaternion_rows(math.cos(yaw), 0, 0, math.sin(yaw))
	position = pivot + (position - pivot) @ turn
	forward, up, right = np.array((forward, up, right)) @ turn
	return position, forward, up, right


def write_video(images, out, fps, sound=None):
	# <!-- custom: A GIF has no sound, so a scene such as a religion's founding movie is written as H.264 video, with its MovieSound as AAC when given; ffmpeg encodes it, as for the Bink movies in movie_frames.py. (Claude code Opus 5.5) -->
	import subprocess
	import tempfile
	from movie_frames import find_tool
	with tempfile.TemporaryDirectory() as folder:
		for k, image in enumerate(images):
			# <!-- custom: H.264 in yuv420p needs even dimensions. (Claude code Opus 5.5) -->
			image.crop((0, 0, image.size[0] // 2 * 2, image.size[1] // 2 * 2)).save(os.path.join(folder, "%05d.png" % k))
		command = [find_tool("ffmpeg"), "-v", "error", "-y", "-framerate", "%f" % fps, "-i", os.path.join(folder, "%05d.png")]
		if sound:
			# <!-- custom: The Taoism scene animates for 5 s while its Taoist.mp3 lasts 10.8 s, and ending at the scene cut the music in half; hold the last frame until the sound ends. (Claude code Opus 5.5) -->
			command += ["-i", str(sound), "-vf", "tpad=stop_mode=clone:stop=-1", "-c:a", "aac", "-b:a", "192k", "-shortest"]
		subprocess.run(command + ["-c:v", "libx264", "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(out)], check=True)


# <!-- custom: Scaling every unit to one size hid what its art define says: futuremod's Warbot uses the Assault Mech's model at fScale 0.10 and fInterfaceScale 0.5 against 0.35 and 0.6, and its Sevopedia shows it about four times smaller, close to the 4.2 of fScale times fInterfaceScale.
# So a unit with an fScale is drawn at that product times a factor per scene, from the hand-fitted Immortal (2.15 at 0.44), Galley (0.40 at 0.102) and Bomber (1 at 0.5). (Claude code Opus 5.5) -->
DOMAIN_ART_SCALE = {"DOMAIN_LAND": 4.9, "DOMAIN_IMMOBILE": 4.9, "DOMAIN_SEA": 3.9, "DOMAIN_AIR": 2.0}


def resolve_mod_assets(args, parser):
	# <!-- custom: Replace art names with local copies so the rest of the preview reads ordinary files.
	# An ART_DEF_ type picks its files from the art XML: the KFM when a clip is chosen, its own model rather than the KFM's, a leaderhead's NoShaderNIF first as the Gandhi and Montezuma previews do, else a unit's SHADERNIF, since the BtS Warrior's plain NIF textures its body with TeamColor.bmp and drew only the club, and its BackgroundKFM unless --leader-background is given.
	# The game takes a unit's or leader's model from the art XML even when its KFM names another: History Rewritten's Alexander shares Zara Yaqob's KFM, which names Zara Yaqob.nif. (Claude code Opus 5.5) -->
	from civ4_assets import Civ4Assets, default_cache
	assets = Civ4Assets(args.mod)
	cache = args.cache or default_cache(args.mod)

	def local(value):
		if value is None or Path(value).exists():
			return value
		path, label = assets.stage(str(value), cache, args.refresh)
		print("%s: %s" % (label, value))
		return path

	name = str(args.asset)
	subject = name.upper()
	if subject.startswith(("BUILDING_", "UNIT_")) and not subject.startswith(("BUILDINGCLASS_", "UNITCLASS_", "UNITCOMBAT_")):
		# <!-- custom: A BUILDING_ or UNIT_ type stands for its art define, a unit's first when it has several. (Claude code Opus 5.5) -->
		assets.buildings() if subject.startswith("BUILDING_") else assets.units()
		name = assets.type_art.get(subject)
		if name is None:
			parser.error("%s has no art define in %s" % (subject, args.mod))
		args.asset = Path(name)
		subject = name
	wants_plot = bool(args.terrain or args.feature or args.plot or args.on_plot or subject.startswith(("TERRAIN_", "FEATURE_", "BONUS_", "IMPROVEMENT_")))
	if subject.startswith(("BONUS_", "IMPROVEMENT_")):
		# <!-- custom: A BONUS_ or IMPROVEMENT_ type stands for its art define, placed on a plot it may appear on. (Claude code Opus 5.5) -->
		from plot_scene import field
		kind = "Bonus" if subject.startswith("BONUS_") else "Improvement"
		info = assets.infos("Terrain", kind.lower() + "infos", kind + "Info").get(subject)
		if info is None:
			parser.error("%s is not %s of %s" % (name, "a bonus" if kind == "Bonus" else "an improvement", args.mod))
		name = field(info, "ArtDefineTag")
	args.plot_only = subject.startswith(("TERRAIN_", "FEATURE_"))
	if subject.startswith("RELIGION_"):
		# <!-- custom: A RELIGION_ type stands for its founding movie: the scene its XML names as MovieFile, seen through its own camera with its candle sprites, and its MovieSound for an MP4. (Claude code Opus 5.5) -->
		from plot_scene import field
		religion = assets.infos("GameInfo", "religioninfo", "ReligionInfo").get(subject)
		if religion is None:
			parser.error("%s is not a religion of %s" % (name, args.mod))
		name = field(religion, "MovieFile")
		args.scene_camera = True
		if args.sound is None and field(religion, "MovieSound"):
			args.sound = field(religion, "MovieSound")
		if args.particle_textures is None:
			args.particle_textures = assets.stage_matching("art/shared", "fx_fire*.dds", cache)
	args.asset = Path(name) if subject.startswith("RELIGION_") else args.asset
	fields = {}
	if name.upper().startswith("ART_DEF_"):
		fields = assets.art_defines(name).get(name.upper())
		if fields is None:
			parser.error("%s is not an art define of %s" % (name, args.mod))
		print("%s from %s" % (name.upper(), fields["_xml"]))
		# <!-- custom: Take the first of these that exists: CIV Gold names NoShaderNIF files it does not ship, such as Abu Bakr's frederick_the_great_noshader.nif and Akbar's "Zara Yaqob.nif.nif", while with shaders on the game draws the NIF, which is there. (Claude code Opus 5.5) -->
		model = next((fields[key] for key in ("NoShaderNIF", "SHADERNIF", "NIF") if fields.get(key) and assets.locate(fields[key])[0] is not None), None)
		# <!-- custom: A unit's still shows the first moment of its idle, as the Sevopedia plays it: the file's rest pose spread the arms of Ashes of Erebus's Champion, Adjunct and Centaur and of Realism Invictus's Dahomey Amazon, and sank Master of Mana's Shrine Maiden into the ground.
		# 16 Erebus units compared with screenshots on 2026-11-09 stood as in game.
		# --rest-pose keeps the file's pose. (Claude code Opus 5.5) -->
		if args.clip is None and not args.rest_pose and str(args.out or "").lower().endswith(".png") and not args.frames and not args.orbit and not args.sway and not wants_plot and name.upper() in assets.units() and fields.get("KFM") and assets.locate(fields["KFM"])[0] is not None and len(clip_entries(read_kfm(local(fields["KFM"])), "idle")) == 1:
			args.clip = "idle"
			args.frames = 1
			args.standing_still = True
		if args.clip is not None or (args.out is None and fields.get("KFM")):
			if not fields.get("KFM"):
				parser.error("%s has no KFM for --clip" % name)
			args.asset = fields["KFM"]
			if args.model is None and model and args.out:
				args.model = model
		elif model:
			args.asset = model
		else:
			parser.error("%s names no NIF or KFM that exists: %s" % (name, ", ".join(fields.get(key) for key in ("NoShaderNIF", "SHADERNIF", "NIF", "KFM") if fields.get(key)) or "none"))
		if args.leader_background is None and fields.get("BackgroundKFM") and args.out:
			args.leader_background = fields["BackgroundKFM"]
		unit = assets.units().get(name.upper())
		if unit is not None:
			print("%s: %s, %s, %s" % (unit["Unit"], unit["Domain"], unit["Combat"], unit["Era"] or "no era"))
			preset = DOMAIN_SCENES.get(unit["Domain"])
			if preset and not wants_plot and args.environment is None and not args.no_environment and args.out and not args.scene_camera and not str(args.asset).lower().endswith(".dds"):
				scene = assets.art_defines(preset[0]).get(preset[0])
				if scene is not None:
					args.environment = scene["Path"]
					args.auto_fit = preset
					if fields.get("fScale"):
						args.auto_scale = DOMAIN_ART_SCALE[unit["Domain"]] * float(fields["fScale"]) * float(fields.get("fInterfaceScale") or 1)
	building = assets.buildings().get(name.upper()) if name.upper().startswith("ART_DEF_") else None
	if building is not None:
		print("%s: %s, %s, %s" % (building["Building"], building["Kind"], "coast" if building["Water"] else "land", building["Era"] or "no era"))
		if not wants_plot and args.environment is None and not args.no_environment and args.out and not args.scene_camera:
			args.building_fit = BUILDING_SCENES[building["Water"]]
			args.art_scale = float(fields.get("fScale") or 1) * float(fields.get("fInterfaceScale") or 1)
			args.environment = assets.art_defines(args.building_fit["scene"])[args.building_fit["scene"]]["Path"]
	if wants_plot:
		# <!-- custom: Start from the terrain, feature and plot type the XML allows for the subject, and let --terrain, --feature and --plot force any other, even one the XML forbids, to see how it would look. (Claude code Opus 5.5) -->
		import plot_scene
		terrain, feature, plot = plot_scene.defaults(assets, subject)
		terrain = (args.terrain or terrain).upper()
		feature = None if (args.feature or "").lower() == "none" else (args.feature or feature)
		feature = feature.upper() if feature else None
		plot = args.plot or plot
		# <!-- custom: Kept as a function so a GIF of an effect can rebuild the plot at each moment. (Claude code Opus 5.5) -->
		def rebuild():
			ground, _, height = plot_scene.build(assets, cache, args, terrain, feature, plot)
			return ground, height
		args.plot_ground = rebuild()
		args.plot_rebuild = rebuild
		# <!-- custom: The game draws a lone unit SINGLE_UNIT_GFX_EXTRA_SCALE times its fScale (1.22 in SAS, 1.25 in BtS); without it the Llama Kamayuq stood about a third of a plot tall where in-game screenshots show it near half.
		# Bonuses and improvements keep their fScale. (Claude code Opus 5.5) -->
		args.plot_model_scale = float(fields.get("fScale") or 1) * (float(assets.define("SINGLE_UNIT_GFX_EXTRA_SCALE") or 1) if assets.units().get(name.upper()) else 1)
		print("plot: %s" % plot_scene.describe(terrain, feature, plot))
		if args.plot_only:
			return
	args.asset = Path(local(args.asset))
	if args.sound and not Path(args.sound).exists():
		# <!-- custom: --sound takes a file or, with --mod, a sound script such as AS2D_BUILD_TAOIST_MOVIE. (Claude code Opus 5.5) -->
		found = assets.sound(args.sound)
		if found is None:
			parser.error("no sound file for %s in %s" % (args.sound, args.mod))
		args.sound = local(found)
	for option in ("model", "kf", "leader_background", "environment"):
		value = getattr(args, option)
		if value is not None:
			setattr(args, option, Path(local(value)))


def main():
	parser = argparse.ArgumentParser(description="Draw a Civ4 .nif model as a PNG, textured and lit, over a floor grid, or a scene through its own camera.")
	parser.add_argument("asset", type=Path, help="NIF model, KFM animation set, or KF clip to inspect")
	parser.add_argument("out", nargs="?", help="PNG output (omit to inspect a KFM or KF)")
	parser.add_argument("--rest-pose", action="store_true", help="draw a unit's still in its file's rest pose rather than the first moment of its idle")
	parser.add_argument("--clip", help="KFM event code or clip name, such as pleased, greet, agree or disagree")
	parser.add_argument("--kf", type=Path, help="apply this KF to the input NIF")
	parser.add_argument("--model", type=Path, help="override the NIF referenced by a KFM, for example an FX variant")
	parser.add_argument("--pitch", type=float, help="camera pitch in degrees, relative to the embedded view when using a backdrop or environment")
	parser.add_argument("--yaw", type=float, help="starting camera rotation around the model, in degrees")
	camera_motion = parser.add_mutually_exclusive_group()
	camera_motion.add_argument("--orbit", type=float, default=0, help="degrees the camera turns over an animated GIF")
	camera_motion.add_argument("--sway", type=float, default=0, help="degrees the camera swings to either side of --yaw over one GIF loop")
	parser.add_argument("--size", type=int, default=512)
	parser.add_argument("--untextured", action="store_true", help="also draw untextured shapes, which are usually hidden helpers")
	parser.add_argument("--scene-camera", action="store_true", help="look through the file's own NiCamera, as religion-founding scenes do")
	parser.add_argument("--leader-background", type=Path, help="compose a leaderhead over the BackgroundKFM from its art XML")
	parser.add_argument("--environment", type=Path, help="place the model in a separate NIF scene, using the scene camera; with --mod a unit gets its domain's Sevopedia scene unless this is none")
	parser.add_argument("--model-offset", type=float, nargs=3, default=(0, 0, 0), metavar=("X", "Y", "Z"), help="translate the model within --environment")
	parser.add_argument("--model-scale", type=float, default=1, help="scale the model within --environment")
	parser.add_argument("--model-yaw", type=float, help="with --environment, turn the model about its vertical axis, in degrees, without moving the scene")
	parser.add_argument("--turn", type=float, default=0, help="with --environment, turn the view around the model, in degrees, as dragging the Sevopedia's picture does")
	parser.add_argument("--dolly", type=float, help="with --environment, the camera's distance from the model as a fraction of the scene's own")
	parser.add_argument("--aspect", type=float, help="with --environment, the picture's width over height; default: the scene camera's")
	parser.add_argument("--clear-colour", type=lambda text: tuple(int(part) / 255.0 for part in text.split(",")), metavar="R,G,B", help="with --environment, the colour behind the scene")
	parser.add_argument("--frame-shift-y", type=float, default=0, help="move the subject down by this fraction of the environment frame height")
	parser.add_argument("--water-opacity", type=float, default=1, help="multiplier for the Civilopedia water surface's texture alpha")
	parser.add_argument("--opacity-gain", type=float, default=1, help="multiplier for animated material opacity, such as splash ripples")
	parser.add_argument("--particle-textures", type=Path, help="preview scene-camera box emitters using DDS sprites from this folder")
	parser.add_argument("--frames", type=int, default=0, help="sample this many moments of the animation for a frame sheet or looping GIF")
	parser.add_argument("--speed", type=float, help="GIF playback multiplier, such as 0.5 for half speed (default: 1)")
	parser.add_argument("--cycles", type=int, default=1, help="animation repetitions within one GIF camera loop")
	parser.add_argument("--mod", help="find art as the game does for this mod (a folder under Beyond the Sword/Mods, or bts for the base game): the asset may then be an ART_DEF_ type or an Art/... path, as may --model, --kf, --leader-background and --environment")
	parser.add_argument("--team-color", type=lambda text: tuple(int(part) for part in text.split(",")), default=(70, 100, 170), metavar="R,G,B", help="the player colour shown on units painted through TeamColor.bmp (default: 70,100,170)")
	parser.add_argument("--terrain", help="with --mod, stand the subject on a plot of this terrain, such as TERRAIN_PLAINS; a TERRAIN_ or FEATURE_ asset draws the plot alone")
	parser.add_argument("--feature", help="with --mod, the plot's feature, such as FEATURE_FOREST, or none")
	parser.add_argument("--plot", choices=("flat", "hills", "peak"), help="with --mod, the plot type")
	parser.add_argument("--variety", type=int, help="with --feature, the feature art variety, such as 1 for the evergreen Forest")
	parser.add_argument("--latitude", type=int, help="with --feature, pick the art variety the game would for a plot at this latitude, such as 40 for the evergreen Forest")
	parser.add_argument("--river", action="store_true", help="with --mod, run a river along the plot's east edge; a feature that requires one, such as Flood Plains, gets it anyway")
	parser.add_argument("--glow", type=int, default=50, metavar="PERCENT", help="with --mod, a still of a glowing feature, such as Fallout: its light as a percentage of its brightest moment (default: 50); a GIF plays the file's own loop instead")
	parser.add_argument("--on-plot", action="store_true", help="with --mod, stand the subject on the terrain, feature and plot type its XML allows first")
	parser.add_argument("--sound", help="with an .mp4 output, its sound: a file, or with --mod a sound script such as AS2D_BUILD_TAOIST_MOVIE")
	parser.add_argument("--fps", type=float, help="frames per second of an .mp4 output (default: 24)")
	parser.add_argument("--refresh", action="store_true", help="with --mod, replace every cached copy; changed sources are replaced anyway")
	parser.add_argument("--cache", type=Path, help="with --mod, where to copy the art (default: per mod under the system temporary folder)")
	args = parser.parse_args()
	args.no_environment = args.environment is not None and str(args.environment).lower() == "none"
	args.auto_fit = None
	args.building_fit = None
	args.scene_floor = None
	args.scene_pivot = None
	args.scene_sky = 1
	args.standing_still = False
	args.art_scale = None
	args.auto_scale = None
	args.plot_ground = None
	args.plot_only = False
	args.plot_time = None
	args.plot_span = None
	if (args.terrain or args.feature or args.plot or args.on_plot or args.variety is not None or args.latitude is not None or args.river) and args.mod is None:
		parser.error("--terrain, --feature, --plot, --variety, --latitude, --river and --on-plot require --mod, to read the terrain art")
	if not 0 <= args.glow <= 100:
		parser.error("--glow must be between 0 and 100")
	if args.no_environment:
		args.environment = None
	if args.mod is not None:
		resolve_mod_assets(args, parser)
		if args.plot_only:
			# <!-- custom: A terrain or feature alone: draw the plot, turning with --orbit or --sway into a GIF. (Claude code Opus 5.5) -->
			if not args.out:
				parser.error("a plot preview needs an output path")
			is_gif = Path(args.out).suffix.lower() == ".gif"
			# <!-- custom: A GIF of an animated feature plays its own loop, as Fallout's 8 s or the Oasis water's 10 s, at real speed; otherwise a GIF only turns the camera. (Claude code Opus 5.5) -->
			span = args.plot_span if is_gif else None
			frames = (args.frames or 32 if span else max(args.frames, 1)) if is_gif else 1
			images = []
			for k in range(frames):
				if span:
					args.plot_time = span * k / frames
					args.plot_ground = args.plot_rebuild()
				images.append(to_image(render_grid([], [], args, args.orbit * k / frames + args.sway * math.sin(2 * math.pi * k / frames))[0]))
			delay = 1000 * span / frames / (args.speed or 1) if span else 1000 * (args.speed or 1) * 4 / frames
			images[0].save(args.out, save_all=frames > 1, append_images=images[1:], duration=int(delay) if frames > 1 else None, loop=0)
			print("wrote %s: a plot preview" % args.out)
			return
	elif args.cache is not None:
		parser.error("--cache requires --mod")
	if args.particle_textures and (not args.scene_camera or not args.particle_textures.is_dir()):
		parser.error("--particle-textures requires --scene-camera and an existing DDS folder")
	if args.asset.suffix.lower() == ".dds":
		# <!-- custom: Sengoku's and Master of Mana's leaders are flat .dds portraits named as their leaderhead NIF; show the picture. (Claude code Opus 5.5) -->
		if not args.out:
			parser.error("a .dds asset needs an output path")
		Image.open(args.asset).convert("RGB").save(args.out)
		print("wrote %s: a flat %s image" % (args.out, args.asset.name))
		return
	kind = args.asset.suffix.lower()
	# <!-- custom: An .mp4 output is an animation like a GIF, with the frame rate --fps and the sound --sound; the GIF rules below apply to both. (Claude code Opus 5.5) -->
	is_video = bool(args.out and Path(args.out).suffix.lower() == ".mp4")
	is_gif = bool(args.out and Path(args.out).suffix.lower() == ".gif") or is_video
	if (args.sound or args.fps) and not is_video:
		parser.error("--sound and --fps require MP4 output")
	moves_camera = bool(args.orbit or args.sway)
	if not all(map(math.isfinite, (args.orbit, args.sway))) or (moves_camera and (not is_gif or args.scene_camera)):
		parser.error("--orbit and --sway require a finite angle and GIF output without --scene-camera")
	if any(angle is not None and not math.isfinite(angle) for angle in (args.yaw, args.pitch)):
		parser.error("--yaw and --pitch must be finite")
	if args.environment and (not args.out or args.leader_background or args.scene_camera):
		parser.error("--environment requires output and supplies its own camera")
	if any(args.model_offset) and (not args.environment or not all(map(math.isfinite, args.model_offset))):
		parser.error("--model-offset requires --environment and finite coordinates")
	if not math.isfinite(args.model_scale) or args.model_scale <= 0 or (args.model_scale != 1 and not args.environment):
		parser.error("--model-scale requires --environment and a finite positive scale")
	if not math.isfinite(args.frame_shift_y) or (args.frame_shift_y and not args.environment):
		parser.error("--frame-shift-y requires --environment and a finite offset")
	if not 0 <= args.water_opacity <= 1 or (args.water_opacity != 1 and not args.environment):
		parser.error("--water-opacity requires --environment and a multiplier between 0 and 1")
	if not math.isfinite(args.opacity_gain) or args.opacity_gain < 0:
		parser.error("--opacity-gain must be finite and nonnegative")
	if args.cycles < 1 or (args.cycles != 1 and not is_gif):
		parser.error("--cycles requires GIF output and a positive repeat count")
	if args.speed is not None and not is_gif:
		parser.error("--speed requires GIF output")
	if args.speed is not None and (not math.isfinite(args.speed) or args.speed <= 0):
		parser.error("--speed must be finite and positive")
	if args.leader_background and not args.out:
		parser.error("--leader-background requires an output path")
	model, clip = args.asset, args.kf
	index = 0
	if args.clip is not None and kind != ".kfm":
		parser.error("--clip requires a KFM input")
	if args.model and (kind != ".kfm" or args.clip is None):
		parser.error("--model requires a KFM input and --clip")
	if args.kf and kind != ".nif":
		parser.error("--kf requires a NIF input")
	if kind == ".kfm":
		kfm = read_kfm(args.asset)
		print("Model: %s" % kfm.nif_file_name.decode("latin-1"))
		if args.clip is None and args.out is None:
			for entry in kfm.animations:
				print("  %d: %s (sequence %d)" % (entry.event_code, entry.kf_file_name.decode("latin-1"), entry.index))
			return
		if args.clip is None:
			parser.error("select a KFM event with --clip")
		try:
			code = int(args.clip)
			entries = [entry for entry in kfm.animations if entry.event_code == code]
		except ValueError:
			entries = clip_entries(kfm, args.clip)
		if len(entries) != 1:
			parser.error("clip %r must match one event in %s. List the KFM to see its events" % (args.clip, args.asset))
		entry = entries[0]
		clip = kfm_path(args.asset, entry.kf_file_name)
		index = entry.index
		if args.out:
			model = args.model or kfm_path(args.asset, kfm.nif_file_name)
	elif kind == ".kf" and args.out is None:
		clip = args.asset
	elif kind != ".nif":
		parser.error("expected a NIF or KFM for rendering, or a KF to inspect")
	sequence = read_clip(clip, index) if clip is not None else None
	if args.out is None:
		if sequence is None:
			parser.error("a NIF preview requires an output path")
		clip_tracks(sequence)
		return
	data = read_nif(model)
	folder = str(model.resolve().parent)
	transforms, visibility, opacity = {}, {}, {}
	if sequence is not None:
		nodes = {block.name for block in data.blocks if isinstance(block, NifFormat.NiAVObject)}
		transforms, visibility, opacity = clip_tracks(sequence, nodes)
		if not (transforms or visibility or opacity):
			raise SystemExit("no supported animation tracks matched the model")
	backdrop = rest_geometry = None
	if args.leader_background:
		background_kfm = read_kfm(args.leader_background)
		background = kfm_path(args.leader_background, background_kfm.nif_file_name)
		background_data = read_nif(background)
		lender = (data, scene_geometry(data, folder, args, None, {}, {})[0]) if not any(isinstance(block, NifFormat.NiCamera) for block in background_data.blocks) else None
		backdrop, _, _ = render(background_data, str(background.resolve().parent), args, None, True, {}, {}, camera_source=lender)
		if sequence is not None or args.frames > 0:
			rest_geometry = scene_geometry(data, folder, args, None, {}, {})
	environment = None
	if args.environment:
		scene = read_nif(args.environment)
		scene_folder = str(args.environment.resolve().parent)
		cache = {}
		overlays = []
		geometry = scene_geometry(scene, scene_folder, args, None, {}, {}, overlays, cache=cache)
		animated_textures = (scene_folder, cache) if any(isinstance(block, NifFormat.NiTextureTransformController) for block in scene.blocks) else None
		environment = scene, geometry, overlays, animated_textures
		if args.environment.stem.lower() == "waterenvironment" and args.building_fit is None:
			# <!-- custom: The water scene's sky, drawn at full opacity over black, came out white with black patches where the game's is pale blue with soft clouds (Master of Mana's Sea Serpent and MongooseMod's Mermaid, 2026-11-09).
			# The coast scene needed the same two settings. (Claude code Opus 5.5) -->
			args.scene_sky = 0.45
			args.clear_colour = args.clear_colour or (60 / 255.0, 165 / 255.0, 225 / 255.0)
		if args.auto_fit is not None:
			# <!-- custom: Scale a unit placed in its domain's scene by --mod so its largest dimension matches the scene's preset, unless the size or placement was given. (Claude code Opus 5.5) -->
			_, target, offset, pitch, yaw, shift = args.auto_fit
			points = np.vstack([mesh[0] for mesh in scene_geometry(data, folder, args, None, {}, {})[1]])
			if args.model_scale == 1:
				args.model_scale = args.auto_scale or target / max(np.ptp(points, axis=0))
			if not any(args.model_offset):
				args.model_offset = offset
			if args.pitch is None:
				args.pitch = pitch
			if args.yaw is None:
				args.yaw = yaw
			if not args.frame_shift_y:
				args.frame_shift_y = shift
			print("scene %s, model scale %.2f" % (args.environment.name, args.model_scale))
	if args.building_fit is not None:
		# <!-- custom: Each setting of a building's view unless it was given on the command line. (Claude code Opus 5.5) -->
		fit = args.building_fit
		points = np.vstack([mesh[0] for mesh in scene_geometry(data, folder, args, None, {}, {})[1]])
		if args.model_scale == 1:
			args.model_scale = min(fit["art"] * (args.art_scale or 1), fit["reach"] / np.linalg.norm(points, axis=1).max())
		args.model_offset = (fit["offset"] if not any(args.model_offset) else args.model_offset)
		args.pitch = fit["pitch"] if args.pitch is None else args.pitch
		args.yaw = fit["yaw"] if args.yaw is None else args.yaw
		args.frame_shift_y = args.frame_shift_y or fit["shift"]
		args.model_yaw = args.model_yaw if args.model_yaw is not None else fit["model_yaw"]
		args.dolly = args.dolly if args.dolly is not None else fit["dolly"]
		args.aspect = args.aspect or fit["aspect"]
		args.clear_colour = args.clear_colour or fit["clear"]
		args.scene_floor = fit["floor"]
		args.scene_pivot = fit["pivot"]
		args.scene_sky = fit["sky"]
		print("scene %s, model scale %.2f" % (args.environment.name, args.model_scale))
	use_camera = args.scene_camera or backdrop is not None or environment is not None
	if args.frames <= 0 and sequence is None and not is_video:
		if args.speed is not None or moves_camera or args.cycles != 1:
			parser.error("GIF playback options require an animation clip or scene animation with --frames")
		color, drawn, shapes = render(data, folder, args, None, use_camera, transforms, visibility, backdrop, environment=environment)
		to_image(color).save(args.out)
		print("wrote %s: %d triangles drawn from %d shape(s)" % (args.out, drawn, shapes))
		return
	span = (sequence.start_time, sequence.stop_time) if sequence is not None else animation_range(data.blocks)
	# <!-- custom: A still building turning in its scene has no keys of its own, so its GIF turns at the game's pace: timed screenshots of the Drydock and the Ziggurat (2026-11-09) measured 2.4 to 2.8 degrees per second while dragging, where a first 360 degrees in 4 s was about 35 times too fast.
	# --speed shortens it. (Claude code Opus 5.5) -->
	if span is None and moves_camera and environment is not None:
		span = (0.0, max(abs(args.orbit), 2 * math.pi * abs(args.sway)) / SEVOPEDIA_TURN_RATE)
	if span is None:
		raise SystemExit("no keyframed animation in this file")
	duration = span[1] - span[0]
	frames = args.frames if args.frames > 0 else round(duration * args.cycles / (args.speed or 1) * (args.fps or 24)) if is_video else 24 * args.cycles if is_gif else 4
	steps = frames if is_gif else max(frames - 1, 1)
	if is_gif:
		playback = duration * args.cycles / (args.speed or 1)
		if playback > 655.35 and not is_video:
			parser.error("GIF playback exceeds 655.35 seconds. Use a higher --speed")
		# <!-- custom: GIF delays are stored in centiseconds.
		# Round elapsed time before taking differences so rounding does not accumulate each frame. (GPT-6.1-Sol) -->
		delay = max(2, playback * 100 / frames)
		delays = [10 * (round((k + 1) * delay) - round(k * delay)) for k in range(frames)]
	times = [span[0] + duration * ((k * args.cycles) % steps) / steps for k in range(frames)] if is_gif else [span[0] + duration * k / steps for k in range(frames)]
	if moves_camera and not use_camera:
		rest_geometry = scene_geometry(data, folder, args, None, {}, {})
	yaw_offsets = [args.orbit * k / steps + args.sway * math.sin(2 * math.pi * k / steps) for k in range(frames)]
	images = [to_image(render(data, folder, args, at, use_camera, transforms, visibility, backdrop, rest_geometry, yaw, environment, opacity)[0]) for at, yaw in zip(times, yaw_offsets)]
	if is_video:
		write_video(images, args.out, frames / playback, args.sound)
		print("wrote %s: %d frames over %.2f s%s" % (args.out, frames, playback, ", with " + os.path.basename(args.sound) if args.sound else ""))
		return
	if is_gif:
		images[0].save(args.out, save_all=True, append_images=images[1:], duration=delays, loop=0)
		print("wrote %s: %d samples over %.2f s, %.2f s playback" % (args.out, frames, duration, sum(delays) / 1000))
		return
	if args.standing_still:
		images[0].save(args.out)
		print("wrote %s: the first moment of its idle" % args.out)
		return
	width, height = images[0].size
	sheet = Image.new("RGB", (width * len(images) + 8 * (len(images) - 1), height + 20), (30, 30, 30))
	draw = ImageDraw.Draw(sheet)
	for k, (image, at) in enumerate(zip(images, times)):
		sheet.paste(image, (k * (width + 8), 0))
		draw.text((k * (width + 8) + 4, height + 4), "t = %.2f s" % at, fill=(230, 230, 230))
	sheet.save(args.out)
	print("wrote %s: %d frames from %.2f to %.2f s" % (args.out, len(images), span[0], span[1]))


if __name__ == "__main__":
	main()
