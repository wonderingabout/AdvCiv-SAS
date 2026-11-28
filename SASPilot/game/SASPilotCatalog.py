# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)
#
# <!-- custom: SASPilotCatalog: the game's definitions as data, read through its API rather than through the Sevopedia screen, which only SASPilotUI opens: 'info' gives an XML info's getters, 'types' the types of a kind and 'pedia' an entry's texts, with the Sevopedia's item kinds they share.
# Split from SASPilotCommands.py on 2026-11-28, as its first part moved out by topic; Codex (GPT-6.2-Sol) named it Catalog, as Info could be taken for the Info Screen or the live game state.
# SASPilotCommands.py loads it from beside itself, again whenever it changes, and adds its commands and help; 'saspilot' in this module's namespace is that command module. (Claude code Opus 5.5 + GPT-6.2-Sol) -->

# <!-- custom: CvScreenEnums holds PEDIA_ITEM_KINDS, the Sevopedia's item kinds that its link() reads too. (Claude code Opus 5.5) -->
from CvPythonExtensions import *
import CvScreenEnums

gc = CyGlobalContext()

# <!-- custom: The loader binds the command module before the first command. (Claude code Opus 5.5) -->
saspilot = None

# <!-- custom: This module's command help, which the loader adds to the command module's. (Claude code Opus 5.5) -->
_HELP = {}


_HELP["info"] = "An XML info by type, e.g. UNIT_WARRIOR: every zero-argument get/is getter of its info object. args: type."


def cmd_info(args):
	szType = args["type"]
	iType = saspilot._infoIndex(szType)
	getter = None
	# <!-- custom: The type's prefix is not enough to pick the getter (BUILDINGCLASS_ vs BUILDING_, SPECIALBUILDING_...), so try each getXInfo and keep the one whose entry has this type. (Claude code Fable 5.2) -->
	for name in dir(gc):
		if name.startswith("get") and name.endswith("Info") and not name.startswith("getNum"):
			# <!-- custom: Only tables whose count getter exists and covers the index: an index past a table's end could reach native code unchecked (Codex's review). (Claude code Opus 5.5 + GPT-6.1-Sol) -->
			szCount = "getNum" + name[3:] + "s"
			if not hasattr(gc, szCount) or iType >= getattr(gc, szCount)():
				continue
			try:
				info = getattr(gc, name)(iType)
				if info is not None and info.getType() == szType:
					getter = name
					break
			except Exception:
				pass
	if getter is None:
		raise ValueError("no gc.get*Info yields %s" % szType)
	result = describe(info)
	_nameInfoIndices(result)
	result["_index"] = iType
	result["_getter"] = getter
	return result


# <!-- custom: Getters that return another info's index, with that info's getter and count.
# Codex's review found that the first version, which went by the getter's ending (...Tech, ...Bonus), would read a quantity as an index, getHealthBonus being an amount and getFreeSpecialist a count in buildings, and could ask a table for an entry out of range; so only these names, whose meaning is the same in every BtS info that has them, and within range. (Claude code Opus 5.5 + GPT-6.1-Sol) -->
_INDEX_GETTERS = {
	"getPrereqAndTech": ("getTechInfo", "getNumTechInfos"),
	"getObsoleteTech": ("getTechInfo", "getNumTechInfos"),
	"getTechReveal": ("getTechInfo", "getNumTechInfos"),
	"getTechCityTrade": ("getTechInfo", "getNumTechInfos"),
	"getTechObsolete": ("getTechInfo", "getNumTechInfos"),
	"getPrereqAndBonus": ("getBonusInfo", "getNumBonusInfos"),
	"getPrereqReligion": ("getReligionInfo", "getNumReligionInfos"),
	"getStateReligion": ("getReligionInfo", "getNumReligionInfos"),
}


def _nameInfoIndices(result):
	# <!-- custom: 'info type=UNIT_CATAPULT' gave getPrereqAndTech 32, and finding that 32 is TECH_MATHEMATICS took a 'py' call (fog-on playthrough, turn 115, 2026-11-13). These getters also get <getter>Type with the type's name; -1 and out-of-range values stay as they are. (Claude code Opus 5.5) -->
	for name in result.keys():
		if name not in _INDEX_GETTERS:
			continue
		value = result[name]
		(szGetter, szCount) = _INDEX_GETTERS[name]
		if isinstance(value, int) and not isinstance(value, bool) and value >= 0 and value < getattr(gc, szCount)():
			result[name + "Type"] = getattr(gc, szGetter)(value).getType()


def describe(target):
	# <!-- custom: Calls every zero-argument method named get*, is*, can*, has* or count*; a method that needs arguments raises and is skipped.
	# Meant for info objects; also in the 'py' namespace for players, cities and units. (Claude code Fable 5.2) -->
	result = {}
	for name in dir(target):
		if name.startswith("get") or name.startswith("is") or name.startswith("can") or name.startswith("has") or name.startswith("count"):
			try:
				value = getattr(target, name)()
			except Exception:
				continue
			if value is None or isinstance(value, (int, long, float, str, unicode, bool)):
				result[name] = value
	return result


