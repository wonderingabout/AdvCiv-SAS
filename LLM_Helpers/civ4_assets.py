#!/usr/bin/env python3
# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)

# <!-- custom: The art tools first read only files on disk, so previewing another mod's leader meant finding its FPK, extracting the right folder and guessing which textures came from BtS.
# Mods mix their own loose art, their own FPKs and the base game's: Realism Invictus keeps most art in RI_381_Shared0-9 and its unit and structure FPKs, History Rewritten has three FPKs beside loose art, and Caveman2Cosmos splits its art XML into Modules.
# This looks a file up the way the game does, in the mod first and then BtS, Warlords and the original game, each as loose files before archives, and copies what a model needs into one cache folder that nif_preview.py can open.
# See README_Art_Tools.md. (Claude code Opus 5.5) -->

# <!-- custom: argparse parses the commands; fnmatch filters names; os and pathlib walk folders. (Claude code Opus 5.5) -->
import argparse
import fnmatch
import os
from pathlib import Path
# <!-- custom: re finds texture names inside a NIF; sys reports problems; tempfile places the cache; xml.etree reads the art XML; FpkArchive reads packed art. (Claude code Opus 5.5) -->
import re
import sys
import tempfile
import xml.etree.ElementTree as ElementTree

from fpk_tool import FpkArchive

# <!-- custom: This file sits in <Civ4>/Beyond the Sword/Mods/<mod>/LLM_Helpers, so the install is four folders up; CIV4_ROOT overrides it for another install. (Claude code Opus 5.5) -->
DEFAULT_ROOT = Path(os.environ.get("CIV4_ROOT") or Path(__file__).resolve().parents[4])
BASE_GAME = ("bts", "none", "")


def normalized(relative):
	# <!-- custom: Windows ignores trailing spaces and dots in a name, so Realism Invictus's "Art/Units/Cannon Ancient Chinese /..." and History Rewritten's "Amorite AT Infantry /..." load in the game.
	# Listing such a folder as written failed, and an FPK lookup missed it, so every path is compared in this form. (Claude code Opus 5.5) -->
	return "/".join(part.rstrip(" .") for part in relative.replace("\\", "/").strip("/").split("/")).lower()


def find_case_insensitive(base, relative):
	current = Path(base)
	for part in normalized(relative).split("/"):
		match = next((entry for entry in current.iterdir() if entry.name.lower().rstrip(" .") == part), None) if current.is_dir() else None
		if match is None:
			return None
		current = match
	return current


class Layer:
	# <!-- custom: One place the game reads art from: a loose Assets folder or one FPK.
	# Paths are relative to Assets, such as art/units/warrior/warrior.nif. (Claude code Opus 5.5) -->
	def __init__(self, label, assets=None, archive=None):
		self.label = label
		self.assets = assets
		self.archive = archive
		self.index = {normalized(key): key for key in archive.entries} if archive is not None else None

	def read(self, relative):
		if self.archive is not None:
			key = self.index.get(normalized(relative))
			return self.archive.read(key) if key is not None else None
		path = find_case_insensitive(self.assets, relative)
		return path.read_bytes() if path is not None and path.is_file() else None

	def stat(self, relative):
		# <!-- custom: Size and modification time of a file, an archive's entries taking the archive's own time, to tell whether a cached copy is stale. (Claude code Opus 5.5) -->
		if self.archive is not None:
			key = self.index.get(normalized(relative))
			return (self.archive.entries[key][1], self.archive.path.stat().st_mtime) if key is not None else None
		path = find_case_insensitive(self.assets, relative)
		return (path.stat().st_size, path.stat().st_mtime) if path is not None and path.is_file() else None

	def names_in(self, folder):
		if self.archive is not None:
			prefix = normalized(folder) + "/"
			return [key[len(prefix):] for key in self.index if key.startswith(prefix) and "/" not in key[len(prefix):]]
		path = find_case_insensitive(self.assets, folder)
		return [entry.name.lower() for entry in path.iterdir() if entry.is_file()] if path is not None and path.is_dir() else []


