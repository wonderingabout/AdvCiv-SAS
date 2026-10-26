# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)
# <!-- custom: Keep Python visual-resource ownership centralized in SASVisualUtils so direct GameFont/XML-info/art/color lookups and duplicate per-screen caches do not gradually reappear after this refactor. (ChatGPT-5.6-Sol) -->

# <!-- custom: Use only Python's standard tokenizer/regex/unittest helpers so the guard can inspect Python-2.4 gameplay source without importing Civ4 modules under CI's modern Python. (ChatGPT-5.6-Sol) -->
# <!-- custom: ast extracts only the production specialist resource class for focused behavioral fixtures without importing Civ4 or mocking the full UI. (GPT-6.1-Sol) -->
import ast
import io
from pathlib import Path
import re
import tokenize
import unittest


REPO_ROOT = Path(__file__).resolve().parents[4]
PYTHON_ROOT = REPO_ROOT / "Assets" / "Python"
CENTRAL_RESOURCE = PYTHON_ROOT / "SASVisualUtils.py"
CV_ENUMS = REPO_ROOT / "CvGameCoreDLL" / "CvEnums.h"
TRAIT_XML = REPO_ROOT / "Assets" / "XML" / "Civilizations" / "CIV4TraitInfos.xml"
UNIT_XML = REPO_ROOT / "Assets" / "XML" / "Units" / "CIV4UnitInfos.xml"
SPECIALIST_XML = REPO_ROOT / "Assets" / "XML" / "GameInfo" / "CIV4SpecialistInfos.xml"
INTERFACE_ART_XML = REPO_ROOT / "Assets" / "XML" / "Art" / "CIV4ArtDefines_Interface.xml"
RETIRED_MODULES = (
    PYTHON_ROOT / "SASUIResources.py",
    PYTHON_ROOT / "SASFontUtils.py",
    PYTHON_ROOT / "BUG" / "FontUtil.py",
    PYTHON_ROOT / "BUG" / "TraitUtil.py",
    PYTHON_ROOT / "BUG" / "GGUtil.py",
)


def _masked_source(path, mask_strings):
    source = path.read_text(encoding="latin-1")
    tokens = []
    for token in tokenize.generate_tokens(io.StringIO(source).readline):
        token_type, token_text, start, end, line = token
        if token_type == tokenize.COMMENT or (mask_strings and token_type == tokenize.STRING):
            token_text = ""
        tokens.append((token_type, token_text, start, end, line))
    return tokenize.untokenize(tokens)


def _gameplay_python_files():
    for path in sorted(PYTHON_ROOT.rglob("*.py")):
        if path != CENTRAL_RESOURCE:
            yield path


def _quoted_names(block):
    return set(re.findall(r'["\']([A-Z][A-Z0-9_]+)["\']', block))


# <!-- custom: Visual specification maps may be initialization-local; inspect their AST dictionary keys without requiring module scope or formatting. (GPT-6.1-Sol) -->
def _visual_mapping_keys(source, name):
    value = next(node.value for node in ast.walk(ast.parse(source)) if isinstance(node, ast.Assign) and any(isinstance(target, ast.Name) and target.id == name for target in node.targets))
    return set(key.value for key in value.keys)


def _tuple_block(source, name):
    match = re.search(r"^%s\s*=\s*\((.*?)^\)" % re.escape(name), source, re.M | re.S)
    if not match:
        raise AssertionError("Could not find tuple %s" % name)
    return match.group(1)


def _xml_types(path, prefix):
    source = path.read_text(encoding="latin-1")
    return set(re.findall(r"<Type>(%s[A-Z0-9_]+)</Type>" % re.escape(prefix), source))