# <!-- custom: Static facts are in the XML files, which an agent can read directly; what the files lack is the effects text the DLL composes from them and from its own rules, as the Sevopedia shows it, so 'pedia' returns that (the user's point, 2026-11-13).
# One function per kind, with differing arguments. (Claude code Fable 5.2) -->
def _pediaEffects(szPrefix, iType):
	mgr = CyGameTextMgr()
	if szPrefix == "UNIT_":
		return mgr.getUnitHelp(iType, True, False, False, None)
	if szPrefix == "BUILDING_":
		return mgr.getBuildingHelp(iType, True, False, False, None)
	if szPrefix == "PROJECT_":
		return mgr.getProjectHelp(iType, True, None)
	if szPrefix == "TECH_":
		return mgr.getTechHelp(iType, True, False, False, False, -1)
	if szPrefix == "PROMOTION_":
		return mgr.getPromotionHelp(iType, True)
	if szPrefix == "BONUS_":
		return mgr.getBonusHelp(iType, True)
	if szPrefix == "IMPROVEMENT_":
		return mgr.getImprovementHelp(iType, True)
	if szPrefix == "TERRAIN_":
		return mgr.getTerrainHelp(iType, True)
	if szPrefix == "FEATURE_":
		return mgr.getFeatureHelp(iType, True)
	if szPrefix == "CIVIC_":
		return mgr.parseCivicInfo(iType, True, False, True)
	if szPrefix == "RELIGION_":
		return mgr.parseReligionInfo(iType, True)
	if szPrefix == "CORPORATION_":
		return mgr.parseCorporationInfo(iType, True)
	if szPrefix == "SPECIALIST_":
		return mgr.getSpecialistHelp(iType, True)
	return None


# <!-- custom: The kinds are CvScreenEnums.PEDIA_ITEM_KINDS, which the Sevopedia's link() reads too; this file kept its own copy until 2026-11-28, which lacked UNITCOMBAT_, CONCEPT_, VOTE_ and EVENTTRIGGER_.
# Each row is (prefix, count method, info method, category, landing categories, link-matched). See KI#1110.2. (Claude code Opus 5.5) -->
_PEDIA_KINDS = CvScreenEnums.PEDIA_ITEM_KINDS


def _pediaPrefixes():
	prefixes = []
	for kind in _PEDIA_KINDS:
		if kind[0] not in prefixes:
			prefixes.append(kind[0])
	return prefixes


def _pediaKindsOf(szPrefixOrType):
	kinds = [kind for kind in _PEDIA_KINDS if szPrefixOrType.startswith(kind[0])]
	if not kinds:
		raise ValueError("no Sevopedia kind for %s; kinds: %s" % (szPrefixOrType, " ".join(_pediaPrefixes())))
	return kinds


def _pediaKind(szType):
	# <!-- custom: The kind whose table holds szType, checked by the entry's own type: a BUILDINGCLASS_ or UNITCLASS_ type also starts with BUILDING or UNIT, and a CONCEPT_ type is in one of two concept tables. See KI#1110.2. (Claude code Fable 5.2 + Claude code Opus 5.5) -->
	kinds = _pediaKindsOf(szType)
	iType = saspilot._infoIndex(szType)
	for kind in kinds:
		if iType < getattr(gc, kind[1])() and getattr(gc, kind[2])(iType).getType() == szType:
			return kind
	raise ValueError("%s is not a %s type" % (szType, kinds[0][0]))


_HELP["types"] = "The XML types of one kind, to browse as the Sevopedia's lists: kind is a prefix such as UNIT_, BUILDING_, TECH_, CIVIC_, BONUS_, PROMOTION_; without it, the kinds. args: kind."


def cmd_types(args):
	if args.get("kind") is None:
		return _pediaPrefixes()
	# <!-- custom: CONCEPT_ lists both concept tables. See KI#1110.2. (Claude code Opus 5.5) -->
	types = []
	for kind in _pediaKindsOf(args["kind"]):
		types.extend([getattr(gc, kind[2])(i).getType() for i in range(getattr(gc, kind[1])())])
	return types


_HELP["pedia"] = "A type's Sevopedia entry as text: its name, the effects text the Sevopedia shows beside it, and its help and strategy texts, with markup removed. 'info' gives the same type's raw getters. args: type (e.g. UNIT_WARRIOR), long (1 to include the Civilopedia text, default 0)."


def cmd_pedia(args):
	szType = args["type"]
	kind = _pediaKind(szType)
	iType = saspilot._infoIndex(szType)
	info = getattr(gc, kind[2])(iType)
	result = {"type": szType, "name": info.getDescription(), "effects": None}
	szEffects = _pediaEffects(kind[0], iType)
	if szEffects is not None:
		result["effects"] = saspilot._plainText(szEffects)
	result["help"] = saspilot._plainText(info.getHelp())
	result["strategy"] = saspilot._plainText(info.getStrategy())
	if args.get("long"):
		result["civilopedia"] = saspilot._plainText(info.getCivilopedia())
	return result
