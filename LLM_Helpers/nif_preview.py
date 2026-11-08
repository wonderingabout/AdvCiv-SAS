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
	transforms, visibility, skipped = {}, {}, Counter()
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
		elif isinstance(track, NifFormat.NiTransformInterpolator):
			transforms[name] = track
			if track.data and track.data.rotation_type == 4:
				skipped["Euler rotation channels"] += 1
		else:
			skipped[type(track).__name__] += 1
	if nodes is not None:
		# <!-- custom: A clip can target a node absent from the chosen NIF variant.
		# Report missing targets so a partial pose is distinguishable from a fully matched clip. (GPT-6.1-Sol) -->
		missing = (transforms.keys() | visibility.keys()) - nodes
		if missing:
			print("  targets absent from model: %s" % ", ".join(name.decode("latin-1") for name in sorted(missing)))
		transforms = {name: track for name, track in transforms.items() if name in nodes}
		visibility = {name: track for name, track in visibility.items() if name in nodes}
	print("  %d transform tracks, %d visibility tracks" % (len(transforms), len(visibility)))
	if skipped:
		print("  unsupported by renderer: %s" % ", ".join("%s (%d)" % item for item in sorted(skipped.items())))
	return transforms, visibility


def transform_data(node):
	controller = node.controller
	while controller is not None:
		if isinstance(controller, NifFormat.NiTransformController) and controller.interpolator is not None and getattr(controller.interpolator, "data", None) is not None:
			return controller.interpolator.data
		controller = controller.next_controller
	return None


def local_matrix(node, at, interpolator):
	# <!-- custom: At a given time, a node with keyframes takes its translation, rotation and scale from them, interpolated linearly (slerp for rotations); the files' TBC and Bezier tangents are ignored, which is close enough for a still. (Claude code Opus 5.5 + GPT-6.1-Sol) -->
	data = None
	if interpolator is not None:
		data = interpolator.data
	elif at is not None:
		data = transform_data(node)
	if data is None and interpolator is None:
		return node_matrix(node)
	base = node_matrix(node)
	# <!-- custom: A KF can store a constant instead of keys.
	# Gamebryo uses -FLT_MAX for an unset interpolator channel. (GPT-6.1-Sol) -->
	translation = sample(list(data.translations.keys), at, lambda a, b, f: np.array([a.x, a.y, a.z]) * (1 - f) + np.array([b.x, b.y, b.z]) * f) if data else None
	if translation is None and interpolator is not None and interpolator.translation.x > -1e30:
		translation = interpolator.translation
	if translation is not None and not isinstance(translation, np.ndarray):
		translation = np.array([translation.x, translation.y, translation.z])
	rotation = None
	quaternion = None
	if data and data.rotation_type != 4 and len(data.quaternion_keys):
		quaternion = sample(list(data.quaternion_keys), at, slerp)
	elif interpolator is not None and interpolator.rotation.w > -1e30:
		quaternion = interpolator.rotation
	if quaternion is not None:
		if not isinstance(quaternion, np.ndarray):
			quaternion = np.array([quaternion.w, quaternion.x, quaternion.y, quaternion.z])
		rotation = quaternion_rows(*quaternion)
	scale = sample(list(data.scales.keys), at, lambda a, b, f: a * (1 - f) + b * f) if data else None
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


def load_texture(shape, folder, cache):
	for prop in shape.properties:
		if isinstance(prop, NifFormat.NiTexturingProperty) and prop.has_base_texture and prop.base_texture.source:
			name = os.path.basename(prop.base_texture.source.file_name.decode("latin-1").replace("\\", "/"))
			if name not in cache:
				# <!-- custom: Civ4 finds a model's textures by name in its own folder, ignoring case, so look there the same way. (Claude code Opus 5.5) -->
				match = [entry for entry in os.listdir(folder) if entry.lower() == name.lower()]
				cache[name] = np.asarray(Image.open(os.path.join(folder, match[0])).convert("RGBA"), dtype=np.float32) / 255.0 if match else None
			return cache[name]
	return None


def world_matrices(node, parent, out, at, transforms):
	out[id(node)] = local_matrix(node, at, transforms.get(node.name)) @ parent
	if isinstance(node, NifFormat.NiNode):
		for child in node.children:
			if child is not None:
				world_matrices(child, out[id(node)], out, at, transforms)