class PythonVisualResourceTests(unittest.TestCase):
    # <!-- custom: Raw lookup and duplicated shared-art enforcement now belongs to the source-derived python_resource_api check and its fixtures.
    # Replacing these regex scans also lets its narrow, justified direct-read exception work consistently; unrelated .getChar() methods and one-off local art are not shared-cache bypasses. (ChatGPT-5.6-Sol + GPT-6.1-Sol) -->
    def test_display_code_uses_cached_chars_not_ordinals(self):
        # <!-- custom: UI rendering should consume the cached Unicode glyph itself.
        # Keep ordinal() for the small set of integer contracts (translator/XML %c arguments, offset/index arithmetic, diagnostics), not for immediately formatting a glyph back through Python %c. (ChatGPT-5.6-Sol) -->
        failures = []
        display_pattern = re.compile(r"%c[^\r\n]*SASVisuals\.|SASVisuals\.[^\r\n]*%c")
        for path in _gameplay_python_files():
            source = _masked_source(path, False)
            if display_pattern.search(source):
                failures.append("%s: SASVisuals display glyph formatted through %%c instead of cached char" % path.relative_to(REPO_ROOT))
        self.assertEqual(failures, [], "\n".join(failures))

        # <!-- custom: Keep all remaining ordinal consumers intentionally narrow and reviewable; new display code should use char()/named *_CHAR attributes instead. (ChatGPT-5.6-Sol) -->
        allowed = {
            "Contrib/GameFontDisplay.py": re.compile(r"\biMax\s*=.*SASVisuals\.Font\.ordinal\(FontSymbols\.HAPPY_CHAR\)"),
            "Screens/CvMainInterface.py": re.compile(r"(?:localText\.getText|\bcAtt\s*=).*SASVisuals\.(?:Font|Commerce)\.ordinal\("),
            "EntryPoints/CvRandomEventInterface.py": re.compile(r"localText\.getText.*SASVisuals\.Religion\.ordinal\("),
        }
        failures = []
        ordinal_pattern = re.compile(r"SASVisuals\.[A-Za-z]+\.ordinal\(")
        for path in _gameplay_python_files():
            rel = str(path.relative_to(PYTHON_ROOT)).replace("\\", "/")
            source = _masked_source(path, True)
            for line_number, line in enumerate(source.splitlines(), 1):
                if not ordinal_pattern.search(line):
                    continue
                allow_pattern = allowed.get(rel)
                if allow_pattern is None or not allow_pattern.search(line):
                    failures.append("%s:%d: ordinal() is not an approved integer-only visual contract" % (path.relative_to(REPO_ROOT), line_number))
        self.assertEqual(failures, [], "\n".join(failures))


    def test_old_per_screen_visual_char_caches_stay_retired(self):
        # <!-- custom: These were deterministic arrays rebuilt by individual screens despite the same tuples/ordinals already being owned by SASVisualUtils.
        # Keep the concrete legacy cache names retired. (ChatGPT-5.6-Sol) -->
        pattern = re.compile(r"\bself\.(?:COMMERCE_CHARS|YIELD_CHARS)\b")
        failures = []
        for path in _gameplay_python_files():
            if pattern.search(_masked_source(path, False)):
                failures.append(str(path.relative_to(REPO_ROOT)))
        self.assertEqual(failures, [], "\n".join(failures))

    def test_sas_visual_utils_is_imported_through_sasvisuals_alias(self):
        # <!-- custom: Generic collection names such as Yield/Color/Trait remain safely namespaced at call sites, avoiding collisions with inherited modules/globals. (ChatGPT-5.6-Sol) -->
        bad_pattern = re.compile(r"(?:^|\n)\s*(?:from\s+SASVisualUtils\s+import|import\s+SASVisualUtils(?!\s+as\s+SASVisuals\b))")
        failures = []
        for path in _gameplay_python_files():
            if bad_pattern.search(_masked_source(path, True)):
                failures.append(str(path.relative_to(REPO_ROOT)))
        self.assertEqual(failures, [], "\n".join(failures))

    def test_retired_visual_helper_modules_stay_retired(self):
        for path in RETIRED_MODULES:
            self.assertFalse(path.exists(), str(path.relative_to(REPO_ROOT)))
        pattern = re.compile(r"(?:^|\n)\s*(?:from\s+(?:SASUIResources|SASFontUtils|FontUtil|TraitUtil|GGUtil)\s+import|import\s+(?:SASUIResources|SASFontUtils|FontUtil|TraitUtil|GGUtil)\b)")
        failures = []
        for path in _gameplay_python_files():
            if pattern.search(_masked_source(path, True)):
                failures.append(str(path.relative_to(REPO_ROOT)))
        self.assertEqual(failures, [], "\n".join(failures))

    def test_builtin_font_symbol_inventory_matches_dll_enum(self):
        source = CENTRAL_RESOURCE.read_text(encoding="latin-1")
        central = _quoted_names(_tuple_block(source, "BUILTIN_FONT_SYMBOL_NAMES"))
        enums = CV_ENUMS.read_text(encoding="latin-1")
        block = re.search(r"enum\s+FontSymbols\s*\{(.*?)\};", enums, re.S).group(1)
        block = re.sub(r"/\*.*?\*/|//[^\r\n]*", "", block, flags=re.S)
        dll = set(re.findall(r"^\s*([A-Z][A-Z0-9_]*_CHAR)\b", block, re.M))
        self.assertEqual(central, dll)

    def test_trait_visual_map_matches_live_trait_xml(self):
        source = CENTRAL_RESOURCE.read_text(encoding="latin-1")
        central = _visual_mapping_keys(source, "SAS_TRAIT_VISUAL_SPECS")
        self.assertEqual(central, _xml_types(TRAIT_XML, "TRAIT_"))

    def test_great_person_visual_records_match_live_unit_xml(self):
        # <!-- custom: Temporary initialization records own each GP identity and its glyph/color metadata; runtime collections are derived rather than copied.
        # Read the source table structurally so reordered records or formatting changes do not require another duplicated membership list. (GPT-6.1-Sol) -->
        source = CENTRAL_RESOURCE.read_text(encoding="latin-1")
        tree = ast.parse(source)
        records = next(node.value for node in ast.walk(tree) if isinstance(node, ast.Assign) and any(isinstance(target, ast.Name) and target.id == "SAS_GREAT_PERSON_VISUAL_SPECS" for target in node.targets))
        names = [record.elts[0].value for record in records.elts]
        self.assertEqual(len(names), len(set(names)), "duplicate Great Person visual identity")
        self.assertEqual(set(names), _xml_types(UNIT_XML, "UNIT_GREAT_"))
        # <!-- custom: Legacy GP_* constant names define semantic index order independently of XML membership; a set-only check misses swapped roles. (ChatGPT-5.6-Sol + GPT-6.1-Sol) -->
        legacy = ast.parse((PYTHON_ROOT / "BUG" / "GPUtil.py").read_text(encoding="latin-1"))
        roles = next([target.id for target in node.targets[0].elts] for node in ast.walk(legacy) if isinstance(node, ast.Assign) and isinstance(node.targets[0], ast.Tuple) and node.targets[0].elts and all(isinstance(target, ast.Name) and target.id.startswith("GP_GREAT_") for target in node.targets[0].elts))
        self.assertEqual(names, [role.replace("GP_", "UNIT_", 1) for role in roles], "visual record order must preserve legacy role identities")

    def test_gp_construction_records_are_temporary_and_results_cached(self):
        # <!-- custom: Exercise the actual local GP specification and cache initialization without importing Civ4.
        # Repeated getters must reuse resolved data, and construction metadata must not survive as a module/object attribute. (GPT-6.1-Sol) -->
        source = CENTRAL_RESOURCE.read_text(encoding="latin-1")
        definition = next(node for node in ast.parse(source).body if isinstance(node, ast.ClassDef) and node.name == "_GreatPeopleResources")

        class Resource:
            def __init__(self):
                self.reads = []

            def __getattr__(self, name):
                return name

            def char(self, value):
                self.reads.append(("char", value))
                return ("char", value)

            def color(self, value):
                self.reads.append(("color", value))
                return ("color", value)

            def get(self, value):
                self.reads.append(("fixed-color", value))
                return ("fixed-color", value)

        namespace = dict((name, Resource()) for name in ("Font", "Color", "Yield", "Commerce", "FontSymbols", "YieldTypes", "CommerceTypes"))
        names = sorted(_xml_types(UNIT_XML, "UNIT_GREAT_"))
        ids = dict((name, 31 + index * 3) for index, name in enumerate(names))
        namespace["getInfoTypeOrFail"] = lambda name: ids[name]
        exec(compile(ast.Module(body=[definition], type_ignores=[]), str(CENTRAL_RESOURCE), "exec"), namespace)
        cache = namespace["_GreatPeopleResources"]()
        resolved_names = cache.unitTypeNames()
        self.assertEqual(set(resolved_names), set(names))
        self.assertEqual(cache.unitTypes(), tuple(ids[name] for name in resolved_names))
        reads = sum(len(resource.reads) for resource in namespace.values() if isinstance(resource, Resource))
        for index, unit in enumerate(cache.unitTypes()):
            self.assertTrue(cache.hasUnitIcon(unit))
            self.assertEqual(cache.getUnitIcon(unit), cache.unitIcons()[index])
            self.assertEqual(cache.getUnitColor(unit), cache.unitColors()[index])
        cache.init()
        self.assertEqual(sum(len(resource.reads) for resource in namespace.values() if isinstance(resource, Resource)), reads)
        self.assertNotIn("SAS_GREAT_PERSON_VISUAL_SPECS", namespace)
        self.assertNotIn("SAS_GREAT_PERSON_VISUAL_SPECS", vars(cache))
        self.assertFalse(cache.hasUnitIcon(-1))
        self.assertEqual(cache.getUnitIcon(-1), cache.getDefaultIcon())
        self.assertFalse(cache.hasUnitIcon(-1))
        with self.assertRaises(KeyError):
            cache.getUnitColor(-1)

    def test_specialist_visual_map_matches_live_specialist_xml(self):
        source = CENTRAL_RESOURCE.read_text(encoding="latin-1")
        central = _visual_mapping_keys(source, "SAS_SPECIALIST_VISUAL_SPECS")
        self.assertEqual(central, _xml_types(SPECIALIST_XML, "SPECIALIST_"))

    def test_fixed_sas_interface_art_keys_stay_centralized(self):
        # <!-- custom: SAS-owned InterfaceArt definitions are immutable shared resources even when their naming expands beyond today's SAS_EMOJI_* family.
        # Derive the protected keys from XML and reject exact raw-key literals in callers; inherited/dynamic engine ArtDefine-key APIs remain legal. (ChatGPT-5.6-Sol) -->
        sas_art_types = _xml_types(INTERFACE_ART_XML, "SAS_")
        failures = []
        literal_pattern = re.compile(r"^[uUrR]*[\"'](SAS_[A-Z0-9_]+)[\"']$")
        for path in _gameplay_python_files():
            source = path.read_text(encoding="latin-1")
            exceptions = {}
            tokens = list(tokenize.generate_tokens(io.StringIO(source).readline))
            for token in tokens:
                if token.type == tokenize.COMMENT and "resource-cache-direct:" in token.string:
                    reason = token.string.split("resource-cache-direct:", 1)[1].split("-->", 1)[0].strip()
                    if reason and not reason.startswith("("):
                        exceptions[token.start[0]] = reason
            for token in tokens:
                if token.type != tokenize.STRING:
                    continue
                match = literal_pattern.match(token.string)
                if match and match.group(1) in sas_art_types and token.start[0] not in exceptions and token.start[0] - 1 not in exceptions:
                    failures.append("%s:%d: raw SAS InterfaceArt key %s; use SASVisuals.InterfaceArt.%s or document resource-cache-direct: reason" % (path.relative_to(REPO_ROOT), token.start[0], match.group(1), match.group(1)))
        self.assertEqual(failures, [], "\n".join(failures))

    def test_visible_specialist_ids_and_resources_follow_xml(self):
        # <!-- custom: Execute the production resource class against small XML-info fixtures instead of requiring exact loop/variable spellings.
        # Hidden entries before/between visible ones expose slot-versus-ID mistakes; repeated reads verify the shared cache rather than just its method names. (GPT-6.1-Sol) -->
        source = CENTRAL_RESOURCE.read_text(encoding="latin-1")
        tree = ast.parse(source)
        definition = next(node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == "_SpecialistResources")
        compiled = compile(ast.Module(body=[definition], type_ignores=[]), str(CENTRAL_RESOURCE), "exec")

        class Resource:
            def __getattr__(self, name):
                return name

            def char(self, value):
                return value

        class Info:
            def __init__(self, name, visible):
                self.name = name
                self.visible = visible
                self.reads = {"texture": 0, "button": 0}

            def getType(self):
                return self.name

            def isVisible(self):
                return self.visible

            def getTexture(self):
                self.reads["texture"] += 1
                return "texture/" + self.name

            def getButton(self):
                self.reads["button"] += 1
                return "button/" + self.name

        class Context:
            def __init__(self, infos):
                self.infos = infos

            def getNumSpecialistInfos(self):
                return len(self.infos)

            def getSpecialistInfo(self, index):
                return self.infos[index]

        for visible in ((False, True, False, True), (True, False, True, False), ()):
            with self.subTest(visible=visible):
                # <!-- custom: Reversed real XML identities exercise presentation independently of numeric position. (GPT-6.1-Sol) -->
                names = list(reversed(sorted(_xml_types(SPECIALIST_XML, "SPECIALIST_"))))
                infos = [Info(names[index], flag) for index, flag in enumerate(visible)]
                namespace = dict((name, Resource()) for name in ("Font", "Yield", "Commerce", "FontSymbols", "YieldTypes", "CommerceTypes"))
                namespace["gc"] = Context(infos)
                spec = next(node.value for node in ast.walk(definition) if isinstance(node, ast.Assign) and any(isinstance(target, ast.Name) and target.id == "SAS_SPECIALIST_VISUAL_SPECS" for target in node.targets))
                mapping = eval(compile(ast.Expression(body=spec), "<specialist visual choices>", "eval"), namespace)
                exec(compiled, namespace)
                cache = namespace["_SpecialistResources"]()
                if infos:
                    self.assertEqual(cache.getTexture(0), "texture/" + infos[0].name)
                expected = tuple(index for index, flag in enumerate(visible) if flag)
                self.assertEqual(cache.visibleIds(), expected)
                self.assertIs(cache.visibleIds(), cache.visibleIds())
                self.assertNotIn("SAS_SPECIALIST_VISUAL_SPECS", namespace)
                self.assertNotIn("SAS_SPECIALIST_VISUAL_SPECS", vars(cache))
                cache.init()
                for index, info in enumerate(infos):
                    self.assertEqual(cache.getIcon(index), mapping[info.name][1])
                    for unused in range(2):
                        self.assertEqual(cache.getTexture(index), "texture/" + info.name)
                        self.assertEqual(cache.getButton(index), "button/" + info.name)
                    self.assertEqual(info.reads, {"texture": 1, "button": 1})


if __name__ == "__main__":
    unittest.main()
