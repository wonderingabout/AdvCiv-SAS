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
	return any(isinstance(prop, NifFormat.NiTexturingProperty) and prop.has_base_texture and prop.base_texture.source and os.path.basename(prop.base_texture.source.file_name.decode("latin-1").replace("\\", "/")).lower().startswith("teamcolor") for prop in shape.properties)


def load_texture(shape, folder, cache, slot="base_texture"):
	for prop in shape.properties:
		if isinstance(prop, NifFormat.NiTexturingProperty) and getattr(prop, "has_" + slot) and getattr(prop, slot).source:
			name = os.path.basename(getattr(prop, slot).source.file_name.decode("latin-1").replace("\\", "/"))
			if name not in cache:
				# <!-- custom: Civ4 finds a model's textures by name in its own folder, ignoring case, so look there the same way. (Claude code Opus 5.5) -->
				match = [entry for entry in os.listdir(folder) if entry.lower() == name.lower()]
				cache[name] = np.asarray(Image.open(os.path.join(folder, match[0])).convert("RGBA"), dtype=np.float32) / 255.0 if match else None
			return cache[name]
	return None


def world_matrices(node, parent, out, at, transforms, look_targets=None, bound_names=None):
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
				world_matrices(child, matrix, out, at, transforms, look_targets, bound_names)


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


def collect(node, folder, cache, args, meshes, worlds, visibility, at, overlays=None, opacity=None):
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
			threshold = alpha[0].threshold / 255.0 if alpha and alpha[0].flags & 0x200 else (0.5 if blend else -1.0)
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
				collect(child, folder, cache, args, meshes, worlds, visibility, at, overlays, opacity)


# <!-- custom: rasterize first drew opaque or alpha-blended triangles with affine texture coordinates.
# additive draws particles and effects that add light, perspective corrects texture coordinates for a Civilopedia scene's camera, and opacity_multiplier applies --water-opacity to the water overlay.
# The defaults keep earlier previews unchanged. (Claude code Opus 5.5) -->
def rasterize(meshes, project, width, height, shaded, color, depth, additive=False, perspective=False, opacity_multiplier=1):
	light = np.array([0.3, -0.5, 0.8])
	light /= np.linalg.norm(light)
	drawn = 0
	for points, uvs, triangles, texture, blend, threshold in meshes:
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
			visible = inside & (z < block)
			if not visible.any():
				continue
			shade = 1.0
			if shaded:
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
			else:
				rgb = np.full(inside.shape + (3,), 0.6)
				opacity = np.ones(inside.shape + (1,))
			# <!-- custom: Blended texels mix with what is behind them; only mostly opaque ones hide later, farther triangles. (Claude code Opus 5.5) -->
			target = color[top:bottom, left:right]
			opacity *= opacity_multiplier
			add = additive or blend in ("add", "add-alpha")
			mixed = rgb * shade * (1 if blend == "add" else opacity) + (target if add else target * (1.0 - opacity))
			target[visible] = mixed[visible]
			if not add:
				solid = visible & (opacity[:, :, 0] >= 0.5)
				block[solid] = z[solid]
			drawn += 1
	return drawn


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