def skinned_points(node, vertices, worlds):
	# <!-- custom: A skinned mesh, such as a unit's body, is stored in its bind pose: each vertex is moved by its bones, weighted, from the skin's own transform through each bone's bind transform to that bone's place in the scene.
	# PyFFI's get_skin_deformation failed on the Persian Immortal ("cannot find a chain of NiAVObject blocks between BIP R Thigh and MD NonAccum"), so the bones' world matrices from the scene are used directly. (Claude code Opus 5.5 + GPT-6.1-Sol) -->
	skin = node.skin_instance
	overall = node_matrix(skin.data.skin_transform)
	homogeneous = np.hstack([vertices, np.ones((len(vertices), 1))])
	posed = np.zeros((len(vertices), 3))
	weight_sum = np.zeros(len(vertices))
	for bone, bone_data in zip(skin.bones, skin.data.bone_list):
		if bone is None or id(bone) not in worlds:
			continue
		matrix = overall @ node_matrix(bone_data.skin_transform) @ worlds[id(bone)]
		for weight in bone_data.vertex_weights:
			posed[weight.index] += weight.weight * (homogeneous[weight.index] @ matrix)[:3]
			weight_sum[weight.index] += weight.weight
	unweighted = weight_sum == 0
	posed[~unweighted] /= weight_sum[~unweighted][:, None]
	return posed, unweighted


def collect(node, folder, cache, untextured, meshes, worlds, visibility, at):
	world = worlds[id(node)]
	# <!-- custom: Triangle strips too: the Peat bonus model has one NiTriStrips part, which the first version skipped. (Claude code Opus 5.5 + GPT-6.1-Sol) -->
	if isinstance(node, (NifFormat.NiTriShape, NifFormat.NiTriStrips)) and node.data:
		texture = load_texture(node, folder, cache)
		data = node.data
		# <!-- custom: Untextured shapes are usually hidden helpers; the Peat bonus model has two grey "Sphere" shapes the game does not draw, which the first render showed as pyramids. (Claude code Opus 5.5 + GPT-6.1-Sol) -->
		triangles = list(data.get_triangles())
		if (texture is not None or untextured) and triangles:
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
			threshold = alpha[0].threshold / 255.0 if alpha and alpha[0].flags & 0x200 else (0.5 if blend else -1.0)
			meshes.append((points, uvs, triangles, texture, blend, threshold))
	if isinstance(node, NifFormat.NiNode):
		for child in node.children:
			if child is None:
				continue
			track = visibility.get(child.name)
			visible = bool_value(track, at) if track is not None else not (child.flags & 1)
			if visible:
				collect(child, folder, cache, untextured, meshes, worlds, visibility, at)


def rasterize(meshes, project, width, height, shaded, color, depth):
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
				texel = texture[np.minimum((v * h).astype(int), h - 1), np.minimum((u * w).astype(int), w - 1)]
				visible &= texel[:, :, 3] > threshold
				rgb = texel[:, :, :3]
				opacity = texel[:, :, 3:4] if blend else np.ones(inside.shape + (1,))
			else:
				rgb = np.full(inside.shape + (3,), 0.6)
				opacity = np.ones(inside.shape + (1,))
			# <!-- custom: Blended texels mix with what is behind them; only mostly opaque ones hide later, farther triangles. (Claude code Opus 5.5) -->
			target = color[top:bottom, left:right]
			mixed = rgb * shade * opacity + target * (1.0 - opacity)
			target[visible] = mixed[visible]
			solid = visible & (opacity[:, :, 0] >= 0.5)
			block[solid] = z[solid]
			drawn += 1
	return drawn