def lenient_records(data):
	# <!-- custom: Some mods' art XML is not well-formed, and a strict parser rejected the whole file.
	# Chronicles of Mankind closes a comment with "-- >", thecowwarrior's Variety Mod spells a Fallschirmjaeger NIF with a Latin-1 a-umlaut (byte 0xE4) in a file declared UTF-8, and a VIP module file has two top-level elements.
	# Read each <...ArtInfo> block's simple fields instead, ignoring comments. (Claude code Opus 5.5) -->
	text = re.sub(r"<!--.*?--\s*>", "", data.decode("latin-1"), flags=re.DOTALL)
	return [dict(re.findall(r"<(\w+)>([^<]*)</\1>", block)) for _, block in re.findall(r"<(\w*ArtInfo)>(.*?)</\1>", text, re.DOTALL)]


class Civ4Assets:
	def __init__(self, mod=None, root=DEFAULT_ROOT):
		self.root = Path(root)
		bts = self.root / "Beyond the Sword"
		self.mod_assets = None
		if mod is not None and mod.lower() not in BASE_GAME:
			mod_path = Path(mod) if Path(mod).is_absolute() else bts / "Mods" / mod
			if not (mod_path / "Assets").is_dir():
				raise SystemExit("no Assets folder in %s; name a folder under %s or give its absolute path" % (mod_path, bts / "Mods"))
			self.mod_assets = mod_path / "Assets"
		self.layers = []
		self.xml_roots = []
		self.art_records = None
		self.unit_records = None
		# <!-- custom: Loose files come before a folder's own FPKs, as when a mod ships an unpacked fix over its packed art.
		# Within one folder, FPKs are searched in name order; the game's order between two archives holding the same file was not verified. (Claude code Opus 5.5) -->
		for label, assets in (("mod", self.mod_assets), ("BtS", bts / "Assets"), ("Warlords", self.root / "Warlords" / "Assets"), ("Civ4", self.root / "Assets")):
			if assets is None or not assets.is_dir():
				continue
			self.layers.append(Layer("%s loose" % label, assets=assets))
			for fpk in sorted(assets.glob("*.[Ff][Pp][Kk]"), key=lambda path: path.name.lower()):
				# <!-- custom: The Sword of Islam ships an empty Pak1.FPK beside its real Pak0.FPK, and reading it stopped the whole lookup; skip an empty archive. (Claude code Opus 5.5) -->
				if fpk.stat().st_size == 0:
					print("skipped empty %s" % fpk, file=sys.stderr)
					continue
				self.layers.append(Layer("%s %s" % (label, fpk.name), archive=FpkArchive(fpk)))
			self.xml_roots.append((label, assets))
		# <!-- custom: A mod can name another installed mod's art from the Beyond the Sword folder: futuremod's Attila uses "Mods/FfH Age of Ice/Assets/Art/LeaderHeads/Charadon/brennus.kfm".
		# Such paths are found last, as loose files under that folder. (Claude code Opus 5.5) -->
		self.layers.append(Layer("BtS folder", assets=bts))

	def locate(self, relative):
		relative = relative.replace("\\", "/").lstrip("/")
		for layer in self.layers:
			data = layer.read(relative)
			if data is not None:
				return layer.label, data
		return None, None

	def xml_files(self, folder, name_part):
		# <!-- custom: The XML files of one kind, the mod's first; Caveman2Cosmos keeps its XML in Modules, so the mod's Modules folder is searched as well. (Claude code Opus 5.5) -->
		for label, assets in self.xml_roots:
			files = [path for path in (assets / "XML" / folder).glob("*.xml") if name_part in path.name.lower()] if (assets / "XML" / folder).is_dir() else []
			if label == "mod" and (assets / "Modules").is_dir():
				files += [path for path in (assets / "Modules").rglob("*.xml") if name_part in path.name.lower()]
			for path in sorted(files):
				yield label, path

	def art_defines(self, pattern="ART_DEF_*"):
		# <!-- custom: Collect every art define matching pattern, the mod's overriding the base game's of the same Type.
		# Interface art such as CIVILOPEDIA_WATER_ENVIRONMENT matches too, so the Sevopedia's scenes come from the same files. (Claude code Opus 5.5) -->
		if self.art_records is None:
			self.art_records = []
			for label, path in self.xml_files("Art", "artdefines"):
				try:
					records = [{child.tag.rpartition("}")[2]: (child.text or "").strip() for child in element} for element in ElementTree.parse(path).iter()]
				except ElementTree.ParseError as exc:
					print("read leniently %s: %s" % (path, exc), file=sys.stderr)
					records = lenient_records(path.read_bytes())
				self.art_records += [dict(fields, _xml=str(path), _layer=label) for fields in records if fields.get("Type")]
		found = {}
		for fields in self.art_records:
			art_type = fields["Type"]
			if fnmatch.fnmatch(art_type.upper(), pattern.upper()) and art_type not in found:
				found[art_type] = fields
		return found

	def units(self):
		# <!-- custom: Each unit art define's unit, with its domain, unit combat, prerequisite tech and that tech's era, to pick a Sevopedia scene and to filter galleries.
		# The first XML layer holding CIV4UnitInfos.xml or CIV4TechInfos.xml replaces the base game's, as a mod's full copy does; the mod's Modules add to it.
		# Read with patterns rather than an XML parser, which several mods' files fail. (Claude code Opus 5.5) -->
		if self.unit_records is not None:
			return self.unit_records
		eras, units = {}, {}
		for kind, block, store in (("techinfos", "TechInfo", eras), ("unitinfos", "UnitInfo", units)):
			chosen = None
			for label, path in self.xml_files("Technologies" if kind == "techinfos" else "Units", kind):
				if label != "mod" and chosen not in (None, label):
					continue
				if not path.name.lower().endswith("civ4" + kind + ".xml") and label != "mod":
					continue
				chosen = chosen or label
				text = re.sub(r"<!--.*?--\s*>", "", path.read_bytes().decode("latin-1"), flags=re.DOTALL)
				for body in re.findall(r"<%s>(.*?)</%s>" % (block, block), text, re.DOTALL):
					info_type = re.search(r"<Type>\s*([^<\s]+)", body)
					if info_type is None or info_type.group(1) in store:
						continue
					if kind == "techinfos":
						era = re.search(r"<Era>\s*([^<\s]+)", body)
						store[info_type.group(1)] = era.group(1) if era else None
					else:
						fields = {tag: (re.search(r"<%s>\s*([^<\s]+)" % tag, body) or [None, None])[1] for tag in ("Domain", "Combat", "PrereqTech")}
						fields["Unit"] = info_type.group(1)
						# <!-- custom: Realism Invictus lists a unit's techs as <PrereqTechs><TechType>...</TechType></PrereqTechs> instead of one <PrereqTech>, which left every RI unit without an era; take the first listed tech then. (Claude code Opus 5.5) -->
						listed = re.search(r"<PrereqTechs>\s*<TechType>\s*([^<\s]+)", body)
						if fields["PrereqTech"] in (None, "NONE") and listed:
							fields["PrereqTech"] = listed.group(1)
						for art in re.findall(r"<(?:Early|Middle|Late)ArtDefineTag>\s*([^<\s]+)", body):
							store.setdefault(art, fields)
		for fields in units.values():
			fields["Era"] = eras.get(fields["PrereqTech"])
		self.unit_records = units
		return units

	def stage(self, relative, cache, refresh=False):
		# <!-- custom: Copy the folder of relative from every layer into cache, the first layer holding a name winning, so a KFM finds its clips and a NIF its textures beside it.
		# Then copy each texture (.dds, or .tga as CIV Gold's leaders use) a staged NIF names from another folder, such as a shared BtS texture, beside it too, since nif_preview.py looks for textures by name in the model's folder. (Claude code Opus 5.5) -->
		relative = normalized(relative)
		folder = relative.rpartition("/")[0]
		target = Path(cache) / folder
		target.mkdir(parents=True, exist_ok=True)
		sources = {}
		for layer in self.layers:
			for name in layer.names_in(folder):
				if name not in sources:
					sources[name] = layer
		if relative.rpartition("/")[2].lower() not in sources:
			raise SystemExit("%s is not in %s" % (relative, ", ".join(layer.label for layer in self.layers)))
		# <!-- custom: Codex (GPT-6.1-Sol) pointed out that copying only absent files kept showing old art after a texture was edited or a loose override added, so a copy is replaced when its source differs in size or is newer; refresh replaces every copy. (Claude code Opus 5.5) -->
		for name, layer in sources.items():
			destination = target / name
			source = layer.stat(folder + "/" + name)
			if refresh or not destination.exists() or destination.stat().st_size != source[0] or source[1] > destination.stat().st_mtime:
				write_atomically(destination, layer.read(folder + "/" + name))
		for nif in [name for name in sources if name.endswith(".nif")]:
			for texture in set(re.findall(rb"[\w\\/ .()'-]+\.(?:dds|tga|bmp)", (target / nif).read_bytes(), re.IGNORECASE)):
				texture = texture.decode("latin-1").replace("\\", "/").strip()
				base = texture.rpartition("/")[2].lower()
				if base in sources:
					continue
				label, data = self.locate(texture[texture.lower().find("art/"):]) if "art/" in texture.lower() else (None, None)
				if data is None:
					# <!-- custom: A texture named without its folder, such as musket.dds in Realism Invictus's Apache Raiders, comes from the shared Art/Shared folder, here RI_381_Shared4.FPK. (Claude code Opus 5.5) -->
					label, data = self.locate("art/shared/" + base)
				if data is not None:
					if refresh or not (target / base).exists() or (target / base).read_bytes() != data:
						write_atomically(target / base, data)
				else:
					print("texture %s named by %s was not found" % (texture, nif), file=sys.stderr)
		return target / relative.rpartition("/")[2].lower(), sources[relative.rpartition("/")[2].lower()].label