def scene_geometry(data, folder, args, at, transforms, visibility, overlays=None, opacity=None, cache=None):
	worlds = {}
	world_matrices(data.roots[0], np.identity(4), worlds, at, transforms)
	if at is not None and any(isinstance(block, NifFormat.NiLookAtInterpolator) for block in data.blocks):
		world_matrices(data.roots[0], np.identity(4), worlds, at, transforms, worlds.copy())
	meshes = []
	collect(data.roots[0], folder, {} if cache is None else cache, args, meshes, worlds, visibility, at, overlays, opacity)
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
		meshes = environment_meshes + [(points * args.model_scale + offset, *surface) for points, *surface in meshes]
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
		if args.frame_shift_y:
			shift = args.frame_shift_y * (top - bottom)
			top += shift
			bottom += shift
		view_yaw = (args.yaw or 0) + yaw_offset
		if (view_yaw or args.pitch) and (backdrop is not None or environment is not None):
			yaw = math.radians(view_yaw) / 2
			pitch = -math.radians(args.pitch or 0) / 2
			turn = quaternion_rows(math.cos(pitch), *(right * math.sin(pitch))) @ quaternion_rows(math.cos(yaw), 0, 0, math.sin(yaw))
			# <!-- custom: Rotate the camera around the subject at a fixed distance.
			# A leader's separately rendered backdrop stays fixed. (GPT-6.1-Sol) -->
			pivot = position + forward * np.median(distances) if backdrop is not None else np.array(args.model_offset)
			position = pivot + (position - pivot) @ turn
			forward, up, right = np.array((forward, up, right)) @ turn

		def project(points):
			relative = points - position
			distance = relative @ forward
			usable = distance > near
			safe = np.where(usable, distance, 1.0)
			sx = ((relative @ right) / safe - left) / (right_edge - left) * width
			sy = (top - (relative @ up) / safe) / (top - bottom) * height
			return sx, sy, distance, usable
		color = backdrop.copy() if backdrop is not None else np.zeros((height, width, 3), dtype=np.float32)
		depth = np.full((height, width), np.inf)
		# <!-- custom: Such scenes bake their lighting into textures, so they are drawn unshaded. (Claude code Opus 5.5) -->
		drawn = rasterize(meshes, project, width, height, False, color, depth, perspective=environment is not None)
		if environment is not None:
			drawn += rasterize(overlays, project, width, height, False, color, depth, perspective=True, opacity_multiplier=args.water_opacity)
		if args.particle_textures:
			particles = particle_billboards(data.blocks, worlds, args.particle_textures, at or 0.0, right, up)
			drawn += rasterize(particles, project, width, height, False, color, depth, additive=True)
		return color, drawn, len(meshes)
	# <!-- custom: Orthographic camera: turn around the vertical axis (z is up in Civ4 models), then tilt down; screen x right, screen y up, depth into the screen. (Claude code Opus 5.5) -->
	yaw = math.radians((30 if args.yaw is None else args.yaw) + yaw_offset)
	pitch = math.radians(25 if args.pitch is None else args.pitch)
	turn = np.array([[math.cos(yaw), -math.sin(yaw), 0], [math.sin(yaw), math.cos(yaw), 0], [0, 0, 1]])
	tilt = np.array([[1, 0, 0], [0, math.sin(pitch), math.cos(pitch)], [0, math.cos(pitch), -math.sin(pitch)]])
	view = tilt @ turn
	model = np.vstack([mesh[0] for mesh in meshes])
	flat = model @ view.T
	low, high = flat[:, :2].min(axis=0), flat[:, :2].max(axis=0)
	# <!-- custom: Draw at twice the size and shrink at the end, which smooths edges much as NifSkope's antialiasing does. (Claude code Opus 5.5) -->
	size = args.size * 2
	scale = size * 0.8 / max(high - low)
	offset = np.array([size / 2.0, size / 2.0]) - (low + high) / 2.0 * scale
	if args.orbit or args.sway:
		# <!-- custom: Use a yaw-independent radius for the orbit, so the view does not zoom as the model turns. (GPT-6.1-Sol) -->
		rest_points = np.vstack([mesh[0] for mesh in framing_meshes])
		center = (rest_points.min(axis=0) + rest_points.max(axis=0)) / 2
		radius = np.linalg.norm(rest_points - center, axis=1).max()
		scale = size * 0.8 / max(2 * radius, 1e-9)
		offset = size / 2.0 - (center @ view.T)[:2] * scale
	color = np.zeros((size, size, 3), dtype=np.float32)
	color[:] = (0.18, 0.18, 0.18)
	depth = np.full((size, size), np.inf)
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

	def project(points):
		screen = points @ view.T
		return screen[:, 0] * scale + offset[0], size - 1 - (screen[:, 1] * scale + offset[1]), screen[:, 2], np.ones(len(points), dtype=bool)
	drawn = rasterize(meshes, project, size, size, True, color, depth)
	return color, drawn, len(meshes)


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
	if name.upper().startswith("ART_DEF_"):
		fields = assets.art_defines(name).get(name.upper())
		if fields is None:
			parser.error("%s is not an art define of %s" % (name, args.mod))
		print("%s from %s" % (name.upper(), fields["_xml"]))
		# <!-- custom: Take the first of these that exists: CIV Gold names NoShaderNIF files it does not ship, such as Abu Bakr's frederick_the_great_noshader.nif and Akbar's "Zara Yaqob.nif.nif", while with shaders on the game draws the NIF, which is there. (Claude code Opus 5.5) -->
		model = next((fields[key] for key in ("NoShaderNIF", "SHADERNIF", "NIF") if fields.get(key) and assets.locate(fields[key])[0] is not None), None)
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
			if preset and args.environment is None and not args.no_environment and args.out and not args.scene_camera and not str(args.asset).lower().endswith(".dds"):
				scene = assets.art_defines(preset[0]).get(preset[0])
				if scene is not None:
					args.environment = scene["Path"]
					args.auto_fit = preset
	args.asset = Path(local(args.asset))
	for option in ("model", "kf", "leader_background", "environment"):
		value = getattr(args, option)
		if value is not None:
			setattr(args, option, Path(local(value)))