def render(data, folder, args, at, use_camera, transforms, visibility):
	worlds = {}
	world_matrices(data.roots[0], np.identity(4), worlds, at, transforms)
	meshes = []
	collect(data.roots[0], folder, {}, args.untextured, meshes, worlds, visibility, at)
	if not meshes:
		raise SystemExit("no drawable shapes")
	camera = next((b for b in data.blocks if isinstance(b, NifFormat.NiCamera) and id(b) in worlds), None) if use_camera else None
	if camera is not None:
		# <!-- custom: A Gamebryo camera looks along its local x axis, with y up and z right; its frustum, at distance 1, gives the view's edges, so the picture keeps its aspect (4:3 for the religion movies). (Claude code Opus 5.5) -->
		m = worlds[id(camera)]
		forward, up, right = (m[k, :3] / np.linalg.norm(m[k, :3]) for k in range(3))
		position = m[3, :3]
		width = args.size * 2
		height = int(round(width * (camera.frustum_top - camera.frustum_bottom) / (camera.frustum_right - camera.frustum_left)))
		near = max(camera.frustum_near, 1e-3)

		def project(points):
			relative = points - position
			distance = relative @ forward
			usable = distance > near
			safe = np.where(usable, distance, 1.0)
			sx = ((relative @ right) / safe - camera.frustum_left) / (camera.frustum_right - camera.frustum_left) * width
			sy = (camera.frustum_top - (relative @ up) / safe) / (camera.frustum_top - camera.frustum_bottom) * height
			return sx, sy, distance, usable
		color = np.zeros((height, width, 3), dtype=np.float32)
		depth = np.full((height, width), np.inf)
		# <!-- custom: Such scenes bake their lighting into textures, so they are drawn unshaded. (Claude code Opus 5.5) -->
		drawn = rasterize(meshes, project, width, height, False, color, depth)
		return color, drawn, len(meshes)
	# <!-- custom: Orthographic camera: turn around the vertical axis (z is up in Civ4 models), then tilt down; screen x right, screen y up, depth into the screen. (Claude code Opus 5.5) -->
	yaw, pitch = math.radians(args.yaw), math.radians(args.pitch)
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


def main():
	parser = argparse.ArgumentParser(description="Draw a Civ4 .nif model as a PNG, textured and lit, over a floor grid, or a scene through its own camera.")
	parser.add_argument("asset", type=Path, help="NIF model, KFM animation set, or KF clip to inspect")
	parser.add_argument("out", nargs="?", help="PNG output (omit to inspect a KFM or KF)")
	parser.add_argument("--clip", type=int, help="KFM event code to render")
	parser.add_argument("--kf", type=Path, help="apply this KF to the input NIF")
	parser.add_argument("--model", type=Path, help="override the NIF referenced by a KFM, for example an FX variant")
	parser.add_argument("--pitch", type=float, default=25, help="degrees the camera looks down")
	parser.add_argument("--yaw", type=float, default=30, help="degrees the camera turns around the model")
	parser.add_argument("--size", type=int, default=512)
	parser.add_argument("--untextured", action="store_true", help="also draw untextured shapes, which are usually hidden helpers")
	parser.add_argument("--scene-camera", action="store_true", help="look through the file's own NiCamera, as religion-founding scenes do")
	parser.add_argument("--frames", type=int, default=0, help="draw this many moments of the keyframed animation side by side")
	args = parser.parse_args()
	kind = args.asset.suffix.lower()
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
		entry = next((entry for entry in kfm.animations if entry.event_code == args.clip), None)
		if entry is None:
			parser.error("event %d is absent from %s" % (args.clip, args.asset))
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
	transforms, visibility = {}, {}
	if sequence is not None:
		nodes = {block.name for block in data.blocks if isinstance(block, NifFormat.NiAVObject)}
		transforms, visibility = clip_tracks(sequence, nodes)
		if not (transforms or visibility):
			raise SystemExit("no supported animation tracks matched the model")
	if args.frames <= 0 and sequence is None:
		color, drawn, shapes = render(data, folder, args, None, args.scene_camera, transforms, visibility)
		to_image(color).save(args.out)
		print("wrote %s: %d triangles drawn from %d shape(s)" % (args.out, drawn, shapes))
		return
	span = (sequence.start_time, sequence.stop_time) if sequence is not None else animation_range(data.blocks)
	if span is None:
		raise SystemExit("no keyframed animation in this file")
	frames = args.frames if args.frames > 0 else 4
	times = [span[0] + (span[1] - span[0]) * k / max(frames - 1, 1) for k in range(frames)]
	images = [to_image(render(data, folder, args, at, args.scene_camera, transforms, visibility)[0]) for at in times]
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