def write_atomically(path, data):
	# <!-- custom: art_gallery.py runs several previews at once, which may copy the same scene into the cache together; write a temporary file and rename it so none reads a half-written copy. (Claude code Opus 5.5) -->
	temporary = path.with_name("%s.%d.part" % (path.name, os.getpid()))
	temporary.write_bytes(data)
	try:
		os.replace(temporary, path)
	except PermissionError:
		# <!-- custom: On Windows the rename fails while another preview has the finished copy open; that copy is complete, so keep it. (Claude code Opus 5.5) -->
		temporary.unlink()
		if not path.exists():
			raise


def default_cache(mod):
	# <!-- custom: An absolute cache under the system temporary folder, one per mod, so repeated previews reuse what was copied. (Claude code Opus 5.5) -->
	name = "bts" if mod is None or mod.lower() in BASE_GAME else Path(mod).name
	return Path(tempfile.gettempdir()) / "civ4_asset_cache" / re.sub(r"[^\w.-]+", "_", name)


def main():
	parser = argparse.ArgumentParser(description="Find Civ4 art the way the game does, in a mod first, then BtS, Warlords and the original game, loose files before FPKs.")
	parser.add_argument("--mod", help="mod folder name under Beyond the Sword/Mods, or an absolute path; bts searches the base game only")
	parser.add_argument("--root", type=Path, default=DEFAULT_ROOT, help="Civ4 install folder (default: found from this file, or CIV4_ROOT)")
	sub = parser.add_subparsers(dest="command", required=True)
	p = sub.add_parser("defines", help="list art defines, such as 'ART_DEF_LEADER_*', with their files")
	p.add_argument("pattern", nargs="?", default="ART_DEF_*")
	p = sub.add_parser("locate", help="say which layer supplies a file, such as Art/Units/Warrior/Warrior.nif")
	p.add_argument("path")
	p = sub.add_parser("stage", help="copy a file's folder, merged from all layers, into the cache and print its path")
	p.add_argument("path")
	p.add_argument("--cache", type=Path, help="cache folder (default: per mod under the system temporary folder)")
	p.add_argument("--refresh", action="store_true", help="replace every cached copy, not only those whose source changed")
	args = parser.parse_args()
	assets = Civ4Assets(args.mod, args.root)
	if args.command == "defines":
		defines = assets.art_defines(args.pattern)
		for art_type in sorted(defines):
			fields = defines[art_type]
			files = ", ".join("%s=%s" % (key, value) for key, value in fields.items() if not key.startswith("_") and value.lower().endswith((".nif", ".kfm", ".kf")))
			print("%s [%s]: %s" % (art_type, fields["_layer"], files or "-"))
		print("%d art define(s)" % len(defines))
	elif args.command == "locate":
		label, data = assets.locate(args.path)
		if data is None:
			raise SystemExit("%s was not found" % args.path)
		print("%s: %d bytes from %s" % (args.path, len(data), label))
	else:
		path, label = assets.stage(args.path, args.cache or default_cache(args.mod), args.refresh)
		print("%s (from %s)" % (path, label))


if __name__ == "__main__":
	sys.exit(main())