def main():
	parser = argparse.ArgumentParser(description="Draw a Civ4 .nif model as a PNG, textured and lit, over a floor grid, or a scene through its own camera.")
	parser.add_argument("asset", type=Path, help="NIF model, KFM animation set, or KF clip to inspect")
	parser.add_argument("out", nargs="?", help="PNG output (omit to inspect a KFM or KF)")
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
	parser.add_argument("--frame-shift-y", type=float, default=0, help="move the subject down by this fraction of the environment frame height")
	parser.add_argument("--water-opacity", type=float, default=1, help="multiplier for the Civilopedia water surface's texture alpha")
	parser.add_argument("--opacity-gain", type=float, default=1, help="multiplier for animated material opacity, such as splash ripples")
	parser.add_argument("--particle-textures", type=Path, help="preview scene-camera box emitters using DDS sprites from this folder")
	parser.add_argument("--frames", type=int, default=0, help="sample this many moments of the animation for a frame sheet or looping GIF")
	parser.add_argument("--speed", type=float, help="GIF playback multiplier, such as 0.5 for half speed (default: 1)")
	parser.add_argument("--cycles", type=int, default=1, help="animation repetitions within one GIF camera loop")
	parser.add_argument("--mod", help="find art as the game does for this mod (a folder under Beyond the Sword/Mods, or bts for the base game): the asset may then be an ART_DEF_ type or an Art/... path, as may --model, --kf, --leader-background and --environment")
	parser.add_argument("--team-color", type=lambda text: tuple(int(part) for part in text.split(",")), default=(70, 100, 170), metavar="R,G,B", help="the player colour shown on units painted through TeamColor.bmp (default: 70,100,170)")
	parser.add_argument("--refresh", action="store_true", help="with --mod, replace every cached copy; changed sources are replaced anyway")
	parser.add_argument("--cache", type=Path, help="with --mod, where to copy the art (default: per mod under the system temporary folder)")
	args = parser.parse_args()
	args.no_environment = args.environment is not None and str(args.environment).lower() == "none"
	args.auto_fit = None
	if args.no_environment:
		args.environment = None
	if args.mod is not None:
		resolve_mod_assets(args, parser)
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
	is_gif = bool(args.out and Path(args.out).suffix.lower() == ".gif")
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
			name = args.clip.casefold()
			name = {"greet": "greeting", "agree": "affirmative", "disagree": "negative"}.get(name, name)
			entries = []
			for candidate in kfm.animations:
				stem = Path(candidate.kf_file_name.decode("latin-1").replace("\\", "/")).stem.casefold()
				if stem == name or stem.endswith("_" + name):
					entries.append(candidate)
			# <!-- custom: "idle" matched HeavySpearman_MD_Idle, _MD_FortifyA_Idle and _MD_FortifyB_Idle, so the Immortal's idle needed its event number.
			# When several clips match, keep the one whose whole name after _MD_ is the requested name. (Claude code Opus 5.5) -->
			exact = [candidate for candidate in entries if Path(candidate.kf_file_name.decode("latin-1").replace("\\", "/")).stem.casefold().rpartition("_md_")[2] == name]
			if len(entries) > 1 and len(exact) == 1:
				entries = exact
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
		if args.auto_fit is not None:
			# <!-- custom: Scale a unit placed in its domain's scene by --mod so its largest dimension matches the scene's preset, unless the size or placement was given. (Claude code Opus 5.5) -->
			_, target, offset, pitch, yaw, shift = args.auto_fit
			points = np.vstack([mesh[0] for mesh in scene_geometry(data, folder, args, None, {}, {})[1]])
			if args.model_scale == 1:
				args.model_scale = target / max(np.ptp(points, axis=0))
			if not any(args.model_offset):
				args.model_offset = offset
			if args.pitch is None:
				args.pitch = pitch
			if args.yaw is None:
				args.yaw = yaw
			if not args.frame_shift_y:
				args.frame_shift_y = shift
			print("scene %s, model scale %.2f" % (args.environment.name, args.model_scale))
	use_camera = args.scene_camera or backdrop is not None or environment is not None
	if args.frames <= 0 and sequence is None:
		if args.speed is not None or moves_camera or args.cycles != 1:
			parser.error("GIF playback options require an animation clip or scene animation with --frames")
		color, drawn, shapes = render(data, folder, args, None, use_camera, transforms, visibility, backdrop, environment=environment)
		to_image(color).save(args.out)
		print("wrote %s: %d triangles drawn from %d shape(s)" % (args.out, drawn, shapes))
		return
	span = (sequence.start_time, sequence.stop_time) if sequence is not None else animation_range(data.blocks)
	if span is None:
		raise SystemExit("no keyframed animation in this file")
	frames = args.frames if args.frames > 0 else 24 * args.cycles if is_gif else 4
	duration = span[1] - span[0]
	steps = frames if is_gif else max(frames - 1, 1)
	if is_gif:
		playback = duration * args.cycles / (args.speed or 1)
		if playback > 655.35:
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
	if is_gif:
		images[0].save(args.out, save_all=True, append_images=images[1:], duration=delays, loop=0)
		print("wrote %s: %d samples over %.2f s, %.2f s playback" % (args.out, frames, duration, sum(delays) / 1000))
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
