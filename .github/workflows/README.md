# GitHub workflow checks

These files are developer/repository automation, not Civ4 runtime files.

- `python-ruff.yml` shows full Ruff output and runs critical Ruff Python sanity checks.
- `python24-compile.yml` runs the real CPython 2.4 parser/bytecode compiler through Docker.
- `checks-*.yml` splits blocking checks by subject so failures are independent and easy to locate.
- `runtime-aip-predump-refresh.yml` refreshes the committed Sevopedia Leader AI Personality predump and opens/updates a PR only when the predump file changes. It can be run manually and also runs automatically after pushes that touch known AIP predump dependency files.
- `build/` contains active automated check helpers grouped by subject.
- `tests/<subject>/` mirrors the `build/<subject>/` hierarchy for workflow/tooling helper tests; `checks-tests.yml` runs the full suite automatically, and the same suite can be run locally.
- `lib/` contains shared Python 3 helpers used by workflow scripts.
- Future `release.yml` and `release/` checks can be added for release-only checks such as documentation marker cleanup and archive contents.

These scripts run outside Civ4, so they may use modern Python 3. They do not need Civ4 Python 2.4 compatibility.

## Menu

- [Features](#features)
- [AIP predump refresh workflow](#aip-predump-refresh-workflow)
- [Python Ruff workflow](#python-ruff-workflow)
- [Markdown lint workflow](#markdown-lint-workflow)
- [Python 2.4 compile workflow](#python-24-compile-workflow)
- [Current automated checks](#current-automated-checks)
- [Helper reference](#helper-reference)
  - [Assets](#assets)
    - [`build/assets/advisor_defaults.py`](#buildassetsadvisor_defaultspy)
    - [`build/assets/art_button_paths.py`](#buildassetsart_button_pathspy)
    - [`build/assets/art_define_structure.py`](#buildassetsart_define_structurepy)
    - [`build/assets/fonts.py`](#buildassetsfontspy)
    - [`build/assets/leader_audio.py`](#buildassetsleader_audiopy)
    - [`build/assets/map_previews.py`](#buildassetsmap_previewspy)
    - [`build/assets/opening_music.py`](#buildassetsopening_musicpy)
    - [`build/assets/tech_audio.py`](#buildassetstech_audiopy)
  - [Diagnostics](#diagnostics)
    - [`build/diagnostics/bbai_log.py`](#builddiagnosticsbbai_logpy)
    - [`build/diagnostics/diagnostic_log_safety.py`](#builddiagnosticsdiagnostic_log_safetypy)
    - [Local `--staged` option for diagnostic defaults](#local---staged-option-for-diagnostic-defaults)
    - [`build/diagnostics/diagnostic_record_format.py`](#builddiagnosticsdiagnostic_record_formatpy)
    - [`build/diagnostics/revision_commit_references.py`](#builddiagnosticsrevision_commit_referencespy)
    - [`build/diagnostics/runtime_revision_history.py`](#builddiagnosticsruntime_revision_historypy)
    - [`build/diagnostics/runtime_status.py`](#builddiagnosticsruntime_statuspy)
    - [`build/diagnostics/sas_game_record_log.py`](#builddiagnosticssas_game_record_logpy)
    - [`build/diagnostics/sas_revision_history.py`](#builddiagnosticssas_revision_historypy)
  - [Documentation](#documentation)
    - [`build/documentation/agents_low_value_repeated_links.py`](#builddocumentationagents_low_value_repeated_linkspy)
    - [`build/documentation/art_samples.py`](#builddocumentationart_samplespy)
    - [`build/documentation/ci_markers_listed.py`](#builddocumentationci_markers_listedpy)
    - [`build/documentation/diagnostic_artifact_names.py`](#builddocumentationdiagnostic_artifact_namespy)
    - [`build/documentation/disclaimers_first.py`](#builddocumentationdisclaimers_firstpy)
    - [`build/documentation/drive_links.py`](#builddocumentationdrive_linkspy)
    - [`build/documentation/example_file_locations.py`](#builddocumentationexample_file_locationspy)
    - [`build/documentation/folder_indexes.py`](#builddocumentationfolder_indexespy)
    - [`build/documentation/generated_docs.py`](#builddocumentationgenerated_docspy)
    - [`build/documentation/image_filename_policy.py`](#builddocumentationimage_filename_policypy)
    - [`build/documentation/known_issues_chronology.py`](#builddocumentationknown_issues_chronologypy)
    - [`build/documentation/long_comments.py`](#builddocumentationlong_commentspy)
    - [`build/documentation/markdown_images.py`](#builddocumentationmarkdown_imagespy)
    - [`build/documentation/markdown_links.py`](#builddocumentationmarkdown_linkspy)
    - [`build/documentation/markdown_prose_changes.py`](#builddocumentationmarkdown_prose_changespy)
    - [`build/documentation/markdown_structure.py`](#builddocumentationmarkdown_structurepy)
    - [`build/documentation/numbered_references.py`](#builddocumentationnumbered_referencespy)
    - [`build/documentation/orphan_images.py`](#builddocumentationorphan_imagespy)
    - [`build/documentation/requires_version_markers.py`](#builddocumentationrequires_version_markerspy)
    - [`build/documentation/retired_names.py`](#builddocumentationretired_namespy)
    - [`build/documentation/sas_source_guide.py`](#builddocumentationsas_source_guidepy)
  - [EXE patches](#exe-patches)
    - [`build/exe_patches/exe_internals_placement.py`](#buildexe_patchesexe_internals_placementpy)
    - [`build/exe_patches/exe_patches_export_ignore.py`](#buildexe_patchesexe_patches_export_ignorepy)
  - [Hygiene](#hygiene)
    - [`build/hygiene/control_characters.py`](#buildhygienecontrol_characterspy)
    - [`build/hygiene/line_ending_churn.py`](#buildhygieneline_ending_churnpy)
    - [`build/hygiene/line_endings.py`](#buildhygieneline_endingspy)
    - [`build/hygiene/repository_hygiene.py`](#buildhygienerepository_hygienepy)
    - [`build/hygiene/text_blank_lines.py`](#buildhygienetext_blank_linespy)
  - [Python compatibility](#python-compatibility)
    - [`build/python/python24_compile.py`](#buildpythonpython24_compilepy)
    - [`build/python/star_import_names.py`](#buildpythonstar_import_namespy)
  - [Repository](#repository)
    - [`build/repository/adjacent_duplicate_lines.py`](#buildrepositoryadjacent_duplicate_linespy)
    - [`build/repository/assets_dlls.py`](#buildrepositoryassets_dllspy)
    - [`build/repository/commit_trailers.py`](#buildrepositorycommit_trailerspy)
    - [`build/repository/dev_logs.py`](#buildrepositorydev_logspy)
    - [`build/repository/dll_commit_message.py`](#buildrepositorydll_commit_messagepy)
    - [`build/repository/dll_define_changes.py`](#buildrepositorydll_define_changespy)
    - [`build/repository/dll_python_bindings.py`](#buildrepositorydll_python_bindingspy)
    - [`build/repository/dll_runtime_revision.py`](#buildrepositorydll_runtime_revisionpy)
    - [`build/repository/examples_archive_size.py`](#buildrepositoryexamples_archive_sizepy)
    - [`build/repository/future_dates.py`](#buildrepositoryfuture_datespy)
    - [`build/repository/ki_commit_titles.py`](#buildrepositoryki_commit_titlespy)
    - [`build/repository/makefile_windows_tools.py`](#buildrepositorymakefile_windows_toolspy)
    - [`build/repository/project_sources.py`](#buildrepositoryproject_sourcespy)
    - [`build/repository/release_upstream.py`](#buildrepositoryrelease_upstreampy)
    - [`build/repository/squash_message.py`](#buildrepositorysquash_messagepy)
    - [`build/repository/squash_pr_number.py`](#buildrepositorysquash_pr_numberpy)
    - [`build/repository/temp_files.py`](#buildrepositorytemp_filespy)
    - [`build/repository/ui_map_sync.py`](#buildrepositoryui_map_syncpy)
    - [`build/repository/version_metadata.py`](#buildrepositoryversion_metadatapy)
    - [`build/repository/workflow_keep_going.py`](#buildrepositoryworkflow_keep_goingpy)
    - [`build/repository/workflow_script_coverage.py`](#buildrepositoryworkflow_script_coveragepy)
  - [Runtime](#runtime)
    - [`build/runtime/aip.py`](#buildruntimeaippy)
    - [`build/runtime/aip_predump_values.py`](#buildruntimeaip_predump_valuespy)
    - [`build/runtime/detail_manager.py`](#buildruntimedetail_managerpy)
    - [`build/runtime/hands_free_defaults.py`](#buildruntimehands_free_defaultspy)
    - [`build/runtime/mapscripts.py`](#buildruntimemapscriptspy)
    - [`build/runtime/worldsizes.py`](#buildruntimeworldsizespy)
  - [Shared helpers](#shared-helpers)
    - [`lib/advciv_release.py`](#libadvciv_releasepy)
    - [`lib/blank_lines.py`](#libblank_linespy)
    - [`lib/ci_markers.py`](#libci_markerspy)
    - [`lib/cpp_lex.py`](#libcpp_lexpy)
    - [`lib/git_context.py`](#libgit_contextpy)
    - [`lib/reference_spellings.py`](#libreference_spellingspy)
    - [`lib/revision_history.py`](#librevision_historypy)
    - [`lib/sas_live_define_overrides_file.py`](#libsas_live_define_overrides_filepy)
    - [`lib/xml_defines.py`](#libxml_definespy)
  - [Source](#source)
    - [`build/source/advisor_scoreboard_space.py`](#buildsourceadvisor_scoreboard_spacepy)
    - [`build/source/checkout_byte_compares.py`](#buildsourcecheckout_byte_comparespy)
    - [`build/source/cpp_define_reads_cached.py`](#buildsourcecpp_define_reads_cachedpy)
    - [`build/source/cpp_standard_conformance.py`](#buildsourcecpp_standard_conformancepy)
    - [`build/source/custom_comment_closing.py`](#buildsourcecustom_comment_closingpy)
    - [`build/source/custom_comment_indentation.py`](#buildsourcecustom_comment_indentationpy)
    - [`build/source/float_format_int_division.py`](#buildsourcefloat_format_int_divisionpy)
    - [`build/source/inherited_files.py`](#buildsourceinherited_filespy)
    - [`build/source/lint_suppressions.py`](#buildsourcelint_suppressionspy)
    - [`build/source/python_aligned_columns.py`](#buildsourcepython_aligned_columnspy)
    - [`build/source/python_binding_targets.py`](#buildsourcepython_binding_targetspy)
    - [`build/source/python_dead_stores.py`](#buildsourcepython_dead_storespy)
    - [`build/source/python_define_reads_cached.py`](#buildsourcepython_define_reads_cachedpy)
    - [`build/source/python_define_reads_import.py`](#buildsourcepython_define_reads_importpy)
    - [`build/source/python_engine_callbacks.py`](#buildsourcepython_engine_callbackspy)
    - [`build/source/python_multiline_calls.py`](#buildsourcepython_multiline_callspy)
    - [`build/source/python_resource_api.py`](#buildsourcepython_resource_apipy)
    - [Custom-comment logical reflow](#custom-comment-logical-reflow)
    - [`build/source/python_wrapper_null_args.py`](#buildsourcepython_wrapper_null_argspy)
    - [`build/source/raw_getinfotype.py`](#buildsourceraw_getinfotypepy)
    - [`build/source/sas_live_define_overrides.py`](#buildsourcesas_live_define_overridespy)
    - [`build/source/sevopedia_top_attributes.py`](#buildsourcesevopedia_top_attributespy)
    - [`build/source/shared_define_values.py`](#buildsourceshared_define_valuespy)
    - [`build/source/source_change_provenance.py`](#buildsourcesource_change_provenancepy)
    - [`build/source/string_label_compares.py`](#buildsourcestring_label_comparespy)
    - [`build/source/unicode_button_paths.py`](#buildsourceunicode_button_pathspy)
  - [XML and rules](#xml-and-rules)
    - [`build/xml/advanced_start_era_points.py`](#buildxmladvanced_start_era_pointspy)
    - [`build/xml/asset_primary_tech.py`](#buildxmlasset_primary_techpy)
    - [`build/xml/asset_tech_prereq_redundancy.py`](#buildxmlasset_tech_prereq_redundancypy)
    - [`build/xml/barbarian_balance.py`](#buildxmlbarbarian_balancepy)
    - [`build/xml/bonus_font_order.py`](#buildxmlbonus_font_orderpy)
    - [`build/xml/building_art_lsystem_names.py`](#buildxmlbuilding_art_lsystem_namespy)
    - [`build/xml/civ_specific_assets.py`](#buildxmlciv_specific_assetspy)
    - [`build/xml/civ_specific_not_weaker.py`](#buildxmlciv_specific_not_weakerpy)
    - [`build/xml/corporation_prereq_bonuses.py`](#buildxmlcorporation_prereq_bonusespy)
    - [`build/xml/define_int_bounds.py`](#buildxmldefine_int_boundspy)
    - [`build/xml/define_tag_refs.py`](#buildxmldefine_tag_refspy)
    - [`build/xml/feature_impassables.py`](#buildxmlfeature_impassablespy)
    - [`build/xml/global_define_lengths.py`](#buildxmlglobal_define_lengthspy)
    - [`build/xml/global_define_name_style.py`](#buildxmlglobal_define_name_stylepy)
    - [`build/xml/global_defines_nonempty.py`](#buildxmlglobal_defines_nonemptypy)
    - [`build/xml/launch_guard.py`](#buildxmllaunch_guardpy)
    - [`build/xml/marsh_bonuses.py`](#buildxmlmarsh_bonusespy)
    - [`LLM_Helpers/balance/military_tree_continuity.py`](#llm_helpersbalancemilitary_tree_continuitypy)
    - [`build/xml/plot_asset_buttons.py`](#buildxmlplot_asset_buttonspy)
    - [`build/xml/plot_lsystem_asset_relationships.py`](#buildxmlplot_lsystem_asset_relationshipspy)
    - [`build/xml/religion_tech_buttons.py`](#buildxmlreligion_tech_buttonspy)
    - [`build/xml/retired_global_define_names.py`](#buildxmlretired_global_define_namespy)
    - [`build/xml/retired_xml_asset_names.py`](#buildxmlretired_xml_asset_namespy)
    - [`build/xml/sas_define_usage.py`](#buildxmlsas_define_usagepy)
    - [`build/xml/sas_text_file_placement.py`](#buildxmlsas_text_file_placementpy)
    - [`build/xml/sas_text_references.py`](#buildxmlsas_text_referencespy)
    - [`build/xml/tech_columns.py`](#buildxmltech_columnspy)
    - [`build/xml/tech_prereqs.py`](#buildxmltech_prereqspy)
    - [`build/xml/true_starts_coverage.py`](#buildxmltrue_starts_coveragepy)
    - [`build/xml/turn_define_gamespeed.py`](#buildxmlturn_define_gamespeedpy)
    - [`build/xml/unit_naming_combat_types.py`](#buildxmlunit_naming_combat_typespy)
    - [`build/xml/wonder_cost_columns.py`](#buildxmlwonder_cost_columnspy)
    - [`build/xml/wonder_culture_gpp_columns.py`](#buildxmlwonder_culture_gpp_columnspy)
    - [`build/xml/xml_child_duplicates.py`](#buildxmlxml_child_duplicatespy)
    - [`build/xml/xml_civ4_text_characters.py`](#buildxmlxml_civ4_text_characterspy)
    - [`build/xml/xml_comments.py`](#buildxmlxml_commentspy)
    - [`build/xml/xml_display_order.py`](#buildxmlxml_display_orderpy)
    - [`build/xml/xml_element_only_content.py`](#buildxmlxml_element_only_contentpy)
    - [`build/xml/xml_parent_duplicate_keys.py`](#buildxmlxml_parent_duplicate_keyspy)
    - [`build/xml/xml_redundant_defaults.py`](#buildxmlxml_redundant_defaultspy)
    - [`build/xml/xml_sas_text_english.py`](#buildxmlxml_sas_text_englishpy)
    - [`build/xml/xml_sas_text_inherited.py`](#buildxmlxml_sas_text_inheritedpy)
    - [`build/xml/xml_suspicious_angle_tags.py`](#buildxmlxml_suspicious_angle_tagspy)
    - [`build/xml/xml_suspicious_text_chars.py`](#buildxmlxml_suspicious_text_charspy)
    - [`build/xml/xml_text_duplicate_tags.py`](#buildxmlxml_text_duplicate_tagspy)
- [CI markers in commit messages](#ci-markers-in-commit-messages)
- [CI markers in source comments](#ci-markers-in-source-comments)
- [Run Locally](#run-locally)
- [Not currently automated](#not-currently-automated)
- [Dependabot](#dependabot)

## Features

According to ChatGPT-5.5:

- GitHub workflow checks live under [`.github/workflows`](/.github/workflows/).
- Workflow YAML files stay directly in this folder. Active Python 3 check helpers live under `build/<subject>/`, helper regression tests under matching `tests/<subject>/` folders, and shared helpers under `lib/`.
- `checks-*.yml` files are the authoritative lists of blocking category checks.
- The `.github/` workflow folder is development infrastructure and should stay excluded from player release archives through `.gitattributes`.

For example, this helped spot [map scripts that were previously unclassified in SAS map-script heaviness defines](https://github.com/wonderingabout/AdvCiv-SAS/actions/runs/27198308080/job/80295526028); they are now listed explicitly for exhaustiveness.

This also helped spot and fix duplicate parent XML keys [found by new GitHub workflow check](https://github.com/wonderingabout/AdvCiv-SAS/actions/runs/27258698041/job/80498936912) (See if needed [KI#148](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#ki-148)).

## AIP predump refresh workflow

[`runtime-aip-predump-refresh.yml`](/.github/workflows/runtime-aip-predump-refresh.yml) refreshes `SevoPediaLeaderCachePredumped.py` outside Civ4. It keeps the manual `workflow_dispatch` trigger, and also runs automatically on pushes that touch known AIP predump dependency files:

- `Assets/XML/Civilizations/CIV4LeaderHeadInfos.xml`
- `Assets/XML/AI_Variables_GlobalDefines.xml`
- `Assets/XML/GlobalDefines_advciv_sas.xml`
- `Assets/Python/Contrib/Sevopedia/ai_utils_shared_with_civ4.py`
- `Assets/Python/Contrib/Sevopedia/SevoPediaLeaderAIPValues.py`
- `.github/workflows/build/runtime/aip_predump_values.py`
- `.github/workflows/runtime-aip-predump-refresh.yml`

The workflow checks out the selected or pushed branch, runs `python .github/workflows/build/runtime/aip_predump_values.py --write`, reruns the normal checker, and then inspects the predump file diff. If there is no diff, the log says the predump is already current and no PR is created.

If there is a diff, it commits only `SevoPediaLeaderCachePredumped.py` to `bot/refresh-aip-predump-cache-<base-branch>` and creates or updates a PR named `Refresh AIP predump cache` targeting the branch that triggered the workflow.

The bot ignores its own refresh branches and skips runs by `github-actions[bot]`, so a generated predump PR does not recursively trigger another refresh. This uses only official checkout/setup-python actions plus GitHub's runner-provided `git`/`gh` tools.

If PR creation fails with a permission error, check the repository's Actions workflow permissions: the workflow needs `contents: write`, `pull-requests: write`, and repository settings that allow GitHub Actions to create pull requests.

Validated behavior, tested in [PR#31](https://github.com/wonderingabout/AdvCiv-SAS/pull/31):

- current `main` predump already current -> no PR;
- leader XML comment-only change (Test 0) -> no PR;
- real AIP numeric XML change (e.g., Temporary test 1: increase LEADER_MONTEZUMA's war likeliness iMaxWarRand from 50 to 10) -> predump refresh PR;
- shared AIP label/display change (e.g., Temporary test 2: "Build Unit %" -> "Build Unit Prob") -> predump refresh PR.

The [PR#31](https://github.com/wonderingabout/AdvCiv-SAS/pull/31) body keeps the detailed temporary test commits, GitHub Actions logs, and temporary bot PR links. The important result is that the bot reacts to actual generated predump drift, not merely to touched dependency files.

## Python Ruff workflow

[`python-ruff.yml`](/.github/workflows/python-ruff.yml) runs latest Ruff through `astral-sh/ruff-action` as a separate Python sanity workflow. It intentionally runs isolated from [`ruff.toml`](/ruff.toml), because `ruff.toml` is for the user's VS Code Ruff extension and local editing signal/noise, not for CI strictness.

The local config keeps legacy Civ4/Python 2.4 false-positive noise manageable in the user's IDE, while GitHub should show the broader repository picture. Both configurations exclude the verbatim `LLM_Helpers/context/mapscript_refs` archaeology corpus because downloaded reference sources are not AdvCiv-SAS runtime code and should not be lint-modified.

The workflow first prints the full `ruff check . --isolated --select ALL` grouped report so all findings are visible, then fails on a practical critical gate (ignoring only those deemed non-critical and too noisy after empirical review) for syntax/parse errors and Pyflakes bug checks.

The first GitHub run showed that only a few rules were clearly too noisy, so this is the first cautious narrowing step; narrow further only from actual failure output.

A further step fails on style rules promoted once the repository had none left, each a plain slip with one clear fix (2026-11-22):

- E703, a needless trailing semicolon; E714, `not x is None` for `x is not None`; E401, several imports on one line.
- The same day, once their findings were fixed by hand: E701, `if x: y` on one line; E702, `a; b`; E711, `== None`; E713, `not x in y`, already clean; E101, indentation mixing tabs and spaces.
- The base AdvCiv 1.12 comparison copy under `_1_AdvCiv-SAS/Docs/examples/source_comparison` is excluded, as it stays as it was.
- To promote another rule, fix its findings first, then add it to that step's `--select`.
- [KI#21.7](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#ki-21.7) retraces why: SAS's earlier hand sweeps fixed these rules too, but without a gate they came back.

A last step fails on Ruff's RUF100, a `noqa` that suppresses nothing. RUF100 needs every rule enabled, or each `noqa` naming a rule outside the narrow critical gate, such as `E402`, would look unused, so this step runs `--select ALL` and fails only on RUF100.

- Added on 2026-11-17: a `noqa: E402` was added for an import after a `sys.path` insert, which E402 already allows, and [`lint_suppressions.py`](#buildsourcelint_suppressionspy) passed it, since it checks that a suppression names a rule and a reason, not that one is needed.

For example, this helped spot shadowed duplicate Python callbacks in the base Civ4 `Oasis.py` map script (see [KI#164](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#ki-164)) and a dormant undefined `Point` (instead of `PointLayout`) helper in `RectLayout.py` (see [KI#165](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#ki-165)).

Note: Separate artifacts were considered, which according to ChatGPT-5.5 are as of now limited to 500MB for free users, but GitHub Actions already lets us view on the web browser/URL and download workflow logs as ZIP (as of now right click "Download Log Archive"), so we do not need and so do not use artifact storage for now.

## Markdown lint workflow

[`documentation-markdownlint.yml`](/.github/workflows/documentation-markdownlint.yml) fails on markdownlint findings in maintained documentation, using [markdownlint-cli2-action](https://github.com/DavidAnson/markdownlint-cli2-action) v25.0.0 (markdownlint-cli2 0.24.0 / markdownlint 0.42.0). Pushes and pull requests touching Markdown, either Markdown configuration, or this workflow trigger it; manual runs are also available. The mirrored base AdvCiv comparison branch is excluded as in the other sanity workflows.

Rule settings come from [`.markdownlint.jsonc`](/.markdownlint.jsonc), shared with the VS Code extension. Existing exceptions for tabs, long lines, raw HTML and intentional code-span whitespace remain unchanged.

[`.markdownlint-cli2.jsonc`](/.markdownlint-cli2.jsonc) defines the shared local/CI scope: all Markdown files anywhere in the repository, respecting `.gitignore`.

Explicit exclusions cover the legacy reference material in `_0_Legacy`, generated helper outputs/examples/commit diffs, imported map-script reference subfolders, dependency folders and version-named published changelog archives. Maintained context guides and archive README indexes remain checked.

New documentation locations need no per-file registration.

CI reports findings without modifying files. This complements the blocking local-link checks; declared-menu checks remain available for manual review.

A real README failure prompted this addition: three tab-indented history bullets became an unintended code block, causing MD046 to flag every later fenced example. Removing the three tabs fixed the list without changing the examples.

Run the same scope and configuration locally:

```sh
npx markdownlint-cli2@0.24.0
```

`npx` comes with Node.js; on Windows, `winget install --id OpenJS.NodeJS.LTS` installs it. Check the [markdownlint-cli2 project](https://github.com/DavidAnson/markdownlint-cli2) for more current installation advice.

## Python 2.4 compile workflow

[`python24-compile.yml`](/.github/workflows/python24-compile.yml) runs [`build/python/python24_compile.py`](#buildpythonpython24_compilepy) inside `ghcr.io/wonderingabout/python-2.4:2.4.6`, built from the separate [`wonderingabout/python-2.4-docker`](https://github.com/wonderingabout/python-2.4-docker) Docker-image recipe. It checks `Assets/Python` and `PrivateMaps` with the real CPython 2.4 parser/bytecode compiler, which is closer to Civ4's embedded Python than Ruff or modern Python 3.

This is intentionally a syntax/compile compatibility check only: it does not launch Civ4, run gameplay code, import `CvPythonExtensions`, or validate engine-only runtime objects. It uses `docker run` after normal checkout instead of a job-level container so GitHub Actions and checkout still run on the ordinary runner, while the old image only needs to provide Python 2.4.

A [test run confirmed it fails](https://github.com/wonderingabout/AdvCiv-SAS/actions/runs/27897204427) on Python 2.5+ ternary syntax such as `SAS_MAGIC_PY24_COMPILE_BREAK_TEST = 1 if True else 0` in `Assets/Python/SASMagicNumbers.py`.

## Current automated checks

The automated layout has two matching layers: workflow categories at `.github/workflows/checks-<subject>.yml`, and their Python helpers under `.github/workflows/build/<subject>/`. Helper regression tests mirror those subjects under `tests/<subject>/`; `checks-tests.yml` runs each populated subject in its own named step. Categories without tests need no empty folder.

| Helper/test area | Workflow |
| --- | --- |
| `build/assets/` | `checks-assets.yml` |
| `build/diagnostics/` | `checks-diagnostics.yml` |
| `build/documentation/` | `checks-documentation.yml`; Markdown lint additionally uses `documentation-markdownlint.yml` |
| `build/exe_patches/` | `checks-exe-patches.yml` |
| `build/hygiene/` | `checks-hygiene.yml` |
| `build/python/` | `python24-compile.yml`; `python-ruff.yml` invokes Ruff directly |
| `build/repository/` | `checks-repository.yml`; release checks use `repository-release-upstream.yml` |
| `build/runtime/` | `checks-runtime.yml`; the predump refresh bot reuses its helper through `runtime-aip-predump-refresh.yml` |
| `build/source/` | `checks-source.yml`; this workflow also runs `LLM_Helpers/formatting/reflow_custom_comments.py --check` |
| `build/xml/` | `checks-xml.yml` |
| `tests/` | `checks-tests.yml` |

There are nine `checks-*.yml` category workflows plus five specialized workflows for Markdown lint, Ruff, the real Python 2.4 compile check, the AIP predump refresh bot, and release upstream freshness. Each blocking checker has its own named GitHub step so progress, failures, duration and logs stay attributable to one concern.

The category checks cover repository/shipping safety, text hygiene, maintained documentation, XML/rules consistency, asset references, diagnostic defaults/history, runtime configuration, source-change conventions and the workflow-helper regression suite. They are still sanity checks rather than a substitute for C++ compilation, Civ4 runtime testing or code review.

All helper regression tests also run locally with:

```bash
python -m unittest discover -s .github/workflows/tests -t .github/workflows -v
```

To run one subject locally, use the same top-level directory:

```bash
python -m unittest discover -s .github/workflows/tests/repository -t .github/workflows -v
```

Keep `-t .github/workflows`: some tests import their helper as a package from there, such as `test_project_sources.py`, which then fails without it. On 2026-11-22 a run without it reported `ModuleNotFoundError: No module named 'build'`, which looked like a broken test, while the same 134 repository tests passed with `-t`.

Local platform-specific game-code tests live separately under [`tests/`](/tests/README.md), including the Windows/VC2003 diagnostic writer harness; they are not part of this workflow.

The `-t` argument keeps test package names distinct from standard-library modules such as `xml`. Source-tool tests also cover related manual helpers in `LLM_Helpers`; the commit-diff packaging tests live with repository tooling.

## Helper reference

### Assets

#### `build/assets/advisor_defaults.py`

Keeps `SAS_MILIT_UI_BATTLE_XY_ON=1` in shipped XML so Battles coordinates are sortable by default; setting it to 0 remains a local option when screen width is scarce.

`SAS_WORLD_CHANGES_SHOW_INTERMEDIATE_ON=0` keeps the Changes view compact by default; setting it to 1 displays each permitted raw event separately. `SAS_WORLD_CHANGES_SHOW_CANCELLED_ON=0` also omits eligible cancelled rows from the summary; setting it to 1 restores those rows. Both SHOW toggles therefore default to 0.

#### `build/assets/art_button_paths.py`

Verifies local `.dds` button/image paths under `Assets/Art` contain no whitespace because a path that works through a direct Civ4 button or atlas reference can fail when reused in `<img>` markup. Paths beneath any directory named `nif` are excluded because model texture paths can be embedded in NIF files and are not safely renamed through ordinary XML changes.

Base-game art paths referenced from XML are also outside this local-asset check. See [KI#118](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#ki-118), including the former `Buildings/Natya_Shastra/indian sreni.dds` example.

#### `build/assets/art_define_structure.py`

Checks all mod-local `CIV4ArtDefines_*.xml` files for the `Civ4ArtDefines` root, exactly one recognized ArtInfos collection, the required ArtInfo wrapper around each entry, one nonempty Type per entry, and no stray collection/root text.

Missing the Tipi's BuildingArtInfo wrapper caused a startup crash even though its loose child tags were valid XML; this check covers that gap alongside `xml_element_only_content.py`.

#### `build/assets/fonts.py`

Verifies shared UI font defaults are `1 / 2 / 3 / 4 / 3`.

#### `build/assets/leader_audio.py`

Verifies every non-empty leader diplomacy-audio reference resolves through the mod-local `Audio2DScripts.xml` and `AudioDefines.xml` tables to a non-empty filename. This catches per-era mapping typos such as Stalin's former Renaissance `AS2D_DIPLO_STALIN_EARLY_INTROO` reference instead of silently losing the intended diplomacy intro.

See [KI#1031](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#ki-1031).

#### `build/assets/map_previews.py`

Fails for each map script shown in Simple Game (its `isAdvancedMap` returns 0 or `False`, as read by the shared [`simple_game_scripts.py`](/LLM_Helpers/README.md#simple_game_scriptspy)) that has no `WorldPickerInfo` entry in `CIV4WorldPickerInfos.xml`, since such a script shows the dark default globe, and for each SAS preview path in that file whose `.dds` is missing. Its message gives the `map_preview_dds.py --variants 3` command that makes one.

On 2026-11-12, 14 of the 38 shown scripts had no preview and nothing had flagged it. Scripts that keep the default globe on purpose are listed in `DEFAULT_GLOBE_ON_PURPOSE` with their reason, such as RandomScriptMap, which picks another script each game; the check also fails when a listed script gains an entry, so the list stays current. See [KI#1082](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#ki-1082).

#### `build/assets/opening_music.py`

Verifies main-menu opening music has a valid `Audio2DScripts.xml` trigger/fixed script, and if shuffle is enabled, at least one valid non-`NONE` shuffle script.

#### `build/assets/tech_audio.py`

Verifies every technology's normal and multiplayer audio reference resolves through the mod-local `Audio2DScripts.xml` and `AudioDefines.xml` tables to a non-empty filename, that each technology keeps a distinct spoken recording, and that no technology-specific `AS2D_TECH_*` script remains orphaned after a technology is removed or renamed. `AS2D_TECH_GENERIC` is the intentional reusable exception.

Mod-local resolution matters because missing entries in these replacement audio tables are not inherited from base Civ4; this check would catch the missing Drama entries, malformed Communism multiplayer script ID, wrong-layer Aesthetics multiplayer reference, and stale removed-tech scripts found during a technology rework.

### Diagnostics

#### `build/diagnostics/bbai_log.py`

Verifies BBAI logging is disabled by default in `Assets/XML/GlobalDefines_advciv_sas.xml`. Every integer `SAS_BBAI_*` define is discovered automatically and required to be `0`, so dedicated categories such as Citizen, Culture, Evacuation, Worker, and Worker-sea logging cannot be omitted from the check when categories are added.

The only explicit nonzero exceptions are `SAS_BBAI_SCORE_LOG_INTERVAL_T_UNSCALED_GS=100` and `SAS_BBAI_LOG_USE_TIMESTAMPED_FILENAME=1`; these configure how enabled logging behaves but do not enable logging themselves.

#### `build/diagnostics/diagnostic_log_safety.py`

Verifies the BBAI and SASGameRecord final emission paths use the shared DLL-owned `logSASDiagnosticLiteralLine` writer instead of Civ4's opaque EXE `gDLL->logMsg` sink.

Ordinary rows are submitted promptly through persistent read/write/delete-shared handles so external tools can inspect or copy output during play; private retry buffers are reserved for unresolved startup paths and failed writes.

The check guards shared-sink presence, reader-sharing flags and the absence of physical-disk `FlushFileBuffers` calls or EXE-logger fallback. It does not prescribe argument lists, flag order, checkpoint statements or output-field spellings.

The XML/PythonDbg modernization exposed an overly broad file-level EXE-logger ban: `logSASCiv4LegacyLogRow` shares `CvGameCoreUtils.cpp` with the owned writer but deliberately uses the inherited logger.

- Only that bridge body is excluded from the EXE-call ban; the rest of the utility file and other publishers remain checked. The disk-flush ban still applies inside the bridge.
- [Checker fixtures](/.github/workflows/tests/diagnostics/test_diagnostic_log_safety.py) cover both the allowed bridge and rejected fallbacks, including comment/string braces and malformed boundaries.

- It does not execute native writes or prove bounded memory/error recovery. The local [diagnostic writer harness](/tests/README.md#diagnostic-writer) exercises the actual writer with normal and injected-failure I/O; it also checks prompt visibility and survival of final rows after abrupt process termination. Game lifecycle and autoplay performance require runtime testing.
- Already-formatted text is written directly, so literal `%` needs no EXE-boundary doubling; producer format strings still use ordinary printf escaping (`%%` for one intended `%`).

This check remains intentionally scoped to the two SAS diagnostic sinks implicated by [KI#375.3](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#ki-375.3), plus their shared writer and the runtime publisher, rather than every inherited logging caller in the DLL.

#### Local `--staged` option for diagnostic defaults

The diagnostic-default checks below ([`runtime_status.py`](#builddiagnosticsruntime_statuspy), [`bbai_log.py`](#builddiagnosticsbbai_logpy) and [`sas_game_record_log.py`](#builddiagnosticssas_game_record_logpy)) accept `--staged`, which makes the check read every file it inspects from the Git index instead of the working tree.

- Development diagnostics are usually left enabled but unstaged, so a plain local run fails on them even when the commit candidate is clean; `--staged` checks what would actually be committed.
- Unstaged companions such as a revision-history entry fail until staged, and the option fails outside a Git checkout. GitHub runs without it, because its working tree is the commit.

```bash
python .github/workflows/build/diagnostics/bbai_log.py --staged
```

#### `build/diagnostics/diagnostic_record_format.py`

Checks that active `logBBAI` and `logSASGameRecord` rows in `CvGameCoreDLL/*.cpp` keep the shared greppable record format: the line starts with an uppercase record ID (or a leading `%s` stage ID such as `FOUND_SITE_%s`), names every field, passes display text that has no XML type through `getSASDiagnosticQuoted` (a `city=%S` argument, as SASGameRecord does for `playerName="PC"`), and repeats no key.

Quotes written into the literal (`city=\"%S\"`) fail because they do not escape a quote inside the name.

- It was added after the BBAI modernization, when a T201 Huge run still showed older rows indented (`    WORKER_...`), civs logged unnamed after `player=%d`, and keys such as `target=%S ... target=(%d,%d)` repeated; one pass fixed 381 formats.
- Every token after the ID must be a `key=value` field: a rerun still showed bare words and groups such as `civ=CIVILIZATION_CHINA stageFlags C1=0` and `rejects(edgeOrIgnored=0 ...)`, now `rejectEdgeOrIgnored=0`.
- SASGameRecord shares the check: it already followed the format except four city names (`city=Emain Macha`, `slowCity=Philadelphia`, `targetCity=Rome`), fixed in revision 189. A display field fails only when its argument reads raw text such as `getName()` without a quoting helper, because SGR often passes a name quoted earlier.
- Pre-keyed `%s` fragments such as `techRows=%d %s` stay legal. Comments are skipped, so disabled rows and the `TrueStarts.cpp` debug surface stay outside the check.
- It does not check field values: identities should use narrow `%s` XML types (`getType()`), but a `getDescription()` passed where `getType()` belongs still needs review.

#### `build/diagnostics/revision_commit_references.py`

Checks finalized SGR and Runtime revision references against canonical default-branch history or new feature-branch ancestry and their matching source revision markers. SGR entries before revision 69 predate explicit source markers and retain ancestry validation only.

A new revision can say `pending` in its introducing commit because that commit cannot store its own final SHA. The next commit must finalize it, even without another recorder change. Finalized full commit hashes must be wrapped in backticks; `pending` remains status text.

The lifetime rule applies from this checker's introduction; current histories are audited in full. Local draft checks use the staged candidate, excluding unrelated unstaged build outputs and diagnostic overrides.

Existing event boundaries and squash intent (`[ci_squash_pr]` or local `--squash`) are reused: squash candidates validate the aggregate transition, ordinary commits retain individual references. Rewrite stale hashes and practical numbers after rebase/squash; an unchanged merge retains valid identities.

The practical number in a revision heading (`### Revision N - SAS practical M`) is checked for finalized entries only: it must equal `git rev-list --count` of the entry's commit. A pending one cannot be checked, as its number depends on how its branch lands.

- Until 2026-11-26 no number was checked, though all had matched by hand (200 SGR and 18 Runtime entries on 2026-11-15, 214 and 19 on 2026-11-26); the user asked for the check after the SASLiveDefineOverrides work (KI#128.5) reordered its chunks before committing, which would have shifted any number written for the old order.

- A squashed PR lands as one commit, a rebased or merged one keeps its commits, and a squash can sit on main's tip or replace an earlier preview of itself.
- Example: SASPilot's SGR202 was first written as 6765, a count along its branch, then 6751 for a squash on top of main's preview commit (6750), and finally 6750 again, as the squash replaced that preview.
- Only the integrator knows which applies, so the number is set when the PR lands, as the rewrite rule above says.

#### `build/diagnostics/runtime_revision_history.py`

Checks the XML runtime-recorder revision (or compiled labels in historical commits) against its [history](/_1_AdvCiv-SAS/Docs/revisions/SASRuntime.md), shared by the current-state JSON and activity JSONL. This label is independent of SASGameRecord's revision.

Reuses SASGameRecord's event boundaries and squash-intent policy (`[ci_squash_pr]`), checking each ordinary commit or the complete squash candidate: recognized implementation changes require exactly one increment; pure CI/checker, documentation/example and test maintenance leaves it unchanged. Local checks also validate the pending working-tree increment, including new files before staging.

The runtime-defaults check also enforces independent default-off source and screenshot watcher switches; shared environment metadata and the dialog listener are support components, not separate collection toggles.

Dedicated runtime files always qualify, including implementation comments and the shipped `Assets/SASRuntimeExitObserver.ps1`, `Assets/SASRuntimeDialogObserver.cs`, `Assets/SASRuntimeScreenshotObserver.ps1` and optional `Assets/SASRuntimeSourceObserver.ps1` companions.

Shared source/configuration changes are recognized by runtime symbols in changed lines; unusual refactors still need manual review.

A commit that bumps the Runtime revision must name it in its title, such as `(Runtime17)`, through the same title rule as SASGameRecord; see [`sas_revision_history.py`](#builddiagnosticssas_revision_historypy).

The regression tests cover multiple commits, missed increments, jumps/regressions, history mismatches, checker-only maintenance and clean CRLF working trees.

#### `build/diagnostics/runtime_status.py`

Checks that runtime recording is disabled in the shipped XML. The fixed `Logs/SASRuntimeStatus.json` and its linked timed-activity JSONL history are independent of BBAI/SASGameRecord enables and Civ4 INI logging switches.

Function names, JSON field inventories and exact callback statements are not checked here. The local VC2003 diagnostic harness exercises JSON output, disabled no-I/O behavior, autoplay countdown filtering and failed root migration. Actual EXE lifecycle transitions still require gameplay validation.

The shipped-value check requires `SAS_RUNTIME_STATUS_ON=0`, `SAS_RUNTIME_SOURCE_WATCH_ON=0` and `SAS_RUNTIME_SCREENSHOT_WATCH_ON=0`; local development overrides can enable them without staging those values.

All top-level shipped PowerShell/C# companions under `Assets/` must declare a default-off Define and launch/load owner in `RUNTIME_COMPONENT_CONTROLS`.

- Discovery uses file extensions, not a closed list or an `Observer` suffix, so a newly named or renamed file fails until classified; a missing registered file also fails until its registration/owner is reconciled.
- The dialog listener and shared environment helper inherit `SAS_RUNTIME_STATUS_ON`; source and screenshot observers retain their independent switches.

The guard checks registration, shipped values and filename literals in the declared owner; comments alone do not satisfy the reference check. It does not prove control flow or inspect arbitrary external programs. Native caller review and the Windows observer fixtures remain the behavior checks.

#### `build/diagnostics/sas_game_record_log.py`

Keeps the blocking SASGameRecord CI intentionally small:

- `SAS_SGR_LOG_ON` must be `0` in committed defaults, and `SAS_SGR_LOG` `0` too, so a player turns on the master, then picks a level, as with BBAI; until [SASGameRecord revision 214](/_1_AdvCiv-SAS/Docs/revisions/SASGameRecord.md#revision-214---sas-practical-6868), `SAS_SGR_LOG` alone was the switch and had to be `0`.
- `SAS_SGR_ACTION_TRACE_ON` must be `1`, and `SAS_SGR_SYSTEM_CONTEXT_LVL` must be `2`.
- `SAS_WORLD_CHANGES_SCRIPT_TEXT_ON` must be `1`: saved Changes history retains applied WorldBuilder script text by default even when SGR logging is disabled. Local opt-out tests must not change the committed default.
- Hardware identity, exact paths and process-context opt-ins must each be `0`; these checks catch accidentally committed diagnostic test overrides.
- `SAS_SGR_BUG_STRING_VALS_ON` must be `0`, keeping reviewed BUG strings redacted by default.
- `SAS_SGR_REVISION` in `GlobalDefines_advciv_sas.xml` is the single monotonically increasing implementation-update label; it must match the newest maintained revision-history heading.
- The source-context row must still read and emit that Define directly. The revision is not a compatibility switch and runtime code does not branch on it; build/source/DLL provenance separately describes stale or mixed binaries.
- The history/progression checker additionally enforces the commit rule when Git history is available: a mechanically recognizable qualifying SASGameRecord implementation commit increments exactly once, the revision never regresses or jumps by more than one, and unrelated commits do not increment it.

Compilation, runtime smoke/autoplay testing, log inspection and code review validate recorder implementation/schema behavior. The checker intentionally does not parse/pin individual row fields, writer call sites, lifecycle topology, save-marker bindings, AI provenance paths or other C++ implementation shapes.

Both recorder histories share numbered-entry parsing and require a nonempty `Change` explanation. Continued paragraphs/sub-bullets are accepted; dates, commit labels, hidden comments and fenced examples do not replace the explanation. A later documentation commit does not repair a missing blurb in the commit that advanced the revision.

Intentional SASGameRecord-related code changes, including checker and code-comment maintenance, increment the public revision even when emitted semantics are unchanged. Standalone documentation/history/example/package refreshes do not require a bump.

#### `build/diagnostics/sas_revision_history.py`

Automated historical provenance and current-branch progression check. Validates every finalized SASGameRecord revision hash against the repository's canonical default-branch ancestry. A stale amended/rebased commit can still exist as a Git object, while a valid mainline commit need not be an ancestor of a feature branch, so neither object existence nor current `HEAD` ancestry is sufficient.

Revisions newer than the default branch's recorder revision may instead identify commits in the current `HEAD` lineage. This permits several recorder commits within one PR without leaving multiple entries pending; an amended/rebased hash outside that lineage still fails. Already integrated revisions retain the canonical default-branch requirement.

Callers may pass an explicit canonical branch; otherwise local runs discover `origin/HEAD`, `origin/main` or `main`, and abstain from ancestry validation when none is available.

Revisions 69-152 verify their historical compiled-header marker; revision 153+ verifies the single `SAS_SGR_REVISION` GlobalDefine stored by that commit. Only the newest entry may say `pending`: a commit cannot store its own final hash, but older entries must be finalized.

When the default-branch range is available, the checker also inspects current branch commits individually.

- Dedicated recorder/checker/helper files and SASGameRecord-named Python helpers qualify.
- Other game-source/configuration bridge changes qualify when their diff exposes SASGameRecord markers.
- The known source packager `LLM_Helpers/packaging/make_light_source_zip.py` is excluded: selecting recorder examples/screenshots does not change the recorder. Other helpers retain conservative marker detection, even if their names do not mention SASGameRecord.
- A rename that leaves a file's content unchanged is no recorder change, and the dedicated helper and packager paths are kept at both their flat and their 2026-11-10 `LLM_Helpers/` locations, so older commits are judged by the paths they used.
- A commit that bumps the revision must name it in its title as a whole word, such as `(SGR197)` or `(Runtime17, SGR197)`, after `fc663b10b` bumped SGR197 and Runtime17 without naming either. Squash candidates and merge commits are not checked: their titles come from the PR or name the merged branch. KI numbers stay optional.

This is intentionally conservative automation around the written policy rather than an attempt to infer every semantic dependency.

Commit selection follows the event and explicit merge intent:

- Default-branch pushes check the first-parent commits in `before..after`, including earlier commits in a multi-commit push. Feature-branch pushes defer progression to the PR check because their payload does not identify its merge policy; defaults and history validation still run.
- Ordinary PRs check each authored commit from the base/head merge base, independently of the synthetic merge checkout.
- A PR whose newest commit message carries `[ci_squash_pr]` checks the aggregate base-to-head change as one integration commit: qualifying changes require exactly one bump, unrelated changes require none. Intermediate bumps or corrections do not create public revisions; removing the label restores per-commit checks.
- Local/manual checks retain per-commit behavior; `--squash` explicitly checks the complete working candidate against its default-branch merge base. For example, `python .github/workflows/build/diagnostics/sas_revision_history.py --squash`; the runtime checker accepts the same option.
- A merge commit is judged against the parent with the higher revision, for its number and for whether it changes the recorder.
  - Merging main into the SASPilot branch on 2026-11-17 failed as a jump from 202 to 204: both had used 202 meanwhile, and against the branch's own parent the merge seemed to skip one. Against main's 203, the merge adds the branch's change as 204, one step.
  - A merge that only brings in one side's bump equals that parent and needs none.

This history check complements the minimal revision/default synchronization check and runs automatically in `checks-diagnostics.yml`. It needs canonical default-branch history, so that workflow performs a full-history metadata checkout with blob filtering.

### Documentation

#### `build/documentation/agents_low_value_repeated_links.py`

Keeps low-value repeated links out of AGENTS.md, which agents read whole, so a link whose target the text already names only adds a path to read past.

As of now it covers KI links only: AGENTS.md links only its first KI mention, as `[KI#N](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#ki-N)`, to show where the Known Issues live; every other mention is plain `KI#N`. `--fix` links and unlinks in place.

- Agents read AGENTS.md whole, and a KI number names itself, so the Known Issues path repeated on each KI link was churn that took their focus (the user, 2026-11-24). Before the check, AGENTS.md linked 16 of its 64 KIs, some several times.
  - The request named the rule, link only the first one, but not its intent, so Claude Code Opus 5.5 first read it as each KI's own first mention, and its `--fix` added 46 links; once the user gave the intent, it was clear that this went the opposite way.
- Other links are not covered, so a new kind would be a new rule here. Links to helpers may repeat, as each repeat reminds agents that the helper matters; links to guides and AGENTS.md's own sections may too, as only about 20 of them repeated, too few to be worth a rule.
- Mentions in code spans, fenced blocks and other links' labels are left as they are, and a number with no entry is not linked, such as KI#176.2, which was merged into KI#1091.
- The name says what the check removes, links repeated across the document, such as the Known Issues path 16 times, that are of low value to agents, as the text already names their target (2026-11-24).
  - `agents_ki_links` was too narrow, as KI links are only the first kind covered, and `agents_repeated_links` misled alone, as some repeats are allowed; `low_value` says which repeats go.
  - Both words count: a low-value link used once or a few times costs little and can stay, while one repeated a dozen times or more, as the Known Issues path was, adds up.
  - `agents_boilerplate_links` was less accurate, as boilerplate is text copied in a set shape, while these links were written one by one.

```bash
python .github/workflows/build/documentation/agents_low_value_repeated_links.py
```

#### `build/documentation/art_samples.py`

Keeps the [Art Tools Guide](/_1_AdvCiv-SAS/Docs/Modding_Resources/README_Art_Tools.md#regenerating-the-samples)'s rendered sample pictures in step with the renderer. They fell behind once: Grace O'Malley's still kept the wide eyes of a render made before the bone skinning was fixed, while her GIFs had them right.

- CI has no Civ4 art to render with. [`regenerate_art_samples.py`](/LLM_Helpers/README.md#regenerate_art_samplespy) records a fingerprint of the renderer's code in `LLM_Helpers/art_viewing/art_samples_fingerprint.json` after a complete, successful run, and this check fails when `nif_preview.py`, `civ4_assets.py`, `fpk_tool.py`, `plot_scene.py`, `art_gallery.py`, `art_search.py` or the sample list itself has changed since.
- Comments and blank lines are left out of the fingerprint, so editing only comments does not ask for new pictures.
- The check cannot tell whether the regenerated pictures were reviewed; look at them before committing.

```bash
python .github/workflows/build/documentation/art_samples.py
```

#### `build/documentation/ci_markers_listed.py`

Fails when a CI marker in [`lib/ci_markers.py`](/.github/workflows/lib/ci_markers.py) has no row in the tables of [CI markers in commit messages](#ci-markers-in-commit-messages) or [CI markers in source comments](#ci-markers-in-source-comments), when a row names a marker that file does not define, or when a workflow script spells a marker in its code instead of importing it.

- Added on 2026-11-25 at the user's suggestion, when `ci_define_uncached:` joined `resource-cache-direct:` and `sas-ci-string-compare-exemption:`, which their checks had each spelled in their own file and no section listed.
- Its first run also found `[ci_squash_pr]` and `[ci_update_dll]` spelled in two help texts, `requires_version_markers.py`'s and `dll_commit_message.py`'s, which now take the constants.
- Marker-shaped strings, a bracketed `[ci_x]` or a word such as `ci_x:`, count too, so a new marker cannot start in a check's own file. Comments and docstrings may name a marker, as this entry does.

```bash
python .github/workflows/build/documentation/ci_markers_listed.py
```

#### `build/documentation/diagnostic_artifact_names.py`

Requires explicit generated diagnostic paths in the root README's relevant sections and Logging Inventory, so a reader can find a file without guessing what "companion JSON" means.

- Reads fixed/formatted `SASRuntime*.json` / `SASRuntime*.jsonl` names from `SASRuntimeStatus.cpp` and all top-level shipped PowerShell/C# companions under `Assets/`, normalizing process suffixes to `*`. Also checks the concrete Release and installed DLL build-report locations, rather than requiring invented path tokens such as a configuration placeholder.
- Requires a visible inline-code path such as `Logs/SASRuntimeExit_*.json`; mentions only inside fenced samples or hidden comments do not count. Documents explain the base directory instead of hardcoding the user's Windows profile.
- The small publisher set is audited each run, including documentation-only edits. This is a scoped discoverability guard, not an arbitrary-language path parser or a requirement to list unrelated JSON settings/captures; update the scope if a new publisher uses another naming/path construction.

#### `build/documentation/disclaimers_first.py`

Requires each listed guide's disclaimer directly under its title, before its description and menu: a disclaimer only protects if readers meet it before anything else.

- On 2026-11-12 the user asked that the modding disclaimer of the [Modding Resources](/_1_AdvCiv-SAS/Docs/Modding_Resources/README.md) guide and the disclaimer of the new [EXE patches guide](/_1_AdvCiv-SAS/Docs/Modding_Resources/README_EXE_Patches.md) stay first.
  - A first draft made them the first sections after the description; the user preferred them directly under the title, as a quote block starting with a plain `> **Disclaimer:**`, which covers the whole guide, and with no heading or menu entry.
- The guides and their labels are listed in `REQUIRED_DISCLAIMERS`; add a guide there when it gets a disclaimer. A missing guide or label fails loudly, so a rename cannot silently drop the check.

```bash
python .github/workflows/build/documentation/disclaimers_first.py
```

#### `build/documentation/drive_links.py`

Requires each Google Drive file or folder to be linked at most once per Markdown document, and every Drive link to have a recognised form with an ID (`/drive/folders/<id>`, `/file/d/<id>`, `?id=<id>` or a Docs `/d/<id>`).

- Evidence screenshots live in Drive folders, mostly one per Known Issue. A link copied from another entry still opens a real folder, so the wrong evidence goes unnoticed: on 2026-11-11 the check found KI#1071 linking KI#2's folder, and the Modding Resources guide linking one folder both as its impluvium example and as the whole Modding_Resources Drive.
- The same folder may still be linked from different documents, such as the Modding_Resources Drive from both the Modding Resources guide and README_References.md.
- Whether a link opens is not checked, since that needs the network and the folder's sharing settings. `_0_Legacy/`, `LLM_Helpers/context/` and `Docs/changelogs_web/` keep their own links.

```bash
python .github/workflows/build/documentation/drive_links.py
```

#### `build/documentation/example_file_locations.py`

Reserves `_example` filenames for textual/code/data captures under `_1_AdvCiv-SAS/Docs/examples/`. Screenshots stay under `_1_AdvCiv-SAS/Images/` with descriptive names without `_example`; an image using that marker fails even inside the examples folder. Imported/generated context and executable `test_` modules are outside the artifact rule.

For example, `LLM_Helpers/output_example.txt` fails while `Docs/examples/light_source/packaging_refresh_example.txt` under `_1_AdvCiv-SAS` passes. The packaging capture was manually copied before automatic text receipts existed; its provenance belongs in the explanatory documentation.

Normal runs use added/changed/renamed paths from the push/PR comparison, including untracked local draft files. Missing comparison history, checker changes or `--all` select a full current-path audit. Only filenames/locations are checked; payloads are not opened.

The initial inventory found three screenshots using `_example`; their names and image links were updated to keep the marker specific to textual examples. Existing textual captures already occupied the intended examples hierarchy.

#### `build/documentation/folder_indexes.py`

Keeps folder indexes listing what their folders hold, in alphabetical order, so nobody has to remember to: [`LLM_Helpers/README.md`](/LLM_Helpers/README.md#folders), this README, and the [Modding Resources guides](/_1_AdvCiv-SAS/Docs/Modding_Resources/README.md#guides-in-this-folder).

- Only `README.md` may sit directly in `LLM_Helpers/`; every other helper belongs in the folder of its job.
- Every `LLM_Helpers` folder has a `` ## `folder/` `` section and a Folders table row, both alphabetical, and every helper file is named in its folder's section. `context/` is described as a whole.
  - It found `light_source_python24_linux.py` undescribed when it was added on 2026-11-10.
  - Exception: a folder in `GUIDE_DOCUMENTED_FOLDERS` is documented only in its guide, so every helper file in it, Ghidra `.java` scripts included, must be named in that guide instead, and its README section must be a single line linking to the guide and its disclaimer, with no subsections.
    - Since 2026-11-12 `exe_analysis/` is documented in the [EXE patches guide](/_1_AdvCiv-SAS/Docs/Modding_Resources/README_EXE_Patches.md): its technical details stay for agents in Git and the light-source ZIP, but out of player downloads, while the README, which ships, says only "See the EXE patches guide and the corresponding disclaimer", so a downloaded ZIP holds no description of the EXE work.
- This README's helper reference subjects, the helpers within each subject (by file name), and the helper/test area table are alphabetical. Each check script in `build/` and shared module in `lib/` has a matching heading in the reference and appears in the menu. Private modules prefixed with `_` are exempt.
- The short `build/` and `tests/` READMEs list each subject folder that exists in their own directory.
- Every guide in `_1_AdvCiv-SAS/Docs/Modding_Resources/` is listed under its README's "Guides in this folder", by file name; a list that claims to cover its folder should not need remembering either.

```bash
python .github/workflows/build/documentation/folder_indexes.py
```

#### `build/documentation/generated_docs.py`

Automated documentation check. Validates registered source-to-text conversions in `TEXT_CONVERSIONS`: each entry declares its canonical source, generated text output, converter, refresh command and optional related source artifacts. When run, it regenerates each output into a temporary directory and compares its text with the tracked copy; missing sources or outputs fail.

Add future conversions to this registry with their appropriate converter. The base AdvCiv manual is currently the only entry: `manual.odt` is the canonical source, `manual.txt` is the output and `manual.pdf` is a related artifact.

When given a PR/push-style `--base-ref`, the helper can also check the complete change range: a registered source or related artifact changing without its corresponding text output changing fails. For the manual, this also catches PDF-only edits while ODT content remains authoritative for exact text verification.

Manual dispatch has no change-range base and still verifies all current converted text content.

The helper also accepts `--event-name` for GitHub-style range recovery. After an amended/force-pushed commit, the push event's previous SHA can be absent even from a full-history checkout.

When the previous SHA does exist but the force push replaced it, every change-range check compares from the newest commit both histories share instead, through `push_base_in_history` in [`lib/git_context.py`](/.github/workflows/lib/git_context.py).

- On 2026-11-16, `main` was reset under the SASPilot squash and the next push was judged against that squash, so `source_change_provenance.py` reported every SASPilot import and binding as removed.
- `test_force_push_is_judged_from_the_shared_commit` in `test_generated_docs.py` guards the rule.

For pushes only, the checker first tries fetching that exact commit from `origin`. If it is no longer served, a visible notice reports that paired source/text change-range validation cannot run; all current text-conversion and handicap-report content checks still run and can fail normally.

Missing PR or ordinary local bases fail with a clear diagnostic instead of a Git traceback. Available bases always retain the complete-range check.

Rebuilds the published handicap comparison from current `CIV4HandicapInfo.xml` and the pinned [`handicap_infos_baseline.xml`](/_1_AdvCiv-SAS/Docs/examples/handicap/handicap_infos_baseline.xml).

The baseline was copied from the local base AdvCiv comparison tree only after verifying every published left-side TSV cell; reproducing the entire existing report also confirmed its unchanged fields and totals.

The historical "Base AdvCiv 1.12" report label is retained. No sibling mod checkout is needed in CI.

Display labels are read from the report title. Only report timestamp and absolute source/output paths are ignored; tables, values, deltas, entry ordering and summary counts must match.

To refresh, run `python LLM_Helpers/code_history/convert_advciv_manual_to_txt.py` or `python .github/workflows/build/documentation/generated_docs.py --refresh-handicap`. The checker uses temporary output files and does not overwrite reports unless explicitly asked to refresh the handicap report.

#### `build/documentation/image_filename_policy.py`

Keeps maintained documentation/reference image filenames unambiguous across [`_0_Legacy/Images/`](/_0_Legacy/Images/) and [`_1_AdvCiv-SAS/Images/`](/_1_AdvCiv-SAS/Images/). These naming rules apply to the maintained image trees. Inherited gameplay art can reuse basenames.

- Legacy/base-reference screenshots use the `0.x` namespace; numbered current AdvCiv-SAS images use `1.x`. Descriptive unnumbered SAS images remain valid when a numbered series is not useful.
- Image basenames are case-insensitively unique across both maintained image trees, so an image can be identified reliably in documentation, logs, agent handoffs and filename searches without first knowing its folder.
- `_0_Legacy` is a subset of the SAS tree, so each `_0_Legacy` top-level folder (`Docs`, `Images`) and each `_0_Legacy/Images` subfolder (`advisors`, `sevopedia`, ...) must also exist under `_1_AdvCiv-SAS`. The reverse direction and `_0_Legacy/Docs` subfolders (`AdvCiv`, `BBAI`, ...) are not checked: they hold inherited source material with no SAS counterpart.
- Image files belong in the two maintained image trees or in `Assets/Art/` and `Assets/Res/` for game assets.
  - Added on 2026-11-13: the Sevopedia EXPAND template, `civ4_expand_button.png`, had sat in `LLM_Helpers/game_runs/ui_maps/` since 2026-11-11, outside the image trees, so their naming checks did not see it and light-source ZIPs, which pack selected image folders, left out the template `map_sevopedia.py` needs. It moved to `_1_AdvCiv-SAS/Images/sevopedia/`, beside the Sevopedia screenshots.
  - The [extracted FPK road texture](/_1_AdvCiv-SAS/Docs/examples/fpk/fpk_tool_extract_example/art/terrain/routes/roads/roadprimitive.dds) keeps its original path so the example shows the extractor's output, the one listed exception.
- The full current image inventory is cheap to scan and is checked every run, including untracked local draft images. This catches a new file colliding with an unchanged filename rather than limiting the comparison to changed paths.

The `0.x`/`1.x` split was introduced while adding legacy base-AdvCiv UI references: existing SAS category suffixes were retained and only their leading namespace changed, avoiding an unnecessary renumbering of established image families.

#### `build/documentation/known_issues_chronology.py`

Keeps new history paragraphs at the end of an existing Known Issues entry. It compares that document with the push/PR base, matching entries by KI number; unchanged content requires no chronology scan.

- The motivating example is KI#979's dated post-fix replay note inserted before its existing archaeology and credits. Such placement interrupts the investigation thread; the corrected note follows the earlier material.
- Rejects clear inserted paragraphs when retained body paragraphs still follow them. New KI entries and appended follow-ups are allowed, including additions before the next entry's anchor.
- Conventional `Screenshots/files for this issue:` archive headers are metadata, so adding or moving them to the top does not count as inserting investigation history. Actual replay/investigation paragraphs remain subject to the chronology check.
- Rejects a paragraph that leaves an entry still present and appears in another. On 2026-11-18 a KI#38.7 patch applied at a shifted line landed inside KI#39, and moving it back carried KI#39's last three paragraphs into KI#38.7; the insertion rule allowed it as a deletion plus a new entry, and the structure checks passed.
  - The user noticed while reviewing: VS Code showed KI#39's text, written months before, as new green lines, which made no sense for a commit adding KI#38.7. A content comparison then showed KI#39 had lost its ending, which this rule now reports by itself.
  - Only a paragraph found in one entry counts, so shared credit lines, such as the C++ File Audit Album's "Found and documented … with the help of ChatGPT-5.6-Sol", do not; a whole entry merged into another, as KI#176.2 into KI#1091, leaves no source and passes.
  - Replayed over the 546 commits that changed the Known Issues, it flags 5, all from 2026-08-30: a "Reserved during ChatGPT-5.6-Sol's C031 … re-audit" note moved to the newest provisional entry at each step of that discontinued audit.
  - A declared split passes: when the source entry keeps a paragraph saying it "moved" with a link to the destination, and the destination links back, its paragraphs may move word for word.
    - Splitting KI#11's sheep-yield report into KI#11.3 (2026-11-22) needed it, as keeping the report in KI#11 left the split half done (the user).
    - An unmarked move still fails, and paragraphs only match word for word, so a move cannot reword them.
    - Both the "moved" note, with "moved" as a whole word, and the link back must be new paragraphs: Codex's review found that "removed" matched too and that a declaration already in the document would have let any later move pass.
- Whitespace reflow, title/status edits, paragraph corrections and deletions are allowed. This conservative check cannot tell whether rewritten prose falsifies history; semantic review remains necessary.
- Run `python .github/workflows/build/documentation/known_issues_chronology.py --base-ref HEAD` locally. It reports all detected insertions without editing the document.

#### `build/documentation/long_comments.py`

Verifies the two archives under [`_1_AdvCiv-SAS/Docs/Long_Comments`](/_1_AdvCiv-SAS/Docs/Long_Comments/) stay synchronized with their live `Long_Comments_XML.txt #N` and `Long_Comments_py.txt #N` markers. A live marker without an archived entry fails, and an archived entry without any live marker fails so deleted or superseded source comments do not accumulate as stale documentation.

The documentation archives must also remain valid UTF-8; this prevents legacy encoding damage from being silently reintroduced.

Historical changelogs, archived dev logs, generated LLM commit-diff context and helper outputs, snapshots, and workflow/test files are ignored as references: they may legitimately preserve old marker text, but they must not keep a dead current entry alive. Multiple IDs on one marker line are supported.

IDs remain stable and are not renumbered when stale entries are removed.

#### `build/documentation/markdown_images.py`

Validates local images in maintained Markdown: their files must exist, alt text must equal the URL-decoded filename (including extension), and an HTML `<img>` must specify a positive pixel width. Markdown image syntax, including reference-style images, fails because it does not provide the explicit width used by our screenshot previews.

Existing descriptive and stale pre-rename alts were normalized in the initial sweep. External badges/URLs and fenced-code, inline-code or comment examples remain outside this local-image policy; ignored/generated review copies are excluded through shared maintained-document discovery.

Local image paths must start at the repository root, for example `/_1_AdvCiv-SAS/Images/sevopedia/1.710_sevopedia_techs%20(1).JPG`. This keeps screenshot links valid when their Markdown guide moves and gives contributors one path convention to follow. If the image itself moves or is renamed, update its references.

The check also applies the repo-root path rule to HTML image examples in `.markdownlint*.jsonc` so config comments demonstrate the same convention.

#### `build/documentation/markdown_links.py`

Local file links must begin with `/`; same-page anchors and external URLs remain valid. This prevents a document move from changing its link targets, though moving the target still requires updating links. The existing link-validation pass checks this rule without a separate scan.

Verifies every repository-local file or directory referenced by a Markdown link resolves to an existing repository path, and verifies `#heading` fragments for Markdown targets against GitHub-style heading anchors and explicit HTML anchors.

It checks normal and explicit reference-style Markdown links plus HTML `<a href="...">` tags, while ignoring external URLs and fenced-code, inline-code, or comment examples. Image references are handled separately by `markdown_images.py`.

A standalone backticked path such as `../tests/` is also flagged when it resolves inside the repository. Use a repo-root path or a descriptive link label so the reference stays clear when the guide moves.

Local links must use repository-root paths beginning with `/` (for example `/_1_AdvCiv-SAS/Docs/README_Known_Issues.md`); document-relative links such as `../README.md` are rejected so moving a Markdown file does not silently retarget them. Same-page anchors and external URLs remain valid.

It also verifies the continuous Known Issues ledger and its standardized `KI#number` schema. Every integer through the highest body entry or stable `F### / provisional KI#number` assignment in the C++ File Audit Album must have an explicit Fixed, Pending, Merged, Rejected or Retired entry; the menu and body identifier sets must match without duplicates; and every entry uses a stable short `#ki-number` anchor.

This catches both undiscoverable body entries such as the previously omitted KI#202 and wholly absent provisional/disposition entries such as KI#501.

Read its whole output, or at least its last line, which gives the verdict: `FAIL Markdown links: N error(s) above`, or the two OK lines.

- Example (2026-11-16): an agent ran it through `tail -1` with KI#1095 alone on main. The last line was then only "Checked N local link reference(s)", so it read a pass and told the user a gap in the KI numbers was fine, while the errors above it listed KI#1084 to KI#1094 as missing; the final FAIL line was added after.

When `_LLM_REPO_FILE_MANIFEST.txt` is present in a light-source ZIP, tracked files and directories intentionally omitted from the bundle are still recognized as existing repository paths; Markdown fragments are checked whenever the target Markdown file itself is bundled. This prevents both moved/renamed repository targets and renamed Markdown headings from silently leaving stale local links.

#### `build/documentation/markdown_prose_changes.py`

Checks list layout in every tracked Markdown file, plus added/edited maintained prose against the push/PR base (local default: `HEAD^`).

- Flags blocks of at least 400 characters only when the existing prose helper finds a safe sentence boundary with at least 100 characters on each side; single long sentences and short attached follow-ups remain valid.
- Soft-wrapped lines still form one rendered paragraph. Split distinct thoughts into a few blank-line paragraphs or child bullets, keeping short related sentences together.
- An added/edited indented follow-up sentence after a list item ending in a full stop needs an explicit child bullet or a separate paragraph; ordinary mid-sentence wrapping remains valid. This checks visible structure, not whether every Markdown section should be a list.
- Reject an apparent tab/four-space-indented list immediately after a prose paragraph, including in unchanged tracked docs: Markdown can merge its bullets into that paragraph. Separate a new top-level list with a blank line and leave its bullets unindented; valid nested lists and ordinary soft wrapping remain allowed.
- Code, tables, blockquotes and HTML comments are excluded. The paragraph-length rule additionally excludes untouched historical prose, copied/generated context and numbered archived changelogs; the tracked-file list-layout scan has no historical-doc exemption.
- An added or edited table row of 1000 characters or more fails: keep the row a short summary and move its details into a table of its own, one row per field or check, linked from the cell.
  - Added on 2026-11-19, as tables were outside the prose rule and the SASPilot guide's `reminders` row, on the SASPilot branch, had reached 5710 characters, one check appended after another; it became the guide's Reminders table.
  - Untouched long rows wait for their next edit; that day 13 rows of `README_Assets_Rebalancing.md` (rationale paragraphs in table cells, up to 1763 characters) and the guide's `relations` row were over the limit.
- Reports affected paths and line numbers without rewriting files. Run locally with `python .github/workflows/build/documentation/markdown_prose_changes.py --base-ref HEAD`.

The [existing helper](/LLM_Helpers/README.md#reflow_markdown_prosepy) previews sentence boundaries; its source-only output still needs review for visible structure. Passing this automated check does not establish that the chosen paragraphs or bullets are coherent.

#### `build/documentation/markdown_structure.py`

Automated documentation check. Uses Git to discover maintained Markdown, including nonignored new files during local review; Git-free archives use filesystem discovery instead. Imported reference/context corpora are outside this maintenance scope.

- A Menu/Contents section is required unless a file or category has an explicit, reasoned exemption in the checker. Legal text, short folder indexes, generated examples and historical records have documented exceptions; a new guide elsewhere is checked automatically.
- Menus must index each following body heading once, in body order, with the same rendered title and indentation: one `&emsp;` or two bullet-list spaces per heading level. A presence exemption does not excuse errors in a menu that exists.
- Menus list only the document's own headings. A menu row linking to another document looked like a section of this one, as `Modding_Resources/README.md` did for its sibling guides and `README.md` for three `LICENSE.md` headings; such links belong in a section's text.

Known Issues indexes numbered level-2 KI entries; internal investigation subheadings remain outside its menu. Menu introductions are retained; a refresh also keeps a row linking to another document, which the check then reports.

Explicit HTML `<a id="...">` / `<a name="...">` anchors are rejected outside numbered `ki-N[.N...]` targets in `README_Known_Issues.md`. Ordinary links use heading-generated anchors to avoid a confusing second naming scheme; KI targets remain short and stable when issue headings change. Code examples are excluded from this rule.

Existing `markdown_links.py` continues to validate destinations and stable KI anchors.

Also rejects unpaired `**` bold markers within a paragraph, excluding fenced code, inline code, HTML comments and escaped literal stars. This is a targeted Markdown guard rather than a full CommonMark parser.

Create missing menus or refresh existing ones with `python .github/workflows/build/documentation/markdown_structure.py --refresh-menus`; existing introductions, destinations, body content and dominant line endings are preserved. Exempt documents without a menu remain unchanged.

A folder-wide Deprecated/examples exemption also hid missing menus in maintained migration and runtime-example guides; those now require menus, with only the named short index/generated artifact exempt.

The Logging Inventory reached 55 headings without navigation because the earlier check only validated declared menus. The missing-menu regression now fails for arbitrary new document paths, while fixtures verify exemptions, hierarchy and repeatable generation.

#### `build/documentation/numbered_references.py`

Fails when a tracked text file writes a numbered reference with a space: a pull request is `PR#50`, a Known Issue `KI#1104` and a SASGameRecord revision `SGR210`, one token each, so one grep finds every mention. `--fix` joins them in place; `checks-documentation.yml` runs it as **Numbered references as one token**.

- Added on 2026-11-23, when the user found pull requests written both ways, 29 spaced against 5 joined, while `KI#` was never spaced in 21,972 uses; every tracked text file was converted, history copies such as the dev logs and the archived release notes included, since one grep is the point.
- The spellings live in [`lib/reference_spellings.py`](/.github/workflows/lib/reference_spellings.py), which [`squash_pr_number.py`](#buildrepositorysquash_pr_numberpy) applies to commit messages too.
- The oldest KIs were cited in words, "known issue" with "as of now", "number" or `#` before the number, on 129 lines of C++ and Python comments, XML, the Known Issues and the SAS dev log, so a grep for `KI#53.2.2` missed them; the same day they joined the table and became `KI#53.2.2` and the like.
  - Old Known Issues links that named a KI only by its number or its file and anchor, such as `[57 - title]` or `[README_Known_Issues.md#ki-24]`, were renamed `[KI#57 - title]` and `[KI#24]` by hand, as their anchors already pointed at the right entry; three that an earlier anchor conversion had mangled, such as `#ki-40-if-i-am-not-mistaken-but`, were repaired with them.
- Runtime revisions, such as `Runtime12`, are not listed yet: 4 of their 22 spaced uses sit in the Runtime subsystem's own sources, where a comment change needs a Runtime revision bump, so they can join with the next commit that bumps Runtime.
- `LLM_Helpers/context/`, other mods' material and the map scripts' originals, is not ours to respell.

#### `build/documentation/orphan_images.py`

Fails on an image (`.png`, `.jpg`, `.gif`, `.webp`, `.bmp`, `.svg`) whose file name no other text file in the repository names, as a Markdown or HTML embed, a link, a JSON list or a script string. It is the reverse of [`markdown_images.py`](#builddocumentationmarkdown_imagespy), which fails on an embed whose image is missing.

- The file name is matched rather than the path, in its plain and `%20` spellings, since scripts and tables name an image without its folder. Generated corpora and helper outputs (`LLM_Helpers/context/`, `LLM_Helpers/outputs/`) do not count, as they quote old names.
- It has no exemptions. The first run, on 2026-11-21, found 70: three SAS screenshots left out of the docs, now embedded in the root README; 52 base AdvCiv comparison shots, now shown with captions in the [legacy images page](/_0_Legacy/Images/README.md); and 15 other mods' game font previews, now in a table in the [Art Tools Guide](/_1_AdvCiv-SAS/Docs/Modding_Resources/README_Art_Tools.md#editing-with-game-font-editor).
- So a new image needs a place where it is named: an embed in the doc it illustrates, or a line in its folder's index.

#### `build/documentation/requires_version_markers.py`

Checks that a newly added `(Requires AdvCiv-SAS N+)` names the practical number, `git rev-list --count`, that its change lands at on main: on a push to main, each first-parent commit's own count, a merge commit's included; on a PR marked `[ci_squash_pr]`, the target branch's current count + 1, the squash commit's number.

- The number was written by hand and nothing checked it until 2026-11-22: one too high claims a version that lacks the change, one too low tells players of earlier versions they have it.
- Only a number that now appears more often in a file counts as added, so rewording, moving or deleting an entry passes; archived release texts under `changelogs_web/` are skipped.
- It reuses the revision checks' commit selection, so a feature-branch push is left to its PR, as theirs is.
- A PR not marked for a squash is left to the push on main: a merge commit's count is known only once it exists, which Codex's review found when a branch's `2+` passed on its PR and failed after the merge demanded `4+` (2026-11-22).

#### `build/documentation/retired_names.py`

Fails on a retired tool or feature name, such as SASSaveTransplanter's former plain-English name or SASPilot's early nickname, in any text file of the repository outside the history records.

- We rename old references retroactively, so agents meet only current names. The names come from the table in [`retired_names.md`](/_1_AdvCiv-SAS/Docs/Deprecated/retired_names.md), the single list, as the retired define and XML asset checks read theirs.
- Added on 2026-11-17: main's history had been rewritten that morning to give SASSaveTransplanter its name, yet the same day an agent wrote the old name twice in new text, in the dev-log check's comment and its README section, and only the user's review caught it.
- It reads tracked files and new untracked ones, so a local run also catches a file not yet added: its own first draft was missed that way.
  - [`retired_names.md`](/_1_AdvCiv-SAS/Docs/Deprecated/retired_names.md) and the check's test, which must spell the old names, are exempt.
- Each name has a **Checked** switch, `yes` or `no`, so one can be turned off while a branch that still uses it, such as SASPilot's own docs, catches up and can merge main without failing.
- Matching ignores case and takes whole words only, so a harbour's "pilots" do not match SASPilot's retired nickname. The list says why the nickname is listed as a whole phrase and not as the bare word.
- The dev logs, the `commit_diffs` corpus, archived changelogs, the `Deprecated` folder, the source-analysis records and the recorders' revision histories keep the wording of their time: they quote old commit titles and describe the renames themselves.

```bash
python .github/workflows/build/documentation/retired_names.py
```

#### `build/documentation/sas_source_guide.py`

Keeps SAS-branded mod source and shipped runtime companions discoverable in both the [root README](/README.md) and [Main Changes Guide](/_1_AdvCiv-SAS/Docs/README_Main_Changes_Guide.md), rather than describing features without naming their implementation files.

- Requires a visible filename in a Markdown link to the exact repository-root path. For example, [`SASGameRecordLog.cpp`](/CvGameCoreDLL/SASGameRecordLog.cpp) counts; a bare mention, a generic "implementation" link, a link to another file, or a commented/code-example link does not.
- Applies to tracked C/C++ source/header/export/resource, Python and XML files in gameplay folders (`CvGameCoreDLL`, excluding `Project`; `Assets/Python`; `Assets/XML`; `PrivateMaps`). Tools, tests, generated/untracked outputs, binaries and copied documentation are outside this scope.
  - Top-level shipped `Assets/*.ps1` and `Assets/*.cs` runtime companions are included too; limiting the original check to DLL/Python/XML had missed the screenshot observer.
- Recognizes uppercase `SAS` and lowercase underscore/hyphen branding tokens such as `GlobalDefines_advciv_sas.xml`, avoiding accidental matches such as inherited `StartPointsAsHandicap.cpp`.
- Ordinary runs check changed/added/renamed sources against the push/PR base, plus edits to either document that remove existing source links. Deleted source files are no longer required.
  - This preserves the clean baseline without reading every source file on every run; Git supplies the path inventory and only the two documents are parsed.
- Run a complete current-tree audit with `python .github/workflows/build/documentation/sas_source_guide.py --all`; updating the checker itself or lacking a comparison base also audits the full scope. Normal local review uses `--base-ref HEAD`.
- Reports all missing references together and never inserts a bare file list automatically: links belong beside the relevant feature, with enough explanation to make them useful.

### EXE patches

Checks that keep the EXE patches' material where it belongs: the guide and `LLM_Helpers/exe_analysis/` stay out of player archives, and files that ship describe a patch's effect, not the EXE's internals. Both ran under Repository until 2026-11-12; the user asked for their own category, as the material they protect has its own folders.

#### `build/exe_patches/exe_internals_placement.py`

Fails when a file that ships to players describes the EXE's internals: a decrypted copy of the EXE, Ghidra or its `FUN_` names, a code cave, or an EXE code address outside `CvGameCoreDLL/`, whose patch code needs them. Such details belong in the export-ignored EXE patches guide and `LLM_Helpers/exe_analysis/`; shipping files describe a patch's effect and link to the guide.

- Added on 2026-11-12, when the user's review found these details had spread into shipping files: a Known Issues paragraph on the globe patch's code cave, and notes in the Game Runs guide, the UI map generator and `SelfMod.cpp` comments. [`exe_patches_export_ignore.py`](#buildexe_patchesexe_patches_export_ignorepy) checked only that the guide stays export-ignored, not what other files say.
- Files under export-ignored folders such as `.github/` count as not shipping; inherited `_0_Legacy/` copies are skipped, since AdvCiv's manual quotes its own, already public, patch addresses.
- In `CvGameCoreDLL/`, lines of another mod's comment quoted as is (`// >`, under a line saying it is a quote) are allowed, such as Realism Invictus's notes naming Ghidra's `FUN_` functions: that text is already public in that mod's DLL source, and rewording it would blur whose finding it is.

#### `build/exe_patches/exe_patches_export_ignore.py`

Fails if the [EXE patches guide](/_1_AdvCiv-SAS/Docs/Modding_Resources/README_EXE_Patches.md), its `LLM_Helpers/exe_analysis/` helpers, or the files describing them (`AGENTS.md` and `.github/`) lose their `export-ignore` in `.gitattributes`.

- They stay in Git and the light-source ZIP for agents but out of player and GitHub Download ZIP archives, and only those `.gitattributes` lines keep them out; on 2026-11-12 the user asked for this check so a deleted line cannot pass unnoticed. The [`folder_indexes.py`](#builddocumentationfolder_indexespy) exception keeps what does ship to a link.
- It asks Git for each path's effective attribute. Folders are queried with a trailing `/`: `git check-attr` reported `.github` as unspecified but `.github/` as set, since `/.github/` matches directories only, while `git archive` still skipped the whole folder.
- A listed path that no longer exists fails too, so a move cannot silently drop the check; update `REQUIRED` in the script then.

```bash
python .github/workflows/build/exe_patches/exe_patches_export_ignore.py
```

### Hygiene

#### `build/hygiene/control_characters.py`

Rejects stray control characters (NUL, BEL, form feed and other C0 control bytes except tab, line feed and carriage return, plus DEL) in tracked and untracked text-format files.

- It reports the file, line and a readable escape of the surrounding text.
- Binary formats such as `.lnk`, `.ani` and `.chm` legitimately contain such bytes and are not scanned.

- While documenting new legacy image names, text written through a PowerShell double-quoted string had `` `0 `` become a NUL byte in `AGENTS.md` (`0.610_tech_tree_...`, `0.611_tech_tree_...`) and `` `a `` become a BEL byte in this README (`` `advisors` ``).
  - Markdown structure, prose and line-ending checks passed; VS Code only showed red NUL markers.
  - A repository-wide scan found no other text file affected; this check keeps it that way.
- PowerShell double-quoted strings also silently drop a backtick before most other characters (`` `_web` `` became `_web`).
  - Prefer single-quoted strings or here-strings when generating Markdown with backticks.
- Form feed was allowed at first, as an old page break, though no text file held one. On 2026-11-13 text written through Claude Code's Bash lost backslashes, so `\find.exe` became a form feed and `ind.exe` in the Makefile and in this README, four slips in one session, and this check passed each time. It now rejects form feed too, and scans `.tsv`. See KI#38.7.

#### `build/hygiene/line_ending_churn.py`

Fails when a commit switches a file's line endings between LF and CRLF, so that lines whose text did not change show as changed.

- `line_endings.py` catches a file with mixed endings, but a file switched whole has none, so it passed. Its diff then hides the real change: on 2026-11-17 a commit showed 3,481 changed lines in this README for 23 real ones, and only the user's eye on the line count caught it. See [KI#1097](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#ki-1097).
- Per file, it compares the commit's changed lines with Git's count ignoring line endings (`--ignore-cr-at-eol`); 20 or more lines that differ only there fail. Removed or rewritten lines count in both, so they never trip it.
- A deliberate conversion passes with `[ci_convert_line_endings]` in the commit message. Commit selection is shared with `dll_commit_message.py`.
- Replayed over all of SAS's 2,815 commits, it found 82 files in 56 commits, most from March to May 2026 and only 4 after `line_endings.py` arrived, besides the two README switches already removed by rewriting history. The same command audits any range: `--base-ref <commit> --head-ref main`.

```bash
python .github/workflows/build/hygiene/line_ending_churn.py
```

#### `build/hygiene/line_endings.py`

Verifies active text-like source/config/docs files do not mix CRLF and LF line endings within the same file and that non-empty files end with a newline. This is intentionally a reporting/fail-fast build check only; for local reviewed cleanup, use [`LLM_Helpers/formatting/fix_line_endings.py`](/LLM_Helpers/formatting/fix_line_endings.py).

Since 2026-11-17 it also fails a text file stored with the wrong endings, LF or mixed for the CRLF kinds and CRLF or mixed for all other text.

`.gitattributes` keeps theme, batch and Visual Studio files CRLF (`-text`) and all other text LF, one style per kind, stored and checked out alike. The check reads Git's own report, `git ls-files --eol`, so a Windows checkout's CRLF working files do not make it fail locally only.

Since 2026-11-25 it also fails a tracked text file that Git stores LF but that is CRLF or mixed on disk, from the same report's working-file column, as Python's `write_text` leaves a file rewritten on Windows.

- Git converts such a file back when staged, so commits stay clean, but an exported diff showed it ([KI#1097](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#ki-1097)).
- It can fire only locally, as a fresh checkout follows `.gitattributes`.

A file switched whole between LF and CRLF has no mixed endings and passes here; [`line_ending_churn.py`](#buildhygieneline_ending_churnpy) catches it per commit. See [KI#1097](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#ki-1097).

Generated/reference helper folders such as `LLM_Helpers/outputs` and the verbatim `LLM_Helpers/context/mapscript_refs` and `LLM_Helpers/context/commit_diffs` corpora are excluded to avoid noise or rewriting downloaded originals.

The script prints its scan mode. In a normal Git checkout it lists tracked files with `git ls-files` and checks the current checked-out bytes. In a plain exported folder, such as an extracted light-source zip without `.git`, it falls back to scanning the configured active source/doc folders directly.

Before the first cleanup, this checker found 79 local worktree issues, while GitHub Actions reported only 19. Comparing local bytes with `git show :path` showed that some local mixed-EOL files were clean LF-only in Git's indexed blob (e.g., `BugInit.py`) while true CI failures stayed mixed in both (e.g., `Pangaea.py`).

Fixing all local findings updated 78 worktree files, but staging kept only the 19 stored-content changes that Git/CI saw. This makes local output useful cleanup/export guidance, while staged/GitHub output is the authoritative committed-content failure set.

Note: later on, we noticed a line endings test failed locally:

```log
FAIL text line-ending hygiene
  - .github/workflows/build/runtime/aip_predump_values.py: has mixed line endings: CRLF=560, LF=2, lone_CR=0
  - Assets/Python/Contrib/Sevopedia/SevoPediaLeaderAIPValues.py: has mixed line endings: CRLF=485, LF=1, lone_CR=0
  ```

The LF-only lines are just blank lines:

```log
.github/workflows/build/runtime/aip_predump_values.py
  LF-only line 393
  LF-only line 440

Assets/Python/Contrib/Sevopedia/SevoPediaLeaderAIPValues.py
  LF-only line 334
```

But it passed on [GitHub Actions test](https://github.com/wonderingabout/AdvCiv-SAS/pull/29/commits/c0e4c7624edafb022946267c606692071784dbf0): GitHub Actions checks its own post-checkout bytes, so local/exported mixed line endings can still need cleanup even when CI passes. When this happens in a Git checkout, the script notes failing worktree files that are already clean in the Git index.

To make this clearer, the checker now prints its scan mode and can note when a failing worktree file is already clean in the Git index.

#### `build/hygiene/repository_hygiene.py`

Rejects UTF-8, UTF-16 and UTF-32 BOM signatures in Git-tracked files, including inherited references. Visual Studio `.sln` and `.vcxproj` files may retain UTF-8 BOMs for launcher compatibility; UTF-16/32 BOMs remain rejected everywhere.

For example, `CvGameCoreDLL/Project/AdvCiv.sln` and `AdvCiv.vcxproj` already contain UTF-8 BOMs in the unmodified `AdvCiv_base_1.14_renamed` comparison snapshot. Their inherited BOMs are preserved after the SAS project shortcut stopped opening following their removal.

It also checks installed file paths against the standard Steam Civ4 `Mods/AdvCiv-SAS` anchor: at most 259 UTF-16 units for a file path, and 247 for parent directories. The default mod-folder name is derived from the repository root. `--install-root` can validate another installation path or longer mod name.

Filenames, including extensions, are limited to 56 UTF-16 units as a repository maintenance policy, not a Windows component limit. The existing 52-unit `Gilgamesh__gilgamesh_parent_action_02_affirmative.kf` provided the baseline for this choice; 56 adds four units of leeway while leaving descriptive names and installation-path headroom.

Its exact name is referenced inside `Gilgamesh.kfm`, so a file-only rename would break that reference.

When introducing this limit, eight music files and one example shortcut were shortened; the music XML paths were updated while original download links and credits were preserved. The checker scans every tracked file and reports all violations before failing.

Binary assets are inspected only for a leading encoding signature, without decoding their contents.

#### `build/hygiene/text_blank_lines.py`

Rejects newly introduced excessive blank separators in maintained configuration, build scripts and plain-text documentation. Source C++/Python/XML already use the source-provenance check, and Markdown uses markdownlint; all share the same intent of preventing patching leftovers without flattening meaningful text.

- Allow one blank separator in Git/configuration formats and prose text; allow two in build-script/code formats such as Makefiles, `.inl`, `.rc`, PowerShell and shell scripts.
- Preserve string literals, YAML block scalars, shell/PowerShell here-documents, Makefile `define` bodies and archived `Long_Comments` payloads. Frozen history, imported references/assets and captured examples retain their original layout.
- `--all` audits the current scope for an initial cleanup. Normal CI examines only changed files and reports newly introduced runs, including gaps created by deleting a block between two separators; inherited runs becoming shorter do not fail.

The initial sweep removed leftover separators from the Makefile/resource script and the `Long_Comments` introductions. Recorded text remained intact. Source and supplementary checks reuse `lib/blank_lines.py` for literal protection and blank-row ancestry, avoiding divergent implementations.

```sh
python .github/workflows/build/hygiene/text_blank_lines.py --all
python .github/workflows/build/hygiene/text_blank_lines.py --base-ref main
```

### Python compatibility

#### `build/python/python24_compile.py`

Compile-checks runtime Civ4 Python files under `Assets/Python` and `PrivateMaps` with CPython 2.4 through [`python24-compile.yml`](/.github/workflows/python24-compile.yml). It uses `py_compile` on each source file but redirects bytecode to a temporary directory so the workflow catches real Python 2.4 parser/bytecode errors without writing `.pyc` files into the mounted repository.

This check complements Ruff: Ruff gives modern static diagnostics, while this workflow confirms the old parser still accepts the files Civ4 can load.

#### `build/python/star_import_names.py`

Fails on a name in `Assets/Python` or `PrivateMaps` that Ruff reports as F405, "may be undefined, or defined from star imports", but that nothing provides: none of the file's star-imported repository modules, recursively, nor a Python 2 built-in, a Python 2 exception target in its handler, or an engine export resolved from a BUG API class heading, a DLL binding or the checked list. It runs in [`python-ruff.yml`](/.github/workflows/python-ruff.yml), which installs Ruff.

- Ruff cannot know what `from CvPythonExtensions import *` provides, so a typo there is F405 rather than F821, and the Ruff gate ignores F405, as nearly every Civ4 name arrives that way. [KI#165.2](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#ki-165.2)'s `religionList`, an undefined name from vanilla on, went unseen until 2026-11-22.
- An engine name the reference lacks, such as WorldBuilder's `getWBToolEditTabCtrl`, goes on the script's `ENGINE_NAMES` list only once checked, as a typo added there would hide the next one.

### Repository

#### `build/repository/adjacent_duplicate_lines.py`

Rejects a code line that a commit adds when it repeats the line right above or below it, indentation included, in Python, C++ and PowerShell files.

- Such doubles come from a merge resolution keeping both sides, a script run twice or a paste, and the code still runs, so nothing else catches them. The review on 2026-11-18 found three: `SevoPediaMusic.py` set the same label twice, and the inherited `CvDanQuayle.py` and `CvCustomizableDomesticAdvisor.py` assigned or hid the same thing twice.
- Only added lines count: across the tracked code, 114 lines repeat their neighbour, most on purpose, such as two `NEWLINE` appends for a blank line or matrix rows in map scripts. A deliberate double can say so with a trailing comment, which makes the lines differ.
- Lines of only brackets, separators or comment rules are not counted, nor XML, which repeats rows on purpose, nor test folders, whose harnesses call a function twice to prove the second call changes nothing. Line-ending-only changes are ignored, so a conversion does not count every line as added.
- Replayed over the last 400 commits of main, saspilot and sassavetransplanter, it flags none. Commit selection is shared with `dll_commit_message.py`.
- [KI#1098](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#ki-1098) traces where each of the three doubles came from.
- The same check also rejects newly duplicated literal C++ includes, including non-adjacent headers and duplicates added by a merge. It reports both lines when the directives share a preprocessor arm or one is in an enclosing scope.
  - Existing duplicates and includes under separate conditional groups are outside the comparison. See [KI#1098.2](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#ki-1098.2).

#### `build/repository/assets_dlls.py`

Recursively verifies that `Assets` contains only the one shipped game-core DLL, `Assets/CvGameCoreDLL.dll`. This catches accidentally committed backup, test, Debug-opt, or other DLL variants anywhere under `Assets`.

#### `build/repository/commit_trailers.py`

Rejects a `Co-authored-by:` trailer for anyone not listed in its `ALLOWED_CO_AUTHORS`, as of now only Dependabot, which authored its own action bumps and may share a squashed PR. Agents already credit themselves in the code comments they write, so a trailer on every commit only adds noise.

- On 2026-11-16 Claude Code added one by default to two commits despite the user's rule, and both had to be amended.
- It lists allowed co-authors rather than agents to reject, since a list of agents would miss the next one that adds a trailer by default, while the maintainers are few. Names are matched before the `<`, so no email address is kept in the check; add a new maintainer or bot there.
- A credit written inline in the body, where it says something, stays allowed, such as `e8659a5e4`'s note on GPT-Codex-5.2; only a line starting with the trailer is checked.
- Commit selection is shared with `dll_commit_message.py`: the pushed or PR commits in CI, `HEAD` locally.

For example, the KI#1082.2 commit first ended with this trailer:

```text
- The shipped Release DLL is not updated: only command-line scenario launches show the issue.

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
```

The check reported it as:

```log
FAIL commit 6687872bba1a has a Co-authored-by trailer for Claude Opus 5.5, who is not in ALLOWED_CO_AUTHORS; credit agents in their code comments, or inline in the message where it matters; title was: Fix SAS's main menu setup screens EXE patch leaving a /FXSLOAD scenario's Civilization step in BtS's small box (KI#1082.2)
```

The amended message just drops the trailer. Agents are already credited plenty in the comments they write, such as `(Claude code Opus 5.5)`, so a message names one only now and then, inline where it helps or is intended, for example "found while Claude Code Opus 5.5 replayed the push range".

Dependabot's trailer passes:

```text
Co-authored-by: dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com>
```

```bash
python .github/workflows/build/repository/commit_trailers.py
```

#### `build/repository/dev_logs.py`

Keeps the dev logs' hand edits, anonymized authors and commits in the branch's history: `_0_Legacy/Docs/dev_logs/` and `_1_AdvCiv-SAS/Docs/dev_logs/` hold one log per mod, newest first.

- The logs are hand-edited copies of `git log`. On 2026-11-17, 650 of the SAS log's 2,420 entries, 8 of base AdvCiv's 3,094 and 3 of K-Mod's 1,249 differed from Git's own messages, with typo, churn and wording fixes such as "LLM/AI helpers" becoming "AI/LLM helpers".
  - A naive regeneration with `git log` would erase them all, so a commit that changes a dev log must keep its earlier content as the exact tail of the new one: new entries go on top.
  - A deliberate edit of earlier entries, such as a typo fix, passes when the commit message contains `[ci_edit_dev_log]`, as `[ci_update_dll]` does for the DLL.
  - Deleting a log fails. A moved log is followed to its earlier path, even when the move and a large prepend together fall below Git's rename similarity, by pairing logs with the same key after `anonymized_email_`, such as `003_AdvCiv-SAS.txt`.
- Every `Author:` line must be `<hidden>`, as the `anonymized_email` file names promise.
  - Addresses inside message bodies stay as their commits wrote them, such as agents' and bots' `Co-authored-by: GPT-Codex-5.2 <codex@openai.com>` or Dependabot's `Signed-off-by`. They are not personal, and replacing them by hand would be brittle, as more come with new commits.
- Every logged commit must still be in the checked branch's history, so a history rewrite cannot leave the log citing SHAs that no longer exist there.
  - On 2026-11-17 main was rewritten twice, to give SASSaveTransplanter its name in older commits and to reword KI#1091's message. Both times the SAS log ended just before the rewritten commits, but a rewrite reaching further back would have left it stale without any failure.
  - After such a rewrite, replace the old SHAs in the log with the new ones from the rewrite's old-to-new map, keeping the entries' hand edits, and put `[ci_edit_dev_log]` in the commit message.
  - The CI checkout fetches the full history (`fetch-depth: 0`), so a missing commit means it left the history, not that the clone was shallow.
- Commit selection is shared with `dll_commit_message.py`: the pushed or PR commits in CI, `HEAD` locally.
- Added on 2026-11-17, while the SAS dev log was brought up to date from practical 6402 to 6763; the check first confirmed that the committed log survived as the exact tail of the new one.

```bash
python .github/workflows/build/repository/dev_logs.py
```

#### `build/repository/dll_commit_message.py`

Local test DLLs have accidentally been committed with source work, including a Debug-opt build replacing the intentionally shipped Release DLL. Source changes and local test builds happen more often than deliberate distributed Release DLL updates.

A changed installed DLL should therefore remain unstaged unless its inclusion is intentional.

The commit-message marker makes that decision explicit and catches accidental binary staging in CI. CI runs after pushing; it does not stop local staging or Git pushes, so inspect the staged file list before committing as well.

Requires the exact, case-sensitive marker `[ci_update_dll]` in the title or body of every checked commit that adds, modifies, deletes or renames a tracked `.dll` file anywhere in the repository. The extension is case-insensitive.

For example, use `- [ci_update_dll]: install the tested Release build` in the commit body. Source-only commits need no marker. With the reporting wrapper present, changing either a DLL or its `<DLL filename>.build.json` requires both paths to change in that same commit; `[ci_update_dll]` without a changed pair also fails.

A later marked commit cannot excuse an earlier unmarked DLL update; each message is checked separately. Merge commits are compared against their first parent, and root commits include additions.

- Only the first-parent chain of a push or pull request is judged, so commits that arrive through a merge are not. The base AdvCiv 1.14 merge (2026-11-19) brought in upstream commits such as `5970334b6` that update their DLL without SAS's marker; the merge commit itself still needs the marker for the DLL it ships.

On pushes, inspect all commit identities supplied by the GitHub push event and read the actual paths/messages from Git. This avoids depending on a discarded push-before object after an amendment.

If the payload may be truncated, require the complete Git range instead; missing history produces a clear failure rather than silently passing.

On PRs, inspect commits reachable from the PR head but not its base, using the actual head SHA rather than GitHub's synthetic merge commit. Manual/local runs check the selected head commit by default.

The repository workflow keeps complete commit/tree history with `fetch-depth: 0` and `filter: blob:none`, while checkout materializes the selected revision's files.

Historical blobs are omitted initially. Intent checking needs only messages/tree paths; build-report checking fetches the reports and changed DLL bytes needed for the selected commits, rather than downloading every historical asset version.

For commits containing the automatic `CvGameCoreDLL/Project/build_with_report.ps1` wrapper, each added/modified DLL must also have its full `<DLL filename>.build.json` in that same committed tree. Earlier commits predate this prospective requirement; they retain the existing intent check.

- The wrapper keeps one current full JSON report beside the DLL and its full `AdvCiv.log`; there is no separate compact format or automatic timestamped archive. Normal build outputs stay Git-ignored.
- Copy/stage the full JSON with an intentionally shipped Release DLL; keep the full log locally. The report retains Git/debug context, timings, diagnostics, temporary-artifact state and DLL hashes; the local log preserves all emitted compiler output, including uncoded messages.
- The guard requires a successful Build/Rebuild with configuration exactly `Release`, zero exit/error status, ordered UTC timestamps, nonnegative duration/diagnostic counts, size/SHA-256 matching the committed binary.
  - Warning counts must also be zero: successful compilation can still emit warnings that need addressing before shipping. CI checks the diagnostics captured by the report; it does not rerun the compiler.
- Every current push/PR/manual head must retain the shipped `Assets/CvGameCoreDLL.dll` and its matching successful Release JSON, even if only source/docs changed. Missing, stale or deleted evidence fails; local uncommitted copies do not count.
- Pair enforcement includes additions, removals and renames. Git compares file bytes: a byte-identical rebuilt DLL is unchanged, so its refreshed JSON cannot be committed alone.
- Historical DLL deletions need no per-commit build evidence. A later report or an uncommitted local file cannot satisfy an earlier binary-changing commit; the current shipped-DLL requirement is checked separately at the head.
- This is a consistency guard against accidental staging, not authenticated proof of compilation or source reproducibility. The recorded Git SHA is pre-build context, not necessarily the final shipping commit when source was uncommitted.

GitHub documents its [push payload and commit-array limit](https://docs.github.com/en/webhooks/webhook-events-and-payloads#push).

This is an explicit-intent marker, not proof that a DLL was compiled in Release mode, corresponds to the current source or was authorized by the user. Preserve the existing rule that compiled binaries require explicit user approval.

When a squash or merge introduces a DLL, its resulting commit message must also contain `[ci_update_dll]`; CI checks that committed message on push. This intent check does not rebuild DLLs or install a local hook; the structural define check below separately covers DLL-consumed XML define name changes.

```sh
python .github/workflows/build/repository/dll_commit_message.py
python .github/workflows/build/repository/dll_commit_message.py --base-ref HEAD~3 --head-ref HEAD
```

#### `build/repository/dll_define_changes.py`

Adding, removing or renaming an XML define consumed by C++ requires an updated shipped Release DLL when integrating into the repository's default branch. The default branch comes from GitHub metadata, so renaming it does not require changing this rule.

- Discover `DefineName` declarations throughout `Assets/XML/**/*.xml`, regardless of filename or name prefix, and compare their combined name sets against each selected commit's first parent; inspect both C++ source trees for those names, ignoring comments.
- Moving an unchanged name between XML files, value/comment edits and Python-only define names require no rebuild. This is a conservative static reference check; dynamically constructed names and preprocessor reachability are not resolved.
- Feature-branch pushes defer enforcement. PRs targeting the default branch and default-branch pushes require the integration head's DLL to differ from the binary before each affected change, with matching successful Release JSON evidence.
- Intermediate source commits can share a later Release build at the integration head; each binary-changing commit still needs its own `[ci_update_dll]` marker and build evidence under the existing intent check.
- Local/manual runs check the selected head commit; `--base-ref` checks a complete range. Amended pushes inspect the new commit identities without relying on a discarded push-before object.

The DLL rebuild check sends the changed define names to Git as input rather than hundreds of command-line arguments. This avoids Windows' command-length limit while preserving literal, whole-name matching; the complete KI#1001.2 rename set exposed that limit.

This catches an unchanged shipped DLL after structural define changes. It does not compile source or prove that a changed binary contains every source edit; review and a current Release build remain necessary.

```sh
python .github/workflows/build/repository/dll_define_changes.py
python .github/workflows/build/repository/dll_define_changes.py --base-ref HEAD~3 --head-ref HEAD
```

#### `build/repository/dll_python_bindings.py`

Adding a Python method/function call alongside an old DLL can break startup or game loading even when Python syntax checks pass. This guard catches changed literal Boost.Python class-method and module-function registrations in `CvGameCoreDLL/**/*Interface*.cpp` and requires matching Release build evidence at default-branch integration.

- Compare `.def("name", target, ...)` and `python::def("name", target, ...)` names and target expressions against each selected commit's first parent; additions, removals and retargeting require a changed shipped DLL. Comments, help strings, whitespace, registration ordering and moves between interface files do not trigger a rebuild by themselves.
- Reuse the existing successful Release report/binary checks, then verify affected registrations against `buildInputsBefore`. An exact source hash matches directly; otherwise the captured `pythonBindingsSha256` fingerprint of names/targets must match, so later comments, reflow or help-string edits do not require another compile. Stale registrations still fail.
  - Build reporting retains exact source hashes for provenance and separately fingerprints literal bindings without requiring Python on the build machine. Reports without that fingerprint still need an exact source match, accepting Git LF or Windows CRLF.
- Like structural XML define changes, intermediate feature-branch commits may remain source-only. Default-branch pushes and PRs require the matching pair at the integration head; existing per-commit DLL intent rules still apply.
- Scope is explicit literal method registrations, not a complete C++/Python compatibility analysis: class/enum/property registrations, macro-generated or computed names, target-signature changes without registration edits, trailing policies/argument metadata and Python callers are not checked.

The guard does not compile or run Civ4, authenticate a report or prove that all native implementation files match. Compilation, runtime testing and review remain necessary.

```sh
python .github/workflows/build/repository/dll_python_bindings.py
python .github/workflows/build/repository/dll_python_bindings.py --base-ref HEAD~3 --head-ref HEAD
```

#### `build/repository/dll_runtime_revision.py`

When a default-branch integration ships a DLL alongside native Runtime changes, this check verifies the Release report's source manifest against each changed dedicated `SASRuntime*.cpp` / `.h` file. It accepts Git LF and build CRLF line endings.

Runtime and SGR can both land source-only changes while the shipped DLL remains suitable. The structural-define and Python-binding rebuild guards still apply. Review observer changes for dependencies on new DLL behavior before deciding whether the shipped binary needs an update.

`SAS_RUNTIME_REVISION` is an XML implementation label. Use DLL/build/source identities to identify the native code actually loaded.

```text
python .github/workflows/build/repository/dll_runtime_revision.py
python .github/workflows/build/repository/dll_runtime_revision.py --base-ref HEAD~2
```

#### `build/repository/examples_archive_size.py`

Keeps compact documentation examples in archives while requiring manual review when an included example file or folder grows beyond **1 MB (1,000,000 bytes)**.

- Checks tracked files under `_1_AdvCiv-SAS/Docs/examples/`; measures uncompressed file bytes and sums included descendants for every folder, including the examples root. Exactly 1 MB is allowed.
- Uses Git's effective `export-ignore` attributes, including parent-directory exclusions. Excluded captures do not inflate their parents' included totals; untracked local captures are outside the check.
- Reports all oversized files/folders together and fails. Review their usefulness, then reduce included content or add appropriate archive exclusions in `.gitattributes`; the check does not edit that file automatically.

```bash
python .github/workflows/build/repository/examples_archive_size.py
```

#### `build/repository/future_dates.py`

Rejects a date that a commit adds when it is later than the commit's own date, taken in the committer's time zone.

- On the evening of 2026-11-16, Claude Code took 2026-11-17 from its session's date instead of the local clock. Two commits added it to an AGENTS.md example, a KI entry, three check comments and two notes in this README before the user noticed.
- Only added lines count, so old text is never judged again. Generated history under `LLM_Helpers/context/` is skipped, since it quotes other commits' dates, and so are test folders, whose fixtures make up dates on purpose.
- The committer date decides, so an amend after midnight may add the new day's date.
- Commit selection is shared with `dll_commit_message.py`: the pushed or PR commits in CI, `HEAD` locally.

For example, a replay of those two commits reported:

```log
FAIL commit d387f6b148dd adds 2026-11-17 to AGENTS.md, after its own commit date 2026-11-16; take dates from the local clock or the commit date, not a session's date: - Example: two titles a few days apart. "Record peer Civ4 clients in SASGameRecord…" (SGR200, KI#38, 2026-11-11) was a real record, as SGR began logging those clients. "Record
```

```bash
python .github/workflows/build/repository/future_dates.py
```

#### `build/repository/ki_commit_titles.py`

Requires a commit that adds Known Issues to name them, so the commit that opened an issue can be found from its number. Most titles already did, such as `(SGR194, KI#203.2)`, but commits adding two or three KIs mostly named them only in the body, if at all.

- New KIs are found by their `<a id="ki-N">` anchors; an entry only moved or renumbered within the file is not new, and editing an existing KI needs no mention.
- Up to three new KIs must each be named in the title. More, as in audit reconciliations that added up to 33 at once, may be named anywhere in the message, and a range such as `KI#1036-KI#1068` names whole-number KIs in between.
- `KI#1076` is not satisfied by `KI#1076.2` or `KI#10760`.
- A KI named before its entry exists is allowed, on purpose (2026-11-23).
  - The KI#11.3 commit named KI#1105, whose entry the user had not finished, and the user's VS Code showed `#1105` as a link to issue #1105 of the upstream AdvCiv repository, which this clone has as its `upstream` remote. GitHub shows it as plain text.
  - A rule failing a message that names a KI with no entry was tried: over all history it flagged only that commit. It led to describing the issue in words instead, which the user found worse than the number, since a grep for `KI#1105` then misses it; the link came from the viewer, not from the text, so the rule was reverted before the push.
- Commit selection is shared with `dll_commit_message.py`: the pushed or PR commits in CI, `HEAD` locally.

```bash
python .github/workflows/build/repository/ki_commit_titles.py
```

#### `build/repository/makefile_windows_tools.py`

Fails when the DLL Makefiles call a tool that both Windows and Git ship under the same name (`find`, `sort`, `expand`, `tar`, `timeout`, `whoami`) without its `System32` path, or contain a control character other than tab and line ends.

- Added on 2026-11-13: a bare `FIND` in the build provenance step resolved to Git's Unix `find` when a build inherited Git Bash's `PATH`, and crawled all of C: while the build waited.
  - It happened on 2026-11-11 and again on 2026-11-13 despite the [DLL Compilation Guide](/_1_AdvCiv-SAS/Docs/Modding_Resources/README_DLL_Compilation.md)'s rule against Git Bash, so the Makefile now names `%SystemRoot%\System32\find.exe` and this check keeps it so. See [KI#38.7](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#ki-38.7).
- The control-character test came from the fix itself: written through a shell, `\find.exe` became a form feed and `ind.exe`, which the name test could not see. Writing this README entry through the same shell then did it again; the Edit tool, which no shell touches, put it right.

#### `build/repository/project_sources.py`

Checks that root `CvGameCoreDLL/*.cpp` and `*.h` files appear under the matching `ClCompile`/`ClInclude` project entries, and reports stale or misclassified root entries. NMake discovers sources independently, so a successful build does not prove that files are visible in the VC2010 IDE. Project-local resources and nested generated files are excluded.

#### `build/repository/release_upstream.py`

When a numeric release tag is pushed or a GitHub release is published, the check fetches the tip of the highest-numbered base AdvCiv release branch directly from upstream. The tagged commit must contain that tip in its Git history.

- If upstream advertises multiple branches at the same highest version, the check requires their tips.
- Ordinary branch pushes and technical anchor tags do not trigger this workflow.

Run the same check before tagging a candidate.

```sh
python .github/workflows/build/repository/release_upstream.py --release-ref HEAD
```

#### `build/repository/squash_message.py`

Lists what a squash merge's commit message must contain, and with `--message FILE` checks a drafted one: the title names its PR as `PR#50`, and each revision the PR bumps, such as `SGR210`, and each KI it opens; the message keeps `[ci_squash_pr]`, and carries `[ci_update_dll]` when the PR ships a DLL.

- Those rules read the squash commit's own message, which exists only once the PR is merged, so before this they failed on the push to main, after the merge; on 2026-11-22 the title drafted for PR#50 lacked SGR210.
- On a PR marked `[ci_squash_pr]` it shows the list as a warning on the PR page; locally, run `python .github/workflows/build/repository/squash_message.py --message FILE` on the drafted message before merging.
- The PR reference and the marker were added on 2026-11-23: PR#50's drafted message, pasted over GitHub's own title and body, which lists the PR's commit messages with their marker, lost both; its squash commit, first pushed without them, was rewritten on 2026-11-23 to carry them and this check. On a PR the number comes from the event; locally pass `--pr N`, or any `PR#N` passes.
  - GitHub's own title ends with a bare `(#50)`, which does not say what the number counts; a PR is named `PR#50`, one token as `KI#1104` is, and a spaced reference fails, as [`build/documentation/numbered_references.py`](#builddocumentationnumbered_referencespy) explains.
  - [`build/repository/squash_pr_number.py`](#buildrepositorysquash_pr_numberpy) checks the same title on main after the merge.
- It reuses the revision readers, the KI anchor rule of `ki_commit_titles.py` and the marker spellings, so it cannot drift from the checks that judge the squash commit.
- It compares the target branch with the tree the squash would commit, from `git merge-tree`, so changes the target already has, such as a cherry-picked entry, are not asked of the squash message; `requires_version_markers.py` does the same, while the DLL check still compares the PR's merge base with its newest commit (2026-11-22).

#### `build/repository/squash_pr_number.py`

On a push to the default branch, and locally on `main`, fails when a commit carrying `[ci_squash_pr]`, the marker a squash commit keeps from its PR, does not name its PR in its title as `PR#50`; GitHub's bare `(#50)` does not count.

On any branch, it also fails a commit message writing a numbered reference with a space, by the table [`numbered_references.py`](#builddocumentationnumbered_referencespy) uses. `checks-repository.yml` runs it as **Squash commits name their PR**.

- Added on 2026-11-23, after PR#50's squash commit lost both its PR reference and the marker to a drafted message, so `git log` and the dev logs no longer led back to the PR's page; that commit was then rewritten to carry both and this check, and [`squash_message.py`](#buildrepositorysquash_messagepy) asks a draft for both before the merge.
- A PR's own commits carry the marker without a number, so PR runs and pushes to other branches are not checked; a commit without the marker, such as a rebase-merged Dependabot commit, needs no number.
- It guards marked commits only: a squash whose message dropped both the number and the marker, as PR#50's did, leaves nothing to tell it from an ordinary commit, so the draft check is the guard for that case (Codex's review, 2026-11-23).
- The title is read as Git's subject, the message's first paragraph joined, and only a positive number such as `PR#50` passes.
- It checks only the commits of each push.

#### `build/repository/temp_files.py`

Verifies that git tracks nothing under `CvGameCoreDLL/Project/temp_files/` and that the only `temp_files` rule in `.gitignore` or `.gitattributes` is the `.gitignore` line ignoring the whole folder.

It used to fail on any local target folder except `Debug-opt`, as a reminder to delete stale intermediates. Since 2026-11-11 `build_with_report.ps1` refuses a `BUILD` while the target folder holds files, and the whole folder is git-ignored, so local folders are left alone.

The same day the zero-byte `.gitkeep` that kept the folder in fresh clones for this check was dropped: the Makefile creates the folder when it is missing.

This helps catch stale fast-compile intermediates and forgetting to replace the committed DLL after compiling (see also [KI#38](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#ki-38) and [KI#38.2](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#ki-38.2)).

#### `build/repository/ui_map_sync.py`

Regenerates `LLM_Helpers/game_runs/ui_maps/civ4_ui_map.json` with `make_civ4_ui_map.py` into a temporary file and fails unless it matches the committed JSON, compared as text so line endings do not count.

- Until 2026-11-16 it compared bytes, so on a Windows clone with `core.autocrlf`, whose checkout writes CRLF while the generator writes LF, it failed on an unchanged JSON while GitHub's LF checkout passed. [`test_ui_map_sync.py`](/.github/workflows/tests/repository/test_ui_map_sync.py) checks that CRLF and LF copies pass and an edited copy fails, through `--map-json`.
- The JSON is generated: edit the generator, never the JSON. On 2026-11-12 an agent had edited the JSON directly, so rerunning the generator would have dropped the WorldBuilder mapping, as Codex's review found.
- The generator derives the Simple Game map list from the map scripts, through the same classifier as [`map_previews.py`](#buildassetsmap_previewspy), so a script added, removed or hidden from Simple Game also fails this check until the JSON is regenerated, with each row's point placed 24 px below the last.
- The generator itself fails when more scripts are shown than the 38 rows that fit at 1920 x 1080 without a scrollbar, since the list's points would then need re-measuring.

The repository workflow also runs [`json_format.py`](/LLM_Helpers/formatting/json_format.py) on the saved window positions and Sevopedia map. The same formatter writes those files, so integer coordinates stay together on one line. The check's error gives the command to reformat the file.

#### `build/repository/version_metadata.py`

Verifies the tracked `Assets/SASModVersion.txt` archive marker retains its Git `export-subst` version-anchor describe, commit, and commit-date placeholders, and that `.gitattributes` still marks the file `export-subst`.

The version placeholder uses one immutable `SAS_VERSION_ANCHOR_<exact-commit-count>` tag: Git's describe distance is the count of commits in `anchor..target`, so AdvCiv-SAS can reconstruct the same practical commit-count version in ordinary GitHub/git-archive downloads without a per-commit VERSION file.

The anchor is one-time repository infrastructure and must not be moved or renamed after creation.

#### `build/repository/workflow_keep_going.py`

Verifies that every check step of `checks-*.yml` keeps running after an earlier check fails, so one push reports every failure. A step added without that condition would otherwise be skipped after any earlier failure, and nothing would show it.

Whether a script itself collects all its findings is left to review: an audit of 95 scripts on 2026-11-09 flagged 25 by how they exit, of which about 6 really stopped early, so a check on it would mostly raise false alarms.

#### `build/repository/workflow_script_coverage.py`

Fails when a check script under `.github/workflows/build/` is not named by any workflow, so a new check cannot sit in the folder, pass locally and never run on GitHub. Shared helpers in `lib/` and modules whose names start with `_` are imported rather than run, so they are left out.

- Added on 2026-11-16, when `string_label_compares.py` had been written and run by hand but no workflow ran it; nothing failed, as `workflow_keep_going.py` only checks the steps that exist.
- Its documentation counterpart is in [`folder_indexes.py`](#builddocumentationfolder_indexespy), which now also fails when a check script has no section in this README.

### Runtime

#### `build/runtime/aip.py`

Verifies the Sevopedia Leader AI Personality Panel is enabled, uses the predumped cache by default, does not dump recomputed cache data to the log by default, and has a non-empty predumped cache file.

#### `build/runtime/aip_predump_values.py`

Validates effective AIP predump values outside Civ4. It compares committed entries in `Assets/Python/Contrib/Sevopedia/SevoPediaLeaderCachePredumped.py` against values reconstructed from `Assets/XML/Civilizations/CIV4LeaderHeadInfos.xml`, mirroring the narrow DLL path needed for these values: `LEADER_DEFAULTS` copy behavior, `CvLeaderHeadInfo::GetChildXmlValByName` missing-tag defaults, primitive array/list loading, and `UWAI::applyPersonalityWeight` with `UWAI_PERSONALITY_PERCENT`.

This script is intentionally separate from [`build/runtime/aip.py`](#buildruntimeaippy). `aip.py` remains the lightweight release-safety check, while this deeper value mirror checks the committed predump against effective XML+DLL-style values.

It currently checks full cached tuples for direct scalar getter keys, scalar attitude-threshold getters, flavors, no-war attitude probabilities, contact aggregate values, and displayed positive/negative memory aggregate values.

Contact and memory aggregate formulas are shared with the in-game AIP helper code; unit AI modifiers and improvement modifiers are not checked because they are not currently displayed/predumped.

The script fails by default when mismatches or missing/unparsed entries are found; use `--allow-mismatch` only for exploratory/debug runs such as `--no-uwai`.

Practical predump workflow:

1. The normal checker run reconstructs the expected AIP cache outside Civ4 and compares it with the committed `SevoPediaLeaderCachePredumped.py`. CI runs this automatically on commits/PRs, so a failure usually means the committed predump is stale relative to leader XML or shared AIP display logic.
2. The `Refresh AIP predump cache` workflow can refresh the predump from GitHub. It runs automatically after pushes to known AIP dependency files and can also be started manually from the Actions tab. When the generated file changes, it opens or updates a bot PR containing only `SevoPediaLeaderCachePredumped.py`.
3. To refresh locally without launching Civ4, run `python .github/workflows/build/runtime/aip_predump_values.py --write`, review the diff, then rerun the checker.
4. The old manual fallback still works: temporarily set `SAS_SEVO_LEADER_AI_CACHE_USE_PREDUMPED = 0` and `SAS_SEVO_LEADER_AI_CACHE_DUMP_TO_LOG = 1`, open the Leaders / AI Personality panel once, copy the generated `PythonDbg.log` block into `SevoPediaLeaderCachePredumped.py`, restore the defaults, and rerun this checker.

The generated file intentionally has no timestamp. This keeps no-op `--write` runs byte-identical when cache data is unchanged, avoiding false diffs and future bot/maintenance churn.

This full-tuple check is intentionally stricter than a raw-value-only comparison. During development, the earlier numeric-only check passed, but the tuple check found 394 stale predump entries after shared/runtime AIP label metadata had changed.

The underlying values were mostly correct, but many committed labels were missing updated `%` text, such as `Build Unit (52)` instead of `Build Unit % (52)`. Refreshing `SevoPediaLeaderCachePredumped.py` fixed those mismatches and confirmed that this check catches display-cache drift, not just numeric-value drift.

Example local commands (Git Bash):

```bash
cd "/c/Program Files (x86)/Steam/steamapps/common/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Mods/AdvCiv-SAS" && python .github/workflows/build/runtime/aip_predump_values.py
cd "/c/Program Files (x86)/Steam/steamapps/common/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Mods/AdvCiv-SAS" && python .github/workflows/build/runtime/aip_predump_values.py --write
```

#### `build/runtime/detail_manager.py`

Verifies `Assets/XML/Misc/CIV4DetailManager.xml` `CITYBILLBOARD_SCALE` keys match the committed shared UI font/default billboard-scale defines and the base values used by `Assets/Python/SASBillboardScale.py`, catching stale rewritten billboard scales after temporary UI upscaling.

#### `build/runtime/hands_free_defaults.py`

Requires the shipped values of the hands-free switches, which spare players clicks and manual steps, so players still get them.

- `SAS_UI_DAWN_OF_MAN_ON=1` keeps the Dawn of Man screen for players; [`toggle_dev_diagnostics.py`](/LLM_Helpers/README.md#toggle_dev_diagnosticspy) `on` sets it to `0` locally.
- The same holds since 2026-11-19 for the Greatest Civilizations screen (`SAS_UI_TOP_CIVS_ON`), whose ranking is recorded as a Timeline row either way.
  - And since 2026-11-27 for the tech splash and the era, wonder, religion and project movies (`SAS_UI_TECH_SPLASH_ON`, `SAS_UI_ERA_MOVIE_ON`, `SAS_UI_WONDER_MOVIE_ON`, `SAS_UI_RELIGION_MOVIE_ON`, `SAS_UI_PROJECT_MOVIE_ON`), first added on the SASPilot branch on 2026-11-13.
- The others are not changed locally, but one switched off by mistake would bring back what it removes: AI Auto Play's no-decision popups and its speed-scaled default turns, SASFastSave's start, end and autoplay-stop saves, scoreboard autocenter, and silent assertion handling (`SAS_ASSERT_SILENT_ACTION=1`).
- Like the diagnostic-default checks it accepts `--staged`, which the local CI runner uses.

#### `build/runtime/mapscripts.py`

Verifies every playable `PrivateMaps/*.py` script is listed exactly once across the SAS map-script heaviness/coverage defines, and every listed map script exists in `PrivateMaps/`. `SAS_MAP_SCRIPT_NAMES_HEAVINESS_UNSPECIFIED` is coverage-only and is not read by the DLL; it documents map scripts intentionally left outside the explicit land-heavy / almost-all-land / naval-heavy override lists.

#### `build/runtime/worldsizes.py`

Verifies hardcoded C++/Python `WorldSizeTypes` enum exposure matches the `Assets/XML/GameInfo/CIV4WorldInfo.xml` order, and that old `SAS_MAGIC_WORLDSIZE_*` Python runtime references have not returned.

### Shared helpers

Workflow checks import these modules to share parsing and repository logic.

#### `lib/advciv_release.py`

Recognizes base AdvCiv's release branches, named by version such as `1.14`, `v1.14` or `release-1.14.1`, and finds the newest one already merged into `HEAD`, as a local branch or a remote one such as `origin/1.14` on GitHub's full-history checkout or `upstream/1.14`. Versions compare number by number, so 1.10 follows 1.9.

- "Already merged" matters: base AdvCiv means the version SAS last merged, and a fetched `upstream/1.15` not merged yet would otherwise be taken for it.
  - Only whole branch names count, locally or on the `origin` and `upstream` remotes: Codex's review found the first draft let a branch such as `scratch/99.99` win.
  - A command that needs the ref and finds none, with no `--upstream-ref` given, stops with a clear message rather than a traceback, which Codex's review also asked for.
- Users:
  - [`inherited_files.py`](#buildsourceinherited_filespy) and [`history_lineage_tables.py`](/LLM_Helpers/README.md#history_lineage_tablespy) take their `--upstream-ref` default from it; they had `"1.14"` and `"upstream/1.14"` written in, so a newer AdvCiv would have needed edits (the user, 2026-11-22);
  - [`release_upstream.py`](#buildrepositoryrelease_upstreampy) and [`make_light_source_zip.py`](/LLM_Helpers/README.md#make_light_source_zippy) share its branch-name pattern, of which each kept its own copy; they look for upstream releases not merged yet, on purpose.
- The workflows cannot import Python, so their `branches-ignore` filters, which skip PR checks against that branch, use GitHub's pattern `"[0-9]+.[0-9]+"` instead of the version. It matches bare two-part names only, such as `1.14`, the way SAS mirrors AdvCiv's branches, not `v1.14` or `1.14.1`; Codex's review pointed out the gap with the shared rule.

#### `lib/blank_lines.py`

Finds newly introduced runs of excess blank lines while preserving spacing within literals and structured text. Used by the source provenance and text spacing checks.

#### `lib/ci_markers.py`

Holds the one spelling of each CI marker for the checks that read them: commit-message markers, such as `[ci_update_dll]`, and source-comment ones, such as `ci_define_uncached:`; see [CI markers in commit messages](#ci-markers-in-commit-messages) and [CI markers in source comments](#ci-markers-in-source-comments).

#### `lib/cpp_lex.py`

Masks C++ comments and string and character literals while retaining line breaks and character offsets. The duplicate-include and source provenance checks use `mask_cpp` to distinguish active code from commented-out code and literal text.

#### `lib/git_context.py`

Runs Git commands, resolves comparison bases for local and CI checks, and decodes historical file contents.

#### `lib/reference_spellings.py`

Holds the one-token spellings of numbered references, such as `PR#50`, `KI#1104` and `SGR210`, and the spaced forms they replace, for [`numbered_references.py`](#builddocumentationnumbered_referencespy) and [`squash_pr_number.py`](#buildrepositorysquash_pr_numberpy).

#### `lib/revision_history.py`

Parses diagnostic revision history entries and validates their Change fields for the SASGameRecord and Runtime checks, and reads `[ci_squash_pr]` to tell whether a PR is intended to be squash-merged.

#### `lib/sas_live_define_overrides_file.py`

Reads `SASLiveDefineOverrides/SASLiveDefineOverrides.txt` with the game's own parser: it loads `Assets/Python/SASLiveDefineOverridesBridge.py` with stand-ins for the two engine modules it imports, so CI and the game cannot disagree on what the file holds or which XML defines it may override.

Used by [`build/source/sas_live_define_overrides.py`](#buildsourcesas_live_define_overridespy). See [KI#128.5](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#ki-128.5).

#### `lib/xml_defines.py`

Reads integer and text values from Civ4 GlobalDefines XML and supports checks of staged diagnostic defaults.

### Source

#### `build/source/advisor_scoreboard_space.py`

Fails when an `Assets/Python` file calls `getAdvisorScoreboardSpace` without declaring `SAS_LEAVES_SCOREBOARD_SPACE = True` in a class body, or declares the marker without calling it.

- While such an advisor is open, the scoreboard shortens leader names to fit beside it, and `CvScreensInterface` finds the open advisors by that marker. An unmarked advisor would leave the scoreboard's war dots and power ratios under it at 1920 px and font 4.
- Added on 2026-11-20, when the marker replaced a hand-kept list of 8 screen IDs in `CvMainInterface.py`, which a new advisor could have missed.
- The check follows a direct-call convention rather than resolving inheritance: the advisor class that calls the helper declares the marker in its own file. A subclass inheriting both, such as `CvForeignDiplomacyAdvisor`, needs nothing.
- Definitions and comments do not count as calls. `CvScreensInterface.py`, which looks up the open advisor's space, and `CvTechChooser.py`, whose space is read apart, are exempt with their reasons in the check.

#### `build/source/checkout_byte_compares.py`

Fails when a CI build script compares bytes (`read_bytes()` with `==` or `!=`) without a `# bytes-compare: <reason>` note on that line or the line above.

- On 2026-11-16 [`ui_map_sync.py`](#buildrepositoryui_map_syncpy) compared the checked-out UI map with its generator's output as bytes. A Windows clone with `core.autocrlf` checks text out with CRLF while the generator writes LF, so it failed locally on an unchanged file while GitHub's LF checkout passed, and GitHub could never catch it.
- Text comparisons (`read_text`) ignore line endings, so they are the default; a byte comparison that is needed, such as for a binary file, states why in its note.

#### `build/source/cpp_define_reads_cached.py`

Fails when the DLL reads a define by name, such as `GC.getDefineINT("SAS_X")` or `GC.getDefineINT("STANDARD_HANDICAP")`, outside a function-local `static`, unless its function says why with a `ci_define_uncached:` comment, so `rg "ci_define_uncached:"` lists every such read; see [AGENTS.md](/AGENTS.md#caching-and-variable-reuse).

Each such read looks the name up in a string map, so a read on a recurring path belongs in a `static const` or AdvCiv's enum-backed `CvGlobals` cache.

- Added on 2026-11-25. A full audit found 545 SAS define reads: 484 in statics, 59 that run once or rarely, such as lazy setting caches, the EXE patches at startup, which the plot indicator's repeats on a resolution or BUG map option change, and SASGameRecord's session rows, which now carry the comment, and two that recur.
  - Both were diagnostic: `SAS_logFirstCityShadowScoutEntry`, behind BBAI's first-city Settler level 3, read `SAS_1ST_CITY_SCOUT_FOG_END_REF_PLOT_MULT` for each frontier plot and step, while the gameplay path beside it already kept it in a static.
- A static is found by walking back to the start of the read's statement, through calls and brace initializers such as `static const int ai[] = { GC.getDefineINT("SAS_A"), ... }`; a `}` closing an earlier block ends the walk.
- The marker counts only in comments, anywhere between the end of the previous function and the read, so it can sit above the signature; a read inside a loop needs it inside that loop.
  - Codex's review (GPT-6.2-Sol) reproduced the first version's gaps: a marker inside a string counted, two functions inside an `extern "C"` block shared one region, a marker for a cold read covered a hot one in a loop below, and a `#if` line or a comma declarator such as `static int a[] = {0}, b = ...` hid a static; each now has a test.
  - A function with no loop of its own but called on a hot path is still covered by its marker, so the comment must be true, which review checks.
- The token went from `Not cached:` to `define-uncached:` to `ci_define_uncached:` at the user's suggestion (2026-11-25): such generic words can appear in any prose, so an unrelated comment in the same function could exempt a recurring read without anyone meaning to, and a grep for the token would mix exemptions with ordinary comments. The `ci_` prefix, as in the `[ci_update_dll]` commit marker, names a token only this check reads.
- It also fails a read whose call is split across lines, such as `getDefineINT(` with the name on the next line, which hides the read from a grep for the name; none was on 2026-11-25, when the user asked.
  - Only the call must stay on one line: a statement holding a read may span lines, as the 18 doing so then were mostly tables of reads, long conditions and calls carrying inherited markers such as `// advc.301`, which read better split; a rule for whole statements would have needed exceptions for each, so the short ones were collapsed by hand instead.
  - `--list-multiline` lists those statements, with their first line and length, for such a review; it found 18 that day and fails nothing.
- `--list-shared` lists the defines read by name in two or more functions, with each reader, for choosing what joins the enum cache; on 2026-11-25 its review moved 10 inherited defines there ([KI#128.3](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#ki-128.3)). It fails nothing either.
  - Codex's review (GPT-6.2-Sol) reproduced two gaps in the first version: a read was named after the function before its own, and a call closing its parenthesis on the next line passed the split-call rule; a CRLF file's line splice also escaped the scan. Each now has a test.
- It also fails a type-name define in the enum cache, such as `STANDARD_HANDICAP` or `CAPITAL_BUILDINGCLASS`: `CvXMLLoadUtility::SetPostGlobalsGlobalDefines` turns those from XML type names into indices after `cacheGlobals` has filled the cache, through `GetDefinesVarSystem()->SetValue`, which never refreshes it, so the cache keeps a stale value.
  - Moving those two there crashed new-game creation in a Debug-opt test on 2026-11-25, and Codex's review flagged the same load order unprompted; the 31 `SetGlobalDefine` names in `CvXMLLoadUtilitySet.cpp` are the list checked.
- It scans `CvGameCoreDLL`'s `.cpp`, `.h` and `.inl` files, where the C++ code lives, headers' inline functions included.
- At first only SAS defines were checked, and `--all-defines` listed the reads of inherited define names: 52, at setup or on other infrequent paths, none per plot or per unit.
  - The user pointed out the same day that inherited code runs just the same, so a new uncached inherited read deserves the same check; the check now covers every define, and the 52 carry the comment in 22 functions.
  - Examples: `CvGame::doVoteSelection` resets a Secretary-General timer only when it runs out, `CvGlobals::updateCityCamDist` runs on a field-of-view or resolution change, `FIELD_OF_VIEW` is reread because the main interface's slider changes it during play, and `CvMapGenerator::addRivers` reads fresh by design since [KI#243](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#ki-243).
- Runtime Python has no such check: its SAS define reads sit at module level, in screen `__init__` methods, behind lazy `None` caches or once per screen opening or map generation, and none sits inside a loop; the most frequent is `Earth2.py`'s `findStartingPlot`, which reads two once per player.
  - The eight looped reads are inherited BUG and vanilla ones, over a tech's few prerequisites or the options screen.
- Enum-backed `GC.getDefineINT(CvGlobals::SAS_...)` reads are cached already and are not matched; `sas_define_usage.py`'s test keeps them out of statics.

```bash
python .github/workflows/build/source/cpp_define_reads_cached.py
python .github/workflows/build/source/cpp_define_reads_cached.py --list-multiline
python .github/workflows/build/source/cpp_define_reads_cached.py --list-shared
```

#### `build/source/cpp_standard_conformance.py`

Fails when the DLL source brings back one of the non-standard C++ forms that AdvCiv's `advc.cppstd` commit removed from the BtS code it inherited. VC2003 accepts them, so the game is unaffected, but a standard-conforming compiler such as Clang rejects them or leaves their behavior undefined. See [KI#1099](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#ki-1099).

- A `void` function that returns a `?:` expression, such as BtS's `return m_pPlayer ? m_pPlayer->disbandUnit(bAnnounce) : NULL;`.
  - `return f();` in a `void` function stays allowed, since returning a void call is valid, and so does a `?:` inside a call's arguments.
- An `#include` path with a backslash, such as `".\cvreplaymessage.h"`.
- Varargs read through the address after a named parameter, `(char*)(&format+1)`, instead of `va_start`.
- It scans every tracked C/C++ file under `CvGameCoreDLL/`, skipping comments and string literals. It does not cover the other cases that commit fixed, such as narrow `"+"` passed to a wide `%s` format or a `void*` parameter that should be `void const*`.

#### `build/source/custom_comment_closing.py`

Fails when a `# <!-- custom: ...` or `// <!-- custom: ...` comment in Python or C++ is left open: its `-->` must come before the next code line, before another custom comment opens, or before the file ends.

- Why: an open note silently merges with the next one, losing its end and credit unseen. On 2026-11-26 a scripted edit of `SASCurrentDefines.py` removed the line that closed one, and the next note's `-->` then closed both, so the reflow helper saw one valid block; the user asked for this check.
- It scans runtime Python, map scripts, DLL sources and the repository's own Python tools; XML comments are `xml_comments.py`'s.
- A marker counts only after the line's comment start, outside any string, so checks and tools that hold the marker in a string pass; the first run flagged a dozen such.
- Python comments come from the tokenizer and C++ `/* */` blocks are tracked, so a marker in a triple-quoted string is no note, a note opened in a block comment must close before its `*/`, and markers on one line are read in order; Codex's review (GPT-6.2-Sol) found each gap in the first, line-based version.
- Run over the whole repository first, it found seven older comments never closed, in three Sevopedia pages, `CvCityAI.cpp`, `CvUnit.cpp` and two adjacent notes in `CvUnitAI.cpp`; each got its `-->`.

```bash
python .github/workflows/build/source/custom_comment_closing.py
```

#### `build/source/custom_comment_indentation.py`

Verifies that no `// <!-- custom: ... -->` or `# <!-- custom: ... -->` comment in DLL sources, runtime Python or map scripts is indented deeper than both the code line before it and the code line after it.

- A scripted edit once inserted retirement notes two levels too deep in `RiseFall.cpp` and `GroupPathFinder.cpp`; the code still compiled, so only review noticed ([KI#136](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#ki-136)).
- Requiring both neighbours to be shallower allows ordinary end-of-block notes, and a comment directly under a block opener (`{`, `:`, `(`, `,`, `\`), including commented-out code, is skipped.

#### `build/source/float_format_int_division.py`

Fails when runtime Python, including `LLM_Helpers/saspilot`, applies a `%.Nf` format to arguments that divide with no float in them (no literal such as `100.0`, no `float()`). Python 2.4 divides two integers to an integer, so the decimals print as `.00`.

- Vanilla Civ4's Victory screen showed the best rival's population and land shares this way, `2.00%` for 2.30% and 2.06% ([KI#290.2](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#ki-290.2)).
- A division by a value that is already a float passes only with one of those markers, so convert it at the division.

#### `build/source/inherited_files.py`

Keeps the [inherited files audit](/_1_AdvCiv-SAS/Docs/Source_Analysis/inherited_files_audit.md) in step with SAS's decisions about inherited files. It fails when:

- SAS starts or stops keeping the filename of a Python, XML, C++, `res` or `Config` file that vanilla, Warlords, BtS or base AdvCiv provides, or moves its file;
- SAS starts or stops importing an inherited Python module;
- SAS imports a base-game Python module it does not carry, unless `NOT_CARRIED` says why, as SAS keeps the base-game modules it uses ([KI#1104](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#ki-1104)); an entry nothing imports any more fails too;
- a SAS text file has a base-game text file's name, which would replace that file and drop the keys only it defines (KI#1104);
- a static import is outside SAS, the base game, and the known Python 2.4 runtime and optional modules (the scan covers `Assets/Python`, `PrivateMaps`, and `SASPilot/game`);
- a module outside its `SYSTEM_PACKAGES` importers imports a package the base game ships under `Python/System`: `wx`, wxPython, is allowed in the Pitboss server's `Assets/Python/PitBoss/PbAdmin.py` and `PbWizard.py` only, by path, carried on 2026-11-26 (KI#1104);
- the audit was generated from another inherited list.

After a failure, run [`inherited_files.py --inventory`](/LLM_Helpers/README.md#inherited_filespy), which needs only Git, and review the audit's reasons.

- GitHub's runners have neither Civ4 nor base AdvCiv, so [`inherited_files.tsv`](/_0_Legacy/Docs/Manifests/inherited_files.tsv) in the [manifests](/_0_Legacy/README.md#manifests) records what those layers ship, one row per file, never its content:
  - its path as the newest layer providing it ships it, and the layers that ship it;
  - its file events in upstream AdvCiv's history, read from base AdvCiv's newest release branch, which [`lib/advciv_release.py`](#libadvciv_releasepy) finds (`--upstream-ref` overrides it), rather than the local `Mods/AdvCiv` folder, which held SAS files upstream never had;
  - any layer keeping it at another path;
  - it changes only when those layers do; rewrite it then with `--write` on a computer with Civ4 installed, supplying `--civ4-root` when the checkout is outside the install.
- The audit records three fingerprints, of that list, of the inherited filenames SAS keeps and of the inherited modules it imports, so the check stores nothing about SAS and reads SAS's side from the tree.
- Added on 2026-11-22 at the user's request, with the audit, so a new inherited dependency or copy cannot go unrecorded.
  - Its first run found five imports in none of the three: BUG's optional `CvAltRoot`, `CvModFolder` and configobj's `validate`, each tried inside `try`/`except ImportError`, and Python 2's `imp` and `xmllib`.
  - The check uses the known Python 2.4 runtime modules so a Python 3-only import cannot pass on the strength of the CI runner's standard library.
- The shape was settled with the user the same day, after drafts that did not hold up:
  - the list first stored SAS's own status and hashes, which needed Civ4 to refresh after every SAS file change, then a path column per tree that repeated the same path four times;
  - a tracked SAS inventory would have churned with every SAS change and history rewrite, so the full list became a report in `LLM_Helpers/outputs/`;
  - a fingerprint over every SAS file would have failed most feature commits, so the check covers only decisions about inherited files.
- The test feeds it import lines, a Git tree with ignored outputs and the fingerprints.

#### `build/source/lint_suppressions.py`

Fails on any `noqa`, `type: ignore` or `pyright: ignore` comment in our Python that does not name its rule, such as `noqa: E402`, or gives no reason on the same line or the line above. AGENTS.md asks to fix the cause first and to explain any suppression that remains.

- Added on 2026-11-12, when two late imports after a `sys.path` entry each needed a `noqa`, one with no reason. Both were fixed at the cause by loading the module with `importlib`, and the check's first run found one more, a `type: ignore` around `re.match`, fixed by slicing.
- Comments are read with Python's tokenizer, so suppression text inside strings, such as test fixtures, is not counted; verbatim third-party copies under `LLM_Helpers/context/` and `_0_Legacy/` are skipped.

#### `build/source/python_aligned_columns.py`

Fails when the spacing between code tokens on a line in `Assets/Python` or `PrivateMaps` differs from the layout its `--fix` gives, as a formatter's check does.

A table with two or more columns to align uses tabs only, as the Sevopedia charts do, an idea taken from vanilla Civ4's `CvDebugInfoScreen.py`; one space separates tokens everywhere else. `checks-source.yml` runs it as **Runtime Python aligns columns with tabs and leaves one space elsewhere**.

- Added on 2026-11-22: SAS's own Sevopedia charts were aligned with runs of spaces, about 190 rows, which drifted out of line with each rename, such as `SevoPediaWorldSizeChart.py`'s `"W/H Ratio*"`, a few spaces short of its column; tabs move a column by whole tab stops, with far fewer characters.
  - [KI#21.8](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#ki-21.8) records the sweep that fixed 2,269 lines in 89 files before the check was added, as [AGENTS.md](/AGENTS.md#ci-workflows) asks.
- `--fix` lays each table out on 4-column tab stops, the width [`.editorconfig`](/.editorconfig) sets, every column one tab past its widest entry, and gives one space to everything else; it then checks that only whitespace changed, and a second run changes nothing.
  - A table is a run of adjacent lines at the same indentation with as many separators each, a separator being a `,` or `:` or an `=`; it runs on through comment lines, and two rows in a row that align nothing end it. Columns meet only at separators, so a dotted name such as `CyCity.getCommerceRate` is never split.
  - Only a table with two or more columns to align keeps tabs, such as the charts or `CvCustomizableDomesticAdvisor.py`'s `COLUMNS_LIST`. A key-to-value map such as `WorldSizeTypes.WORLDSIZE_ARENA:  1,`, an enum or an assignment list gains little from one aligned column, and a column whose cells are all as wide aligns nothing, so they get one space.
- Commented-out code follows the same rule: a run of comment lines whose text parses as Python, such as `CvCustomizableDomesticAdvisor.py`'s disabled `GRANK_*` rows, is laid out at the column it starts at.
  - Prose stays as written, including the map scripts' `#   FILE:    Wheel.py` notices, which parse in Python 3 as variable annotations, a syntax Python 2.4 does not have.
- Strings, indentation and the gap before a trailing comment are left alone; a prose comment aligned with spaces, such as `COLUMNS_LIST`'s column header, needs aligning by hand after `--fix`.
- A long table such as `COLUMNS_LIST` shows its columns only when its rows fit the editor: with VS Code's word wrap on, zoom out (Ctrl+-) to see the grid.
- Tooling Python under `.github`, `LLM_Helpers` and `tests` is not checked, as it is indented with spaces.

#### `build/source/python_binding_targets.py`

Fails when a Python binding in the DLL's `Cy*Interface*.cpp` files points at a neighbour's target rather than its own, as a copied line left unchanged does. Comments are ignored, in the bindings and in the headers. Three rules:

- An enum binding `.value("NAME", VALUE)` fails when `NAME` is itself an enumerator of the headers but `VALUE` is another, as `.value("TASK_CONSCRIPT", TASK_HURRY)` was ([KI#1090](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#ki-1090)). A rename whose Python name has no enumerator of its own, such as `PLOT_STYLE_NONE` for `NO_PLOT_STYLE`, passes.
- A method binding `.def("name", &Class::target)` fails when `Class` declares its own `name()` and `target` is neither `name` nor its `py_`/`py` wrapper. Methods AdvCiv retired by commenting out their declaration, such as `getStealTreasuryTypes`, pass.
- Inside `python::class_<Owner>`, a `.def` fails when it points at a class that is neither `Owner` nor one of its bases.
- Added on 2026-11-16 for [KI#1090.2](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#ki-1090.2). Run against the older files, it finds all seven slips known so far: [KI#1090](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#ki-1090)'s and KI#1090.2's four enum names, and the three getters [KI#122](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#ki-122) fixed by hand.

#### `build/source/python_dead_stores.py`

Fails when runtime Python in `Assets/Python` or `PrivateMaps` stores `self.X` twice in one block, at one indentation, with nothing between able to read the first value: a reader takes the first one for live, such as `SevoPediaTerrain.py`'s `H_RELEVANT_UNITS`, written twice from the same sum, or `CvForeignAdvisor.py`'s `X_LINK = 50` then `0`.

- Added on 2026-11-24 for [KI#1098.3](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#ki-1098.3), the family of [`adjacent_duplicate_lines.py`](#buildrepositoryadjacent_duplicate_linespy): a repeated line there, an overwritten value here.
- What may read the first value without naming it ends the search: a method on `self`, `self` passed on alone as an argument, or leaving the block through `return`, `break`, `continue`, `raise` or `yield`.
  - Stores inside a `try` block are not checked, as a `finally` or `except` can read the first value when the second store raises, nor is the rest of a function once bare `self` is aliased or passed on.
  - Files are tokenized, so comments and strings, docstrings included, are neither reads nor code.
  - Codex's (GPT-6.2-Sol) review reproduced each of these as a false positive of the first version, which cut lines at `#`.
  - A first scan without those found 26 pairs, half of them reads through such a call, such as `getNextWidgetName()` advancing `nWidgetCount`, or an early `return`, such as the World Advisor's empty Changes tab.
- An empty list reset, such as `self.plotTypes = [] # reinit the array for each pass` right before the store that fills it, is accepted: it misleads no reader, and eight inherited map-generation lines use it. Other empty values, such as `None`, are not.
- It is a heuristic, line-based, and checks only one method: a placeholder set in `__init__` and replaced in another method before any read is what the report-only [`audit_screen_init_layout.py`](/LLM_Helpers/README.md#audit_screen_init_layoutpy) lists.

```bash
python .github/workflows/build/source/python_dead_stores.py
```

#### `build/source/python_define_reads_cached.py`

The Python counterpart of [`cpp_define_reads_cached.py`](#buildsourcecpp_define_reads_cachedpy): fails when runtime Python in `Assets/Python` or `PrivateMaps` reads a define by name, such as `gc.getDefineINT("MAX_TRADE_ROUTES")`, inside a function and outside a cache, unless the function says why with a `ci_define_uncached:` comment, so `rg "ci_define_uncached:"` lists the exemptions of both checks; see [AGENTS.md](/AGENTS.md#xml-lookup-caching-and-validation).

- Measured in game on 2026-11-26, best of 5 rounds of 20,000, a read through `gc` cost 279 ns and one through `SASCurrentDefines` 167 ns; once the bridge empties its caches rather than each read asking its change count, a read costs about 80 ns under Python 2.4, so even a read once per deal, hotkey press or map takes the cache; the marker is for a define other code sets during play, such as Water.py's `PLOTS_PER_RIVER_EDGE`, which `SASCurrentDefines` would miss.
- A cache is `SASCurrentDefines`, a store into an attribute of `self` in `__init__` outside any loop, or a read under a lazy guard of the form `if self.x is None:`, `if getattr(self, "x", None) is None:` or `if NAME is None:` on a declared global, a one-line `if` included; a store in another method runs at each call, and a guard on a parameter, such as `CvMapGeneratorUtil`'s `if fracXExp is None:`, falls back to the define at each call, so both need a reason.
  - The guard is a heuristic: the read under it is not tied to filling that cache, so `if self.x is None: return gc.getDefineINT("X")` passes though it reads at each call, as Codex's review (GPT-6.2-Sol) found; tying it would reject `getGGBarTextMode`'s valid read into a local before the store, so such a guard is reviewed by eye.
- A read inside a `for` or `while` body runs at each pass, so only a marker inside its innermost loop covers it, a comment counting for the blocks its column sits in; a read in a `for`'s own header, such as `range(gc.getDefineINT("MAX_TRADE_ROUTES"))`, runs once, while a `while`'s condition runs at each test, so it belongs to that loop.
- Codex's review (GPT-6.2-Sol) found the first version's gaps, each now tested: a store into `self` in any method or loop counted as a cache, an unrelated guard such as `if self.ready and value is None:` passed, a read split after its bracket was missed, an outer loop's marker covered an inner one, and a valid one-line `if self.x is None: self.x = ...` failed.
- Module-level and class-body reads are left to [`python_define_reads_import.py`](#buildsourcepython_define_reads_importpy), and reads through a variable name, as `SASCurrentDefines` and the overrides bridge make, are the caches themselves.
- Added on 2026-11-26 for [KI#128.9](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#ki-128.9), SAS and inherited defines alike, as in C++. Run repo-wide first, it found 97 reads in 54 functions; five ran in a loop, once per leader or tech, and are now read once before it, and all but the river define go through `SASCurrentDefines`.
- It also fails when a `SASCurrentDefines` read fills a cache kept for the session, in `__init__` or under such a lazy guard: `SASCurrentDefines` is for a read at each use, which live overrides refresh, and a kept attribute for a value fixed for the session, read with `gc`, so keeping a `SASCurrentDefines` value mixes the two.
  - Added on 2026-11-27, after the user caught `CvMainInterface.py`'s new units-waiting switch filled that way. Run repo-wide first, it found no other case; a related slip from the KI#128.9 pass, a local copied from an attribute and filled through `SASCurrentDefines` when empty, which this rule does not see, was fixed by hand in `initState`.

```bash
python .github/workflows/build/source/python_define_reads_cached.py
```

#### `build/source/python_define_reads_import.py`

Fails when runtime Python in `Assets/Python` or `PrivateMaps` reads a GlobalDefine at import, at module level or in a class body, through `getDefineINT`, `getDefineFLOAT`, `getDefineSTRING`, `getDefineBOOL` or `SASCurrentDefines`: the value is then kept for the session, so an override from [`SASLiveDefineOverrides.txt`](/README.md#live-define-overrides) never reaches it, and AGENTS.md prefers reading after setup, as early reads were linked to instability in [KI#128](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#ki-128).

- Added on 2026-11-26 for [KI#128.6](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#ki-128.6). Run repo-wide first, it found 16 such reads, 15 SAS switches in the Sevopedia and BUG's `PEACE_TREATY_LENGTH` in `MoreCiv4lerts.py`, all now read at use; [`audit_define_timing.py`](/LLM_Helpers/README.md#audit_define_timingpy) found the same 16.
- Files are tokenized, so a define's name in a comment or string is no read, and scope comes from the tokens rather than the indentation: a def whose signature spans several lines, with comments at another indent between them, still encloses its body, as in `CvMapGeneratorUtil.py`.
- A read inside a def's body, a one-line def's included, or a lambda's body runs only when called, so it passes.
- What module-level code calls is followed too, as it runs at import: the `__init__` of a class built there, such as `CvScreensInterface.py`'s `mainInterface = CvMainInterface.CvMainInterface()`, a base class's when the class has none, the functions called there, and in turn whatever those call through `self`, by a class name such as `Base.__init__(self)`, or by a name the file defines or imports, objects built inside them included.
  - Added on 2026-11-26, closing the gap [KI#128.6](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#ki-128.6) left.
  - Run on that commit's tree and today's, it found no read in the paths it follows, but two behind `CvEventInterface.py`'s `initAfterReload()`, which runs them only once `BugInit.init()` succeeds, not on the normal first import, while the game is still initializing: the 51 SAS and 4 inherited `__init__` reads KI#128.6 counted sit in classes built later, mostly Sevopedia pages built on first opening.
  - Blocks and names come from Python tokens, and a name is found in its own file or where the file imports it from, by name, alias or `*`, as the 25 map scripts' `balancer = BonusBalancer()` needs.
  - Codex's review (GPT-6.2-Sol) reproduced a first, line-based version missing base classes, objects built inside `__init__`, module functions, constructions under a module-level `if` and one-line `__init__`s, and following a call in a comment, a decorator's lambda and a class imported from another module; each is now a test.
  - A call it cannot resolve, such as an engine method or a name built at run time, is not followed, nor is a call whose outcome depends on a run-time test, which it follows whatever the test: a module-level call whose reads cannot run at import says why with `ci_import_call:`.
  - A def's header and a lambda's arguments run where they stand, so a read in a default argument fails, as Codex's review (GPT-6.2-Sol) found when the first version passed `def f(x=gc.getDefineINT("X"))`.

```bash
python .github/workflows/build/source/python_define_reads_import.py
```

#### `build/source/python_engine_callbacks.py`

Fails when a base-game entry point SAS carries loses a top-level function the engine calls by name: `PbMain.py`'s Pitboss callbacks, `CvTranslator.finishText` and `CvDebugInterface.toggleDebugMode`. Nothing in SAS calls them, so a cleanup or rename would pass every other check and fail only in game or on a Pitboss server.

- Added on 2026-11-26 for [KI#1104](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#ki-1104), when those entry points were carried. The list is curated: each name was found as a string in `Civ4BeyondSword.exe` or `Civ4BeyondSword_PitBoss.exe`, or in the DLL's `CvPythonCaller.cpp`, and the table says where.
- The EXE registers every module in `EntryPoints` and every map script as an `EntryPoint module:`, so registration alone does not show which functions it calls; `CvMapScriptInterface.py`'s map script stubs are left out, and functions no engine file names, such as `CvUnitControlInterface.ProcessEvent`, are not listed.
- It reads Python tokens, so only a `def` at column 0 counts: a method, a commented-out def or one inside a string does not satisfy it. A first, line-based version took a def in a triple-quoted string for real, as Codex's review (GPT-6.2-Sol) reproduced.

```bash
python .github/workflows/build/source/python_engine_callbacks.py
```

#### `build/source/python_multiline_calls.py`

Fails when a call in `Assets/Python` or `PrivateMaps` spans several lines, commented-out calls included, as searches find them too: one line per call greps, compares and lints better, as [AGENTS.md](/AGENTS.md#code-layout-and-collapsing) prefers unless that makes it overly complicated. `--fix` collapses what it flags.

- Added on 2026-11-22: hand sweeps with [`collapse_multiline_calls.py`](/LLM_Helpers/README.md#collapse_multiline_callspy) had no guard, so the [KI#1104](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#ki-1104) copies brought 18 back, such as WorldBuilder's `attachPanelAt`, and 7 SAS calls such as `a, b = _readIniValues(` slipped past the helper; 10 more were commented out, such as `CvDebugInfoScreen.py`'s disabled `screen.addPanel(`.
  - [KI#21.7](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#ki-21.7) retraces those sweeps and what came back.
- It is a heuristic: a call is a dotted name and `(` starting a statement, after `return` or `yield`, or after an assignment target such as `a, b =` or `out[0] =`, and the call itself must span lines; a commented-out call is a run of up to 20 comment lines that compiles once uncommented.
- A flat list or tuple of plain values counts too when it wraps, with several items on one line, as `CvDebugInfoScreen.py`'s `CivInfoItems` did; one item per line stays allowed.
- A comment inside moves, unchanged, onto its own line above the collapsed one, as the movie screens' `#self.EXIT_TEXT,` did; only provenance markers keep a call multi-line, such as AdvCiv's `# <advc.092>` around the arguments it changed, or a SAS `custom:` note, and line-scoped directives such as `# noqa`, which only work on their own line; a comment after the closing bracket stays at the end of the collapsed line.
  - Above moved comments, `--fix` writes a custom note saying where they came from, credited with `--credit "<model>"`, which it then requires: alone, the movie screens' `#self.EXIT_TEXT,` read like a stray line.
- Tables, conditions and multi-line strings stay multi-line, as do quotes inside a multi-line `custom:` note, such as `SevoPediaReligion.py`'s copy of a base AdvCiv call; tooling Python under `.github`, `LLM_Helpers` and `tests` is not checked.

#### `build/source/python_resource_api.py`

Checks consumers of `SASVisualUtils` and `SASTextScale` against their source-derived API, without importing Civ4 or maintaining one spelling guard per resource family. `checks-source.yml` runs it as **Shared Python resource API contracts**.

- Reads module exports, classes, inheritance, methods, explicit instance attributes and constructor-created objects from Python syntax trees. Import aliases, from-import aliases and local-module re-exports are followed.
- Derives dynamic member names from the providers' named tables, DLL enums, BUG symbol registrations and color/art XML. New ordinary collections and methods enter the contract through their declarations, without editing a checker-side member list.
- Reports missing collections/members, unbound namespace roots targeting a known shared API export, missing explicit imports, calls to known non-callable values and straightforward positional/keyword argument mismatches. Strings/comments and shadowed module aliases are excluded.
- Rejects recognizable direct lookups that bypass a shared resource cache, and exact copies of shared art-path literals. Lookup signatures are derived from provider cache writes, constructor-supplied getters and inherited accessors, so ordinary new cached families enter the rule through their implementation.
  - This replaces the earlier regex-based raw-lookup/shared-art tests in `test_python_visual_resources.py`, so aliases and justified exceptions follow one rule. Straightforward legacy forwarding helpers are traced from source too; the separate resource-inventory, namespace, retired-module and display-char checks remain.
  - Current coverage includes symbol/yield/commerce/religion/corporation/bonus glyph ordinals, special religion/corporation glyphs, yield colors, art paths/civilization buttons, literal color identities and the shared font-size Defines. Changing gold amounts or other gameplay values does not require fetching their stable display glyph again.
  - A necessary direct read needs a comment on the lookup line or immediately above it: `# <!-- custom: resource-cache-direct: Explain the concrete reason. (model credit) -->`. Provider implementations own these reads and are excluded from the bypass rule; ordinary API checks still apply there.
  - Cache ownership can cross methods: an accessor returning `self._textureCache[index]` may call an initializer that fills it from `getSpecialistInfo(...).getTexture()`. The lifetime cleanup exposed a missed bypass rule when those operations moved apart; reachable self-method calls, inherited methods and cache identity now connect the public accessor to its writer.
  - This is static origin tracing, not proof that every possible resource reconstruction is detected. Unknown object types, cross-module engine-object re-exports, computed color/Define names and arbitrary recreated mapping/formatting logic can escape detection; other reads such as current player gold or uncached info descriptions remain valid.
- Ordinarily validates changed runtime Python modules and their reverse import dependencies, including unchanged consumers of a changed module. Changes to the shared providers, relevant XML/configuration, `CvEnums.h` or this checker require the wider consumer check.
  - Source trees are read to establish declarations and dependency relationships; incremental selection limits which consumers are validated, rather than claiming every unchanged file is never read.
- Limits: this is a partial static contract checker, not a general Python type checker or an engine simulation. Arbitrary runtime-created attributes, computed return-object types, control-flow-dependent aliases, initialization order and calls using argument unpacking are not proven. Unrecognized dynamic surfaces remain opaque rather than inventing members or rejecting unknown engine behavior.
  - The current runtime sources can be read by the modern Python AST parser used here; the separate Python 2.4 check still establishes runtime syntax compatibility.

The motivating failures illustrate different gaps:

- Replacing `HEALTHY_ICON` inside `UNHEALTHY_ICON` produced `UNSASVisuals.StaticArt.HEALTHY_PERSON`, causing `NameError` during BUG configuration loading. It was valid syntax; Ruff's F405 rule is excluded from the blocking gate because star imports also supply legitimate engine names.
- F3's `CvForeignAdvisor.sasFontTagTitle` raised `AttributeError` after the advisor stopped re-exporting the former font helper. Valid module names do not establish that a requested member exists.
- The broader scan additionally found GameFont Display calling nonexistent `Font.ordinals()`; it now searches the existing cached glyph tuple. The Traits page receives its namespace through `_sevopedia_helpers` star exports, which the resolver follows rather than reporting a false missing import.

Fixing the namespace error did not repair the stale font access: a spelling guard cannot establish whether a valid module exports a requested attribute. Adding another special case for each failure would leave similar gaps in other resource families.

The shared check instead compares consumers with provider declarations and resource data, so the same rules cover different collections and members. New ordinary declarations change the checked contract without requiring another error-specific pattern; dynamic behavior still has the limits listed above.

`tests/source/test_python_resource_api.py` also exercises direct cache bypasses, documented local exceptions, alias/shadowing boundaries and new cached families without checker edits. Cross-method fixtures cover private/inherited initialization helpers and reject false contracts from uncalled writers or uncached metadata.

`test_python_visual_resources.py` additionally derives SAS-owned InterfaceArt keys from `CIV4ArtDefines_Interface.xml` and rejects their raw literal use outside the central provider, with the same documented direct-read exception. This catches fixed keys passed through arbitrary UI helpers as well as direct lookups; dynamically selected or inherited ArtDefine keys remain valid.

Its specialist fixture runs the production resource class with hidden/reordered IDs and an empty visible set, checking actual IDs and reuse of cached textures/buttons instead of requiring exact loop or variable spellings. The GP fixture checks cached results and temporary construction-record lifetime.

Its API fixtures cover all current collection families, inherited and XML/enum-derived members, aliases/re-exports, incorrect calls, provider edits, false-positive boundaries and incremental dependency selection. The earlier namespace-substring and font-name ownership guards were replaced by this shared check.

```bash
python .github/workflows/build/source/python_resource_api.py --base-ref <base-sha>
python .github/workflows/build/source/python_resource_api.py --all
```

#### Custom-comment logical reflow

`checks-source.yml` runs `python LLM_Helpers/formatting/reflow_custom_comments.py --check` automatically for maintained C++/Python/XML source. It reports when an eligible marked custom prose comment needs logical sentence/clause reflow, prints the affected paths and leaves all files untouched.

It does not impose a character-width limit or reflow inherited comments; structured, code-like and ambiguous blocks remain explicit skips for manual review.

Why logical lines rather than a width:

- A grep or a diff shows one physical line, so a line holding one whole sentence gives a reader, person or agent, a complete thought, while a width cut leaves half a sentence on each line, tedious to find again and to read.
- Sentences, not paragraphs, keep the lines short enough to read; a long but clear sentence stays whole, since splitting it would bring back half-sentence hits.
- Runtime Python calls follow the same idea, one call per line, as [`python_multiline_calls.py`](#buildsourcepython_multiline_callspy) checks.

Preview with `python LLM_Helpers/formatting/reflow_custom_comments.py --diff`, then use `--apply` on selected files and review the result. See [the helper documentation](/LLM_Helpers/README.md#custom-comment-logical-reflow) for scope and examples.

#### `build/source/python_wrapper_null_args.py`

Fails when a Python wrapper in the DLL's `Cy*.cpp` files dereferences a pointer argument, written `p->getX()`, while the native function it calls declares that parameter `= NULL` in the headers. Python's `None` then raised "unidentifiable C++ exception" instead of meaning no plot or no attacker; the fix passes it on as `(p == NULL ? NULL : p->getX())`.

- Added on 2026-11-17 for [KI#1091.2](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#ki-1091.2). [KI#1091](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#ki-1091)'s combat wrappers and `pushMission` had this shape, and the check, run against the files before their fixes, found 18 such arguments in 15 wrappers.
- A native parameter without a `NULL` default needs a real object, such as `canWork`'s plot, so dereferencing it passes. Comments are ignored, with the comment stripper of [`python_binding_targets.py`](#buildsourcepython_binding_targetspy).

```bash
python .github/workflows/build/source/python_wrapper_null_args.py
```

#### `build/source/raw_getinfotype.py`

Verifies runtime Python files do not add raw `getInfoTypeForString(...)` or `CvUtil.findInfoTypeNum(...)` lookups outside strict helper implementations and narrow legacy/dynamic exceptions. Use `getInfoTypeOrFail(...)` or `findInfoTypeNumOrFail(...)` for literal/static XML tag lookups so missing or renamed tags fail loudly.

Python comments and string literals are ignored, so code-generation strings such as those in `savemap.py` are not flagged by this check. This allowed to [find](https://github.com/wonderingabout/AdvCiv-SAS/actions/runs/27464773794/job/81185039717) this alternative lookup and that it needed an or fail handling too: now fixed.

#### `build/source/sas_live_define_overrides.py`

Fails when the shipped [`SASLiveDefineOverrides/SASLiveDefineOverrides.txt`](/SASLiveDefineOverrides/SASLiveDefineOverrides.txt), which overrides SAS defines of `GlobalDefines_advciv_sas.xml` while Civ4 runs, differs from the XML or names a define its override cannot reach. See [KI#128.5](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#ki-128.5).

- It fails:
  - a file the game's own parser rejects: a malformed line, a name set twice, or a name that is no integer define of the XML, which `setDefineINT` would otherwise create silently;
  - a shipped override that differs from its XML value, so the game plays the same with the overrides on or off; a different value stays a local, unstaged experiment, so `ci_report.py` runs this check with `--staged`, which reads the values and the XML from the index and the NoEntry list and sources from the working tree;
  - a define kept where an override cannot reach it: a module global or `self.` attribute in runtime Python, or a `static` in the DLL;
  - a comment line in the file, which holds values only, as each define's comment stays in the XML;
  - an override naming a define of [`SASLiveDefineOverridesNoEntry.txt`](/SASLiveDefineOverrides/SASLiveDefineOverridesNoEntry.txt), which lists each define in full with its reason, the failure printing it, in two sections: never, such as master logging switches and EXE patch settings, and not for now, read once by code that could be changed to follow an override; a `*` pattern in that file fails too, as a grep for a define must find its line;
  - since 2026-11-26 ([KI#128.7](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#ki-128.7)), a shipped line for a define not in [`SASLiveDefineOverridesAllowed.txt`](/SASLiveDefineOverrides/SASLiveDefineOverridesAllowed.txt), which the game would refuse, an allowed define without a shipped line, so the values file shows every live define, and a define in both the allowed and NoEntry lists; the reader scan above covers every allowed define.
- Not covered: a read through a name in a variable, as `SASTextScale`'s font sizes, so such a helper clears its own cache when the bridge's change count moves; a lazy global or a `self.` cache split across lines; and defines no shipped line names.

```bash
python .github/workflows/build/source/sas_live_define_overrides.py --staged
```

#### `build/source/sevopedia_top_attributes.py`

Fails when a Sevopedia page reads `self.top.X` and `SevoPediaMain.py` neither assigns `self.X`, defines `def X` or a class attribute `X`, nor does any page assign `self.top.X`. Python finds such a mistake only when the line runs, so it can hide behind one key press.

- Added on 2026-11-13 for [KI#1086](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#ki-1086): the move of the Sevopedia colors into `SASVisuals.Color` left `SevoPediaIndex.py` reading `self.top.COLOR_HIGHLIGHT_TEXT`, which raised a Python exception on Down after a search.
- Files are read with Python's tokenizer, so a comment such as "Was self.top.COLOR_HIGHLIGHT_TEXT" or a string holding the same text does not count; a first draft cut comments by hand, which Codex's review showed a string or an escaped quote could fool. No page reads a member of BtS's `CvPediaScreen` base class, which CI does not have; a page that starts to would need it listed.

#### `build/source/shared_define_values.py`

Fails when a Python script writes one of the switched GlobalDefines names with a number, as in `{"SAS_SGR_LOG": 0}` or `"SAS_UI_DAWN_OF_MAN_ON": (1, 0)`, anywhere but [`LLM_Helpers/diagnostics/define_values.py`](/LLM_Helpers/README.md#define_valuespy). Scripts import the values from there instead; a name alone, as in `getDefineINT("SAS_SGR_LOG")`, is fine.

- Added on 2026-11-19: `SAS_UI_DAWN_OF_MAN_ON` alone stayed at its shipped `1` after a branch switch, and the audit of the toggle behind it found each shipped value written twice, once in a CI check and once in `toggle_dev_diagnostics.py`, with nothing keeping them in step. The committed toggle had 9 such copies.
- Test folders are skipped, since tests feed chosen values to the checks rather than restate what ships, as are the Git-ignored review copies in `LLM_Helpers/outputs/`.

#### `build/source/source_change_provenance.py`

For `Assets/XML/GlobalDefines_advciv_sas.xml` only, separators must contain exactly three blank lines, or none between adjacent blocks. Users read and edit this configuration file directly, so three blank lines distinguish thematic groups while related settings stay adjacent.

The initial sweep normalized existing separators; subsequent checks audit the file whenever touched. Blank lines inside XML comments, CDATA, attributes and text values remain protected. Other source files retain the ordinary diff-aware spacing policy.

Diff-aware source-history guard for maintained C/C++, Python and XML source. It compares the selected push/PR range with its base instead of linting old source in isolation.

Every rule it applies is listed in `REPO_WIDE_RULES` or, with the reason, in `DIFF_ONLY_RULES`; a rule in neither fails the check (added 2026-11-21).

- A rule must hold across the whole repository from the commit that adds it, then it may be checked on changed files only. The user asked for a check rather than trusting AGENTS.md's written rule alone.
- The repo-wide rules also run over every maintained source file on each run, about 10 seconds: a comment line starting with "See KI#", blank-line runs, credit spelling and cascading comments.
- The diff-only ones list why the repository does not meet them, such as the 188 untouched inherited files without a SAS header, which AGENTS.md allows.
- A comment line may not start with a KI reference, such as `# See KI#1103 for ...`; the reference ends the line before. One scan found a single older case, CvDeal.cpp's KI#605 line, fixed with the rule.

It enforces these review rules introduced after repeated provenance mistakes:

- existing one-line C++ declarations and definitions must remain on one line so the complete signature can be found with grep;
  - Added on 2026-11-19, after the base AdvCiv 1.14 merge carried upstream's wrapped parameter list into `CvCityAI::AI_bestSpreadUnit`, splitting SAS's one-line signature.
  - Moving the return type or a trailing qualifier such as `const` onto its own line counts as a split; template lines, access labels such as `public:` and preprocessor directives above the signature do not.
  - Only signatures that were on one line and whose lines the change touches are checked, so new functions and signatures already wrapped in inherited code can still be edited.
  - The gap this leaves: a new function written wrapped from the start passes, as two SAS ones did, `SAS_logInheritedWonderValue` and `getSASReplayStartYearArithmeticBounds`, collapsed by hand on 2026-11-25 with three others; only `CvDLLEntityIFaceBase.h`'s `PlayAnimation`, the EXE's interface header, stays wrapped on purpose.
  - No rule closes it, as of 2026-11-25, although not ideal, because this check's signature parser cannot tell a signature from a call, and flags 107 hits, mostly calls such as `FErrorMsg(...)` and constructed locals, when asked for every wrapped one.
    - A possible extension would be to require one line only for the signatures a commit adds, a diff-mode rule needing a stricter test on few candidates; a stricter repo-wide detector, for definitions and declarations at file or class scope outside comments; or a real C++ parser such as libclang, at the cost of a new dependency.
- Newly added or changed comparisons on DLL save-layout flags and versions fail, including `uiFlag < 23` and `iSaveVersion == 1`.
  - The same check catches reintroduced legacy helpers such as `IDInfo::validateOwner`, `MissionDataLegacy`, and `LegacyArrayEnumMap` uses.
  - It compares active code with the base and permits writer marker assignments, comments, and unrelated flags such as `uiFlagBits`. See [KI#46.2](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#ki-46.2).
- in an upstream merge, a comment found word for word in the merged parent's copy of the same file counts as inherited, so upstream's own notes can be kept as they are;
  - Added on 2026-11-19, when the base AdvCiv 1.14 merge's restored comments, such as PerfectMongoose.py's `# advc.oxi: New method to replace erroneous uses of getCirclePoints`, failed as new uncredited prose, and the merge had first reworded them as custom comments to pass.
  - The merged parent is the second parent of a merge commit in the checked range, or `MERGE_HEAD` while the merge is prepared; [`ci_report.py`](/LLM_Helpers/README.md#ci_reportpy) gives its temporary commit that parent too. Comments are compared line by line without indentation, so a reworded copy still fails;
- another mod's comment may be quoted as is, without a model credit or reflow: a custom line saying it is a quote, such as "Quoted from", and naming the source, then lines each starting with `// >` or `# >`; our own prose mixed into the quote still fails. Added on 2026-11-12 after the globe patch's comments restated Realism Invictus's findings in our voice;
- added/modified Python and XML files carry the standard AdvCiv-SAS modification copyright header alongside inherited owners' notices; newly inserted/moved SAS notices must follow pre-existing owner credits, which include mod-component credits written as "by <Name>, ver." (e.g. `*ActualQuotes* by Willowmound, ver. 4.20`);
  - in XML, place the SAS notice before explanatory comments. Unchanged files and pure renames are excluded;
- newly added/changed direct C++ JSON `Format`/`format` literals keep one object field per adjacent string literal, matching the Runtime formatters without changing emitted JSON bytes; unchanged inherited groups and commented-out examples are excluded;
- new/rewritten Python compound-statement suites reject the E701 pattern `if enabled: log(...)`; keep the body on its own indented line, including diagnostic guards. Unchanged inherited inline suites are outside this diff-aware check;
- rewritten commented-out code is not inherited prose: a changed `//`, `#` or XML comment block passes when every added or removed line is code-like (statements, calls, braces, conditions; XML elements) and a new custom note sits within three lines. Changed prose lines in the same block still fail, and provenance markers such as `advc.131` must survive in the rewritten code or the note;
- newly authored or substantively rewritten source comments use `<!-- custom: ... (model credit) -->`; model-authored comments need the credit, while user-authored comments may omit it. Missing model credits are advisory warnings, not helper failures; unchanged/moved inherited comments and whitespace-only reflow remain valid, while stale inherited comments may simply be removed;
- when a nearby replacement custom comment retains identical or substantially unchanged prose, recognized existing credits in its trailing parenthesized credit list are preserved; dropping one contributor still fails even if another credit remains. Credit reordering/additions and whitespace reflow are allowed, as are whole-comment deletions and unrelated replacements;
- parenthesized custom-comment credits reject the known misspellings `Chat-GPT` and `catgpt`, ignoring case. Prose mentions and other model names remain allowed; this is a small typo guard, not a list of approved models;
- a parenthesized credit naming a Claude model without its family, such as `Opus 5.5` or `code Opus 5.5`, fails; write it in full, such as `Claude code Opus 5.5`. Claude Code Opus 5.5 wrote `(Claude code Opus 4.6 + Opus 5.5)` on 2026-11-26, which the user caught in review, while the credit parser skipped the bare name as no known family;
- newly introduced source separators of three or more blank lines fail; use at most two.
  - Extra separators can accumulate during agent patching or leave inconsistent runs of four or five blank lines without a structural purpose. This guard prevents that formatting noise after the initial cleanup.
  - Changed Python, C/C++ and XML are compared against the base. Unchanged or shortened inherited runs remain allowed; multiline strings, block comments and XML text are protected.
  - Removing code that joins two short separators is checked too. Comment reflow and the critical Ruff gate do not enforce this source-spacing rule; Markdown keeps its existing documentation checks.
- new or rewritten comments reject clear cascading layouts: an extra Python/C++ comment prefix introducing an appended custom explanation, two custom blocks joined on one line, or a nested XML comment. Use separate comment blocks; ordinary inline C++ annotations and marker text inside code strings remain valid. This detects structure, not whether an explanation should be split on meaning alone;
- new or edited dedicated multiline custom C/C++ comments use `//` on each line, rather than `/* ... */`;
  - Each matching grep line should identify itself as a comment without requiring surrounding block context. This catches the block-style KI#243.2 rationale and delimiter-only changes even when the prose stays identical.
  - The existing source check runs this on changed files, without a separate workflow.
  - Quoted examples, untouched blocks, inherited prose with inline custom fragments and single-line inline annotations are allowed.
- if an inherited comment is replaced by a nearby custom comment, known provenance markers such as `advc.xxx`, `KI#...` and `Long_Comments_... #N` are retained;
- every added/removed/changed C/C++ `#include` or Python import has a nearby newly added custom rationale comment, including dependencies in new files; untouched inherited directives are excluded;
- added/removed/changed literal-named Boost.Python `.def(...)` bindings have a nearby new custom rationale comment; a Python help string alone is insufficient. A coherent nearby binding group may share its explanation, and unchanged/reflowed bindings are excluded;
- Parameter-list and return-type changes on existing non-SAS C++/Python functions have a nearby newly added custom comment explaining the interface change.
  - Clear function renames are checked too: one removed and one added function in the same replacement hunk and scope. Clearly SAS-named helpers remain optional; renaming a non-SAS function to a SAS name still needs rationale.

The check is deliberately conservative rather than a full C++ parser. New functions/files have no previous interface contract to explain; new files still require dependency explanations. Distant moves and ambiguous many-function replacements are not guessed to be renames; review those manually.

Standard repository header/directive comments are exempt from the new-comment rule, and source-file deletion is allowed without a tombstone comment.

A non-custom comment also passes when the same file contained it word for word before the base commit (Git pickaxe search of that path's history). This allows restoring an inherited block, such as the AdvCiv `CIV4GameText_advc.xml` text entries moved back from `AdvCiv-SAS_main.xml` on 2026-11-04; changed wording still fails.

The SAS header may also touch an inherited comment block, as in `RandomNameUtils.py` under its original author lines: the block still counts as unchanged when only those two header lines were added.

The header of the generated AIP predump module is `aip_predump_values.py` output, so it is exempt too.

Credit matching is deliberately conservative: free-form attribution, distant moves combined with rewrites and wholesale rewrites still need review.

For example, changing a legacy `void capture()` into `bool capture()` must explain what success/failure means to callers; a name-only `score` to `rank` replacement needs its rationale too. Tests cover those failures and acceptance after adding comments, alongside unchanged overloads, return-type reflow, new functions and ambiguous/distant replacements.

Comment wording quality remains a human-review concern; when run, the helper verifies provenance/rationale presence, not whether the rationale is persuasive.

Run locally against the previous commit with:

```bash
python .github/workflows/build/source/source_change_provenance.py
```

Or provide an explicit comparison base:

```bash
python .github/workflows/build/source/source_change_provenance.py --base-ref <base-sha>
```

A base-game file SAS takes in whole, as [KI#1104](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#ki-1104) asks, keeps its original comments and imports without custom notes: a file new to the checked range counts them as inherited when its leading source header says "Copied from" and the layer and path from `Assets/` match the [inherited-files manifest](/_0_Legacy/Docs/Manifests/inherited_files.tsv). The full install path stays in the header for readers.

- Before this (2026-11-22), every push whose range held the KI#1104 copies failed on their hundreds of Firaxis comments, as main did after the PR#50 squash and its amend.
- GitHub's runners have no Civ4 install to compare the copy with, so the header is trusted once the manifest confirms the path; the copy's custom notes and SAS header are still checked as usual.

#### `build/source/string_label_compares.py`

Fails when runtime Python (`Assets/Python`, `PrivateMaps`) compares a value with a short lowercase string literal, such as `kind == "btn"`, unless a `sas-ci-string-compare-exemption: <reason>` note sits on that line or the line above, inside a credited custom comment.

A note above an `if` also covers the `elif` branches of its chain.

- A label of our own compared as a string fails without any error when it is misspelt, so it is better as a boolean, a widget, a named constant or a lookup that raises on an unknown value. A string read from outside, such as BUG's option types or a WorldBuilder file's `"false"`, is fine with its reason.
- Added on 2026-11-16: the first draft of [KI#300.2](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#ki-300.2) told its Timeline events apart with `"city"` and `"player"`.
  - The same review found the Sevopedia charts showing no icon for a misspelt token, the movie player playing any unknown kind as a BIK and the Customizable Domestic Advisor silently stopping a row on an unknown column type; each now fails loudly or compares no string.
- Three inherited files SAS does not extend are skipped whole: BUG's `BugOptions.py` and `UnitNameEventManager.py`, and the Planet Generator map script.

#### `build/source/unicode_button_paths.py`

Fails when runtime Python starts a button or icon path as `u""` (a variable named `sz...Button` or `sz...Icon`). The engine takes icons as `char const*`, so a unicode one raises a Boost `ArgumentError`.

- Added on 2026-11-15 for [KI#118.2](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#ki-118.2): `CvVictoryScreen.py` set `szNameButton = u""` for a vote building built by an unmet team, and the whole Victory screen broke at turn 120 of a SAS48 island autoplay. It found 16 such defaults, all now `""`.
- `SASTextScale`'s `setTable*Scaled` helpers also pass icons through `str()`, which covers every caller of the wrappers; the check keeps direct screen calls safe too. Names ending in `Icons` (plural), such as `AttitudeUtil`'s, hold icon characters for text and stay unicode.

### XML and rules

#### `build/xml/advanced_start_era_points.py`

Verifies each era's `iAdvancedStartPoints` stays within 10% of base AdvCiv's buying power at the current SAS cost percentages.

The expected value is AdvCiv's points scaled by the ratio of the SAS and AdvCiv `iTrainPercent`, `iConstructPercent` and `iGrowthPercent`, because SAS flattened those percentages without changing the points.

AdvCiv's values are pinned in the checker, as CI has no AdvCiv install; a new era needs a baseline row.

#### `build/xml/asset_primary_tech.py`

Automated XML/rules check. Requires the effective primary unit/building prerequisite to be in the latest required `iGridX` column. Religious buildings and Bomb Shelters may use their shared SpecialBuilding prerequisite; direct `PrereqTech=NONE` is valid there.

Both units and buildings store additional prerequisites in `TechTypes`. Equal-column alternatives remain allowed for display timing.

For resource-specific connecting improvements, checks that the resource's `TechCityTrade` is guaranteed by its reveal and Build prerequisite paths. This catches the six plantation resources retaining Calendar after the Build moved to Agriculture, even though Calendar and Agriculture share a column.

City-like Forts are excluded. The rule applies to every resource with an XML-defined connecting improvement, without named resource exceptions; unknown or unguaranteed trade requirements fail.

Trade unlocks were aligned to the current reveal/Build prerequisites, including the former Marble, Stone and Uranium delays. Changing or renaming resources, builds or technologies needs no checker allowlist update.

#### `build/xml/asset_tech_prereq_redundancy.py`

Flags stale additional unit/building tech requirements when the primary tech already guarantees them through every valid prerequisite path. To keep nearby foundational requirements explicit when useful, it applies only when the additional tech is from an earlier era and the primary tech is at least two columns after the start of its own era.

Era starts and tech-graph guarantees are derived from current XML, so moving or collapsing tech-tree columns updates the check automatically.

#### `build/xml/barbarian_balance.py`

Verifies two Barbarian values stay strictly above every other player's, since a retune could otherwise reach another player's value unnoticed:

- the Barbarian Worker's `iWorkRate` against every other land Worker (`DefaultUnitAI` `UNITAI_WORKER`), including civ-specific ones: its work rate is its main reason to stay civ-specific;
- the Barbarian leader's `iBuildUnitProb` against every other leader's, keeping Barbarians focused on military pressure.

Barbarian assets are found through the `CIVILIZATION_BARBARIAN` civilization's `Units` and `Leaders` lists.

#### `build/xml/bonus_font_order.py`

Verifies that the Nth BonusInfo in `CIV4BonusInfos.xml` uses GameFont glyph N through its art's `FontButtonIndex`, that `CIV4ArtDefines_Bonus.xml` is sorted by `FontButtonIndex`, and that no two art entries share a glyph.

The game itself works in any order, since a bonus's icon comes from `FontButtonIndex` alone. But on 2026-11-08 the XML listed Camel before Peat while their glyphs were the other way round, and the art file still had BtS's grouping, so the XML, the art and the fonts read differently.

Keeping one order makes them easy to compare; [`gamefont_tga.py`](/LLM_Helpers/README.md#gamefont_tgapy) can move glyphs when a bonus is added or moved.

Religions and corporations get their glyphs from XML order itself, and [`build/xml/xml_display_order.py`](#buildxmlxml_display_orderpy) already checks that order.

#### `build/xml/building_art_lsystem_names.py`

Verifies that every `<LSystem>` in `CIV4ArtDefines_Building.xml` names a `building:LSYSTEM_*` placement rule of the city L-system.

- SAS currently uses the BtS `CIV4CityLSystem.xml`, which is not in the repository, so the check reads its 24 names from [`building_art_lsystem_names_bts.tsv`](/_0_Legacy/Docs/Manifests/building_art_lsystem_names_bts.tsv), regenerated locally with `--write --civ4-root <Civ4 install root>`.
- The names are plain identifiers rather than hashes, so failures can list the valid choices.
- If SAS ships its own city L-system, the check reads that file instead.

It catches art imported from another mod with that mod's layout name: the Chieftain's Hall art from Realism Invictus used `LSYSTEM_VIKING_TEMPLE`, which only RI defines (KI#1074).

#### `build/xml/civ_specific_assets.py`

Verifies that civilization and leader references resolve to existing leader, art, trait, civic, and religion entries, and that each civilization's building and unit replacement class matches the class declared by the referenced asset.

It also checks shipped Customizable Domestic Advisor `BLDGCIV_<BuildingInfo Type>` columns so a renamed or replaced civ-specific building cannot silently disappear from a saved layout.

It also verifies civ-specific building and unit assets do not require a later starting tech-tree column (`iGridX`) or an earlier obsolete tech-tree column than the generic asset they replace; same-column parallel tech variation is allowed for flavor.

For example, this helped [spot](https://github.com/wonderingabout/AdvCiv-SAS/actions/runs/27461191223/job/81175197986) and fix `BUILDING_AZTEC_SACRIFICIAL_ALTAR: building class BUILDINGCLASS_MONUMENT replacement uses later tech column than default BUILDING_MONUMENT: TECH_CALENDAR (GridX=2, GridY=11) after TECH_MYSTICISM (GridX=1, GridY=11)`, but `BUILDING_JAPAN_DOUJOU` (JAIL) requiring `TECH_MEDITATION` parallel (`iGridY=9`) to `TECH_CONSTITUTION` required by the generic `BUILDING_JAIL` is fine so it does not need a fix.

Similarly for `BUILDING_EGYPTIAN_OBELISK: building class BUILDINGCLASS_MONUMENT replacement uses earlier ObsoleteTech column than default BUILDING_MONUMENT: TECH_BROADER_EDUCATION (GridX=10, GridY=11) before TECH_LIBERALISM (GridX=13, GridY=11)` being obsolete sooner and so weaker than the generic monument so fixed it (obsolete is now same `GridY` or later).

#### `build/xml/civ_specific_not_weaker.py`

Verifies civ-specific unit/building replacements are not weaker than their generic class defaults. Unit replacements fail if their `iCombat` or `iPower` is lower than the default unit for the same `UnitClass`; building replacements fail if their `iPower` is lower than the default building for the same `BuildingClass`.

#### `build/xml/corporation_prereq_bonuses.py`

Verifies that no corporation lists more `PrereqBonuses` than `NUM_CORPORATION_PREREQ_BONUSES` allows (5 in BtS's `GlobalDefines.xml`, unless `GlobalDefines_advciv_sas.xml` overrides it), and that none lists the same bonus twice.

AdvCiv stores the inputs in a list without a size limit, so the game itself uses every one, but Python reads only up to the define. When Peat was first added to Mining Inc as its 6th input, the Sevopedia's Mining Inc page showed only 5, and debug builds assert while loading the XML.

#### `build/xml/define_int_bounds.py`

Verifies `GlobalDefines_advciv_sas.xml` integer values stay within `[-100000, 100000]`, except specific intentional outliers such as the launch-guard sentinel checked by [`build/xml/launch_guard.py`](#buildxmllaunch_guardpy) and the high bonus-Fallout scrub worker value.

#### `build/xml/define_tag_refs.py`

Verifies any SAS `DefineTextVal` token that looks like a known Civ4 XML tag (e.g. bonuses, techs, building classes, units, promotions) references a real XML `<Type>` value; successful matches are printed by default, and `--quiet` suppresses them.

#### `build/xml/feature_impassables.py`

Verifies that every unit with `FeatureImpassables` blocks the same set of features.

The wheeled units share one rule for dense or wet ground; when a feature such as Marsh joins that set, this catches units that were left out.

#### `build/xml/global_define_lengths.py`

Verifies every shipped root GlobalDefines/PythonCallbackDefines file and any modular `*_GlobalDefines.xml` / `*_PythonCallbackDefines.xml` file keeps `<DefineName>` and `<DefineTextVal>` content at no more than 255 UTF-8 bytes.

The inherited loader passes those fields through fixed `char[256]` scratch buffers and the visible FXML `char*` interface supplies no destination capacity, so 255 bytes leaves room for the C-string terminator.

This is a loader-safety boundary, not a general `FVariableSystem` string-length limit; integer/float/boolean values are parsed through typed branches and are outside this check. See KI#1001.

The checker reports the longest current name/text values on success so growth remains visible without imposing a lower stylistic name limit. It counts surrounding whitespace conservatively rather than assuming the closed XML API removes it before copying.

Regression tests cover the exact 255/256 boundary, UTF-8 byte counting, whitespace, `PythonCallbackDefines.xml`, and modular define files.

One logical value uses an unsuffixed name. When split across two or more defines, every member uses `_PART_N`, consecutively from `_PART_1`, with positive, unpadded suffixes and no unsuffixed base key alongside them.

- A lone numbered key fails and should use the unsuffixed name; `EXAMPLE_LIST` plus `EXAMPLE_LIST_PART_2` also fails because a split family must number every member.
- Names are grouped across shipped files, allowing repeated override declarations; this checks naming, not whether a consumer reads every part.

#### `build/xml/global_define_name_style.py`

Enforces the preventive desired `DefineName` maximum of 42 UTF-8 bytes across the same shipped GlobalDefines/PythonCallbackDefines surface as the fixed-buffer checker.

Every Define in `GlobalDefines_advciv_sas.xml` must also start with `SAS_`; inherited files retain their existing naming. This catches misplaced generic keys such as the moved `SAVE_VERSION`, now configured as `SAS_SAVE_VERSION` with the old engine/BUG key derived during loading.

The 42-byte target comes from Base AdvCiv 1.14, SAS's direct parent, whose supplied define names top out at 42 bytes. It is a readability/headroom naming policy, not a Civ4 engine limit; KI#1001's separate 255-byte checker remains the hard loader-safety boundary.

Shipped names, additions and renames must remain within the 42-byte target; if a clear name cannot fit without obscure abbreviations or loss of important units/semantics, review the policy rather than hiding meaning.

Regression tests cover the exact 42/43-byte boundary, UTF-8 byte counting, inherited names, `PythonCallbackDefines.xml`, modular define files, and SAS-file prefix enforcement using the real `SAVE_VERSION`/`SAS_SAVE_VERSION` example.

#### `build/xml/global_defines_nonempty.py`

Verifies shipped root GlobalDefines/PythonCallbackDefines and modular `*_GlobalDefines.xml` / `*_PythonCallbackDefines.xml` files have non-empty `<DefineName>` values, globally unique names across those files, and exactly one non-empty value field (normally `iDefineIntVal`, `fDefineFloatVal`, or `DefineTextVal`).

All shipped names share the check, including inherited and SAS names. Duplicate declarations fail even if their values match; diagnostics report both files and declaration indexes, and collect all collisions in one run. Shortened SAS names can otherwise collide despite their common `SAS_` prefix.

The engine permits overrides, but this check requires uniqueness within the shipped files rather than silently accepting load-order-dependent duplicates. It does not compare against unshipped base-game files or separately installed mods; an intentional override within the shipped set requires explicit review of the check.

We check this because we suspect they may possibly cause unclear errors; for intentional "empty" string-like behavior, explicit values such as `NONE` are clearer and more reliable.

#### `build/xml/launch_guard.py`

Verifies `SASDefineGuard.py` exists and its int/string sentinel constants match `GlobalDefines_advciv_sas.xml`.

#### `build/xml/marsh_bonuses.py`

Verifies that every bonus able to appear on flat Grassland either allows Marsh in its `FeatureBooleans` or is listed in the checker's exclusions with a reason, such as Corn being a dryland crop.

Civ4 places a bonus under a feature only when the bonus lists that feature, so a new Grassland bonus would otherwise silently never appear on Marsh. The check also fails on stale exclusions and on a Marsh bonus missing Grassland in its `FeatureTerrainBooleans`, which could never be placed.

Only Marsh is covered: the inherited Forest, Jungle and other feature bonus lists were already settled by BtS and AdvCiv, while Marsh is new and lies on Grassland, the terrain with the most bonuses. A future feature could get the same kind of check.

#### `LLM_Helpers/balance/military_tree_continuity.py`

`checks-xml.yml` runs this helper with `--check --review-summary-only`.

It fails only when a playable civilization loses the last unlimited, technology-only military unit in a land/sea/air domain across a reachable technology-column state; pure exploration units do not count as military fallback coverage.

The manual full-report mode also lists narrower successor transitions that add unguaranteed technologies or resource/religion/building requirements; those diagnostics are review-only.

See [`LLM_Helpers/README.md`](/LLM_Helpers/README.md#military_tree_continuitypy) for the exact model and commands.

#### `build/xml/plot_asset_buttons.py`

Verifies that no feature, bonus, improvement, route or build shares its button with another of these, except an improvement or route with the builds that create it, which is how BtS pairs them. The inherited graphical-only Land Worked and Water Worked improvements, which both use the atlas's empty cell, are allowed.

The new Peat Works first reused Quarry's button, and Drain Marsh at first reused the Marsh feature's, so the Sevopedia showed two assets with one picture. Both were noticed only by eye, the first one in game.

#### `build/xml/plot_lsystem_asset_relationships.py`

Verifies active `CIV4PlotLSystem.xml` rules that constrain both a Bonus and an Improvement against the current `CIV4ImprovementInfos.xml` bonus relationship. This catches stale graphical pairings when gameplay data moves a resource to another improvement.

Unused inherited graphical definitions are allowed: selectors for BonusInfo/ImprovementInfo Types absent from the current SAS XML are ignored. For example, the check caught the stale `IMPROVEMENT_FARM + BONUS_WINE` Grapes rules after current SAS had moved Grapes to Plantation.

It also reports an ArtRef that requires an Improvement no incoming production allows: after that fix, `BLeaf_4x3` was reached only by Plantation productions but kept its goal art on Farm (KI#1074).

#### `build/xml/religion_tech_buttons.py`

Verifies that each religion's `TechButton` and `GenericTechButton` is its founding tech's own `Button`, or a BtS religion button whose picture was drawn for that same founding tech.

- The choose-tech popup and the top tech bar show these religion buttons instead of the tech's own while the religion is unfounded. BtS drew each as its BtS founding tech's picture plus a religion badge.
- Added after [KI#1072.2](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#ki-1072.2): six religions moved to other founding techs kept their BtS buttons, so e.g. Calendar showed Polytheism's marble heads. Like `asset_primary_tech.py`'s trade check ([KI#1072](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#ki-1072)), it catches a tech link left behind when SAS moves a prerequisite.

#### `build/xml/retired_global_define_names.py`

Reads the original-to-current conversion table associated with KI#1001.2 directly and rejects retired `SAS_*` names in active XML, C++, Python and documentation.

The checker reads the table directly from the [retired-name migration reference](/_1_AdvCiv-SAS/Docs/Deprecated/global_define_names.md). This keeps one migration map instead of maintaining a second manual retired-name list.

A split can list comma-separated backticked replacement names, and historical aliases may share destinations. Every target must be declared; duplicate retired names or repeated targets within one row still fail.

The active scan intentionally includes XML comments and copied cache/member identifiers, so stale explanatory comments and code identifiers cannot silently preserve an obsolete spelling.

Wildcard references such as `SAS_BBAI_UWAI_*_LOG_LEVEL` also fail when they match retired names but no current declaration; broad patterns shared by old/current names remain valid. The exact-name scan missed these family patterns.

Name-fragment parsers still require source review: the BBAI formatter retained the former suffix matcher after the complete keys were renamed, emitting full keys instead of compact category tokens.

Exceptions preserve the Known Issues investigation, the two frozen audit/archaeology records, published changelogs, dev logs, SGR revision history and its captured example. The migration table is validated separately; AGENTS permits only its explicit old-name search example. Other documentation, including current source-analysis documents, remains checked.

The checker also verifies every mapped current name is still declared in `GlobalDefines_advciv_sas.xml`; a later rename therefore requires updating the existing original-to-current KI row rather than creating an intermediate mapping chain.

Regression tests cover active runtime lookups, copied cache identifiers with lowercase/uppercase prefixes, XML comments, historical-document exclusion, missing current declarations, malformed marker order and longer unrelated keys.

#### `build/xml/retired_xml_asset_names.py`

Verifies that active XML, Python and C++ code does not use an XML asset identifier that SAS retired, such as `BONUS_GRAPES` (now `BONUS_WINE` again) or `LEADER_MAO_ZEDONG` (now `LEADER_CHINESE_LEADER`). A retired spelling would point at an asset that no longer exists.

- The retired names come from the first column of the tables in [`xml_asset_names.md`](/_1_AdvCiv-SAS/Docs/Deprecated/xml_asset_names.md), so that doc stays the single list; `*` there stands for any identifier characters (`TXT_KEY_BONUS_GRAPES*` covers the pedia key too).
- Comments and documentation are not checked: they keep the old names as history, for example in KIs and log captures.

#### `build/xml/sas_define_usage.py`

Checks both directions between `SAS_*` declarations of every value type in `Assets/XML/GlobalDefines_advciv_sas.xml` and runtime define lookups in `Assets/Python/**/*.py`, `PrivateMaps/**/*.py`, and `CvGameCoreDLL/**/*.cpp` / `**/*.h`. Missing declarations and declarations without a lookup fail with file/name diagnostics.

Comments, documentation, tests, compiled DLLs and generated `temp_files` are not runtime consumers; unrelated SAS constants, widget names, enums and log labels are not XML lookups.

The scanner follows string aliases and discovers functions forwarding a name parameter to a define getter, including font and BBAI helpers. Integer `%d` name families are expanded from explicit lower/upper guards with an immediate return, so all four current billboard font settings are checked, including missing family members.

Per-era families read through `SAS_readBarbarianEraCostPercents("<prefix>", ...)` in C++ are expanded from the era types in `Assets/XML/GameInfo/CIV4EraInfos.xml` (`ERA_ANCIENT` -> `<prefix>ANCIENT_PCT`), so each loaded era's define is required and counted as used, for example `SAS_BARB_REG_BLDG_COST_ANCIENT_PCT`.

Unsupported SAS name expressions fail and require extending the scanner rather than silently accepting a prefix. This is a static reference check: it does not prove a function executes, evaluate arbitrary Python/C++ expressions, resolve every possible cross-file alias, or preprocess C++ conditional compilation.

One existing declaration is intentionally coverage-only metadata: `SAS_MAP_SCRIPT_NAMES_HEAVINESS_UNSPECIFIED` is consumed by `build/runtime/mapscripts.py`, not by game code. Its explicit exception is reported separately and its documented consumer is verified.

Other unused declarations are errors. This checker does not change configuration values or require a SASGameRecord revision bump.

Enum-backed `GC.getDefineINT(CvGlobals::SAS_...)` / `getDefineBOOL(...)` calls count as XML Define usage too. The source test derives the shared-cache list from `CvGlobals.h`, checking duplicate names, master-list inclusion, repeated enum references and absence of leftover string/local-static copies.

#### `build/xml/sas_text_file_placement.py`

Verifies that SAS pedia texts sit in their dedicated file: asset `*_PEDIA` entries belong in `AdvCiv-SAS_Sevopedia_Lengthy.xml`, even short stubs, and concept pages (`TXT_KEY_CONCEPT_*_PEDIA`) in `AdvCiv-SAS_Core.xml`. The 2026-11-05 City Center texts, the Warrior pedia and a shared Barbarian stub had landed in `AdvCiv-SAS_main.xml` and were moved.

It also keeps SAS pedia names consistent: a SAS text used as an XML `<Civilopedia>` value must end in `_PEDIA` (or `_PEDIA_SR`, after BtS's own rules-changes concept page), and a SAS `_PEDIA` text must be used as one. Inherited texts are not checked; all 263 SAS `_PEDIA` texts already followed both rules.

#### `build/xml/sas_text_references.py`

Verifies every `TXT_KEY` defined across all SAS-owned GameText files (`Assets/XML/Text/AdvCiv-SAS*.xml`) is referenced by active mod XML, BUG configuration, Python, map-script Python, or C++.

The other direction too: every `TXT_KEY` used by active mod XML, Config, Python, map scripts or C++ must be defined by mod GameText or the inherited text, reading a `CHANGED_` tag as its key.

Inherited text counts only where BtS, Warlords or vanilla define it, from the hash list's `game` column: base AdvCiv's original files are not loaded by SAS, which carries its own copies, so 2,302 tags defined only there would otherwise pass while the game shows the key.

Base AdvCiv's own undefined keys are listed in [`xml_text_undefined_inherited.tsv`](/_0_Legacy/Docs/Manifests/xml_text_undefined_inherited.tsv). See [KI#1085](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#ki-1085).

It also verifies that buildings, units, civilizations, and leaders with SAS-owned descriptions reference Civilopedia keys defined in the mod's GameText files, unless the pedia text is explicitly confirmed as inherited from the base game or expansion.

Other explicit exceptions cover confirmed inherited base references, empirically confirmed EXE runtime references with no static reference, and BUG option-key families constructed dynamically at runtime. Every passing run prints the exact keys in each exception group so accepted uncertainty stays visible in CI.

An exception that is no longer needed fails too, so the lists stay a record of real exceptions. Moving identical text back to base AdvCiv on 2026-11-04 left eight such stale keys, for example `TXT_KEY_LEADER_TOKUGAWA_PEDIA`.

Every diplomacy response key used by `CIV4DiplomacyInfos.xml` must exist in mod GameText or in the inherited-text hash list of [`xml_sas_text_inherited.py`](#buildxmlxml_sas_text_inheritedpy), whatever its prefix (`AI_DIPLO_*`, `USER_DIPLO_*`). The `TXT_KEY`-only check could not catch a lost key such as the KI#149 `_CORRECTED` Montezuma demand, which only Warlords text defines.

The two sea-level recommendation labels are runtime exceptions because changing the High label changed its Custom Game list text in-game, and Low uses the matching EXE convention.

Inherited AdvCiv/BUG/BULL text remains outside the blocking unused-key check because a full static scan produces hundreds of uncertain legacy and dynamic candidates; the broader manual [`audit_unused_text_keys.py`](/LLM_Helpers/README.md#audit_unused_text_keyspy) remains available for optional review audits.

#### `build/xml/tech_columns.py`

Verifies all techs in the same tech-tree column (`iGridX`) share the same core column values, currently `iCost` and `iAsset`; different `iGrid` column rows in the same column are allowed, but same-timing techs should normally have identical research cost and asset/trade valuation.

#### `build/xml/tech_prereqs.py`

Verifies that every `OrPreReqs`/`AndPreReqs` entry in `CIV4TechInfos.xml` names an existing tech in an earlier `iGridX` column, and that the prerequisite graph has no cycle.

- Added after [KI#29](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#ki-29): clicking Transhumanism's box in the tech advisor crashed while placeholder prerequisites were in use, recalled as an impossible or circular dependency. The tree passed this check when it was added.

#### `build/xml/true_starts_coverage.py`

Verifies the True Starts companion data that the runtime actually depends on.

Every playable or AI-playable civilization must have exactly one `TruCivInfo`, because Random True Starts builds its civilization candidate pool from those rows and fixed civilizations can later be dereferenced through the same mapping while another player is Random.

Every leader referenced by a playable civilization must also have one `TruLeaderInfo` as the maintained SAS completeness policy; the runtime tolerates a missing leader row, but it would silently lose the optional contemporaneity/bias data.

`TruBonusInfo` is intentionally sparse: missing bonus rows mean no True Starts resource bias and are valid. The check therefore validates the uniqueness and resolution of supplied bonus rows without requiring one for every `BonusInfo`. Added with the KI#936 fix after the asset-companion audit exposed missing Ireland/Kingdom of Benin civilization rows and their three SAS leader rows.

#### `build/xml/turn_define_gamespeed.py`

Verifies turn-valued integer `SAS_*` defines make their game-speed semantics explicit in the define name. `T_NORM_GS` means the XML value is expressed at Normal speed and code must scale it with the appropriate game-speed percentage; `T_UNSCALED_GS` means literal game/path turns are intentionally kept unchanged across game speeds.

The existing longer `TURN(S)_NORMAL_GAMESPEED` and `TURN(S)_UNSCALED_GAMESPEED` forms retain those same meanings. Standalone `T` is checked alongside `TURN`/`TURNS`, so shortening the unit cannot silently bypass the classification check. Tests cover both spellings, missing/malformed/mixed classifications and non-duration uses.

The check ignores non-duration uses such as `SAS_DO_TURN_*` function-scope names, `...PER_TURN` rates, and `...PATH_TURN_VALUE...` score weights. It also recognizes legacy-looking maximum countdown, minimum/maximum age, and log-interval names so those cannot silently evade the convention.

This naming rule was added after auditing turn gates while implementing non-combat food-production allocation: the new production gate correctly needed `TrainPercent` scaling, nearby UWAI contact limits correctly represented unscaled movement/path turns, and the victory-denial countdown windows were found to need `VictoryDelayPercent` scaling.

The checker intentionally validates naming/declared intent rather than trying to infer the correct scaling formula from C++: code review still decides whether a Normal-speed value should use `TrainPercent`, `ConstructPercent`, `VictoryDelayPercent`, or another game-speed field. The explicit names make that audit grep-friendly and prevent ambiguous raw turn gates from being added silently.

#### `build/xml/unit_naming_combat_types.py`

Fails when BUG's [`Unit Naming.xml`](/Assets/Config/Unit%20Naming.xml) or its options tab lacks a `Combat_<type>` option for a unit combat type in `CIV4UnitCombatInfos.xml`, lists one for a type that no longer exists, or an option lacks its `_TEXT` or `_HOVER` text. BUG raises `ConfigError` for an unknown option, so a missing one breaks Unit Naming for every unit of that type.

- Added on 2026-11-13 for [KI#1087](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#ki-1087): SAS's split of `UNITCOMBAT_MELEE` into polearm and shock left only `Combat_MELEE`, so with Unit Naming on every Spearman or Swordsman raised a Python exception.
- The option texts are built from the option ID, so `sas_text_references.py` counts them as a dynamic family and cannot check them; this check does.

#### `build/xml/wonder_cost_columns.py`

Verifies normally constructible world wonders unlocked in the same technology-cost tier have the same production cost and that world-wonder costs increase in later, more expensive technology tiers. Multiple visual columns may intentionally share a timing tier when their technologies have the same research cost.

Great Person-founded shrines/corporation headquarters (`iCost=-1`) are excluded, as is the deliberately expensive United Nations diplomatic-victory wonder.

#### `build/xml/wonder_culture_gpp_columns.py`

Verifies normally constructible world wonders follow an era-relative flat-culture progression: 4 in the first two Ancient-era columns, 6 through the rest of the Ancient and Classical eras, and 8 through the Medieval and Renaissance eras.

From the start of the Industrial era, culture-advisor wonders without a culture percentage modifier have 10 flat culture and other wonders have none; a wonder with a local or global culture modifier has no flat culture in every era.

World-wonder Great Person point rates (`iGreatPeopleRateChange`) must match within each column and never decrease in later populated columns; GP-producing national wonders and ordinary buildings cannot exceed the latest world-wonder rate available by their direct or shared special-building prerequisite tech column. Great Person-founded shrines/corporation headquarters (`iCost=-1`) are excluded.

#### `build/xml/xml_child_duplicates.py`

Checks suspicious duplicate child/list XML entries inside the same parent object, failing on high-confidence duplicates such as duplicate flavors, leader memory/contact keys, civilization city names, and unit/promotion lists; reports lower-confidence duplicates such as exact duplicate event trigger `Text + Era` entries without failing, prints source line numbers, and hides known allowed/noisy duplicates such as weighted goody huts and reused world-picker art paths unless run with `--show-ignored`.

This helped [spot](https://github.com/wonderingabout/AdvCiv-SAS/actions/runs/27336768909/job/80762873956) and fix XML text duplicate errors.

See [KI#150](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#ki-150).

#### `build/xml/xml_civ4_text_characters.py`

Verifies active GameText values do not contain Unicode typography that Civ4 renders as visible artifacts, including em/en dashes, curly quotes, ellipsis characters, and non-breaking spaces. It also catches repeated question marks that indicate lost characters.

XML comments are ignored, while readable accented letters remain allowed.

#### `build/xml/xml_comments.py`

Verifies XML comments under `Assets/XML` do not contain illegal double hyphen `--` and are not left unclosed.

#### `build/xml/xml_display_order.py`

Verifies that XML lists whose file order players see follow the order players expect. Custom Game and the Policy Advisor show these lists in file order, so a misplaced entry is visible in game but nothing else reports it.

- **Leaders** follow the alphabetical order of their shown names. A test with `LEADER_CHINESE_LEADER` moved showed Mao Zedong between Lincoln and Louis XIV in the Custom Game list.
  - The shown name can differ from the Type: Mao Zedong is `LEADER_CHINESE_LEADER`, Roosevelt is `LEADER_FRANKLIN_ROOSEVELT`. `LEADER_BARBARIAN` and `LEADER_DEFAULTS` are not in the list and are skipped.
- **Civilizations** follow their short names: Custom Game lists short names in `CIV4CivilizationInfos.xml` order, while Play Now sorts full names itself. So `CIVILIZATION_AMERICA` ("United States") sits under U; Minor and Barbarian stay last.
- **Civics** follow, within each category, the tech-tree column (`iGridX`) of their required tech, as the Policy Advisor and the Sevopedia show them in file order. Civics without a required tech count as column 0.
  - The first run found Vassalage (Philosophy) after Bureaucracy (Civil Service) and Theocracy (Monotheism) after Pacifism (Medicine), both left behind by later tech moves.
- **Religions** keep the historical founding order SAS chose on 2025-05-22 (BtS starts with Judaism); the Sevopedia groups them by era and keeps their file order within each era.
  - The order must match the GameFont glyph order. The DLL gives each religion its icon and holy-city icon in XML order, so reordering religions needs the glyphs in `Assets/Res/Fonts/GameFont.tga` and `GameFont_75.tga` moved too, or the icons get swapped.
  - The first version also required the tech-tree column order of their founding techs. It was dropped on 2026-11-05: a later tech move could then have demanded reordering religions and moving their glyphs, against the historical order the file follows.
  - CI cannot see which picture sits in a `.tga` slot, so the check compares against the order read from both fonts' editor previews on 2026-11-05. Corporations follow the same rule if SAS ever ships `CIV4CorporationInfo.xml`.
- **Missionaries, religion buildings, executives and corporation headquarters** follow the order of their religion or corporation, so religion N's assets sit in position N of `CIV4UnitInfos.xml` and `CIV4BuildingInfos.xml`. No known screen breaks if they drift; the matching layout makes each family easy to find. They were already in order when the check was added.
- Names come from mod GameText, else from the inherited names list of [`xml_sas_text_inherited.py`](#buildxmlxml_sas_text_inheritedpy).
- True Starts is not checked: `CIV4TruLeaderInfos.xml` is looked up by `<LeaderType>`, so its order is not shown in game. Its base AdvCiv `TRU_RAMESSES` before `TRU_RAGNAR`, the reverse of the leader file, was swapped by hand on 2026-11-04 for tidiness (see [KI#1073.2](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#ki-1073.2)).
- See [KI#1073](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#ki-1073) for the screenshots and the misplacements this check found.

#### `build/xml/xml_element_only_content.py`

Verifies non-GameText XML under `Assets/XML` parses and contains no stray text between child elements. This catches XML that is well-formed but rejected by Civ4's schema loader, such as a leftover wrapped-comment line after a self-closing BuildingInfo field or a Python-style `#` before an XML comment.

GameText is excluded because its language elements intentionally contain text content and inherited files can use legacy encodings.

#### `build/xml/xml_parent_duplicate_keys.py`

Verifies parent-style XML objects are not defined twice with the same key, such as duplicate `*Info` `<Type>` values or duplicate audio `ScriptID` / `SoundID` entries. This intentionally does not check child/list duplicate semantics, which can be more context-dependent.

#### `build/xml/xml_redundant_defaults.py`

Verifies a small set of XML representations that are known to be semantically redundant in Civ4/AdvCiv-SAS: explicit zero-valued entries inside `Flavors`, where an omitted flavor already evaluates to 0, and non-empty `TechTypes` lists containing only `NONE`/`NO_TECH`, where an empty `TechTypes` list has the same effective meaning.

This was added after the flavor audit found both patterns in inherited/stale XML (see [KI#22.7](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#ki-22.7)).

The check is deliberately conservative rather than a generic "zero is bad" rule. Many scalar zero fields are mandatory or meaningful defaults, and some padded list formats may depend on loader/schema behavior.

Add another pattern only after confirming that the shorter representation is accepted and semantically identical.

#### `build/xml/xml_sas_text_english.py`

Verifies AdvCiv-SAS-owned GameText XML files (`Assets/XML/Text/AdvCiv-SAS*.xml`) only use `<English>` language entries. The former whitelist for renamed Moctezuma diplomacy entries was removed on 2026-11-04, when the inherited `MONTEZUMA` text keys were restored.

#### `build/xml/xml_sas_text_inherited.py`

Verifies that every entry in `Assets/XML/Text/AdvCiv-SAS*.xml` still differs from the inherited English text: base AdvCiv 1.12 (`0d81edb64`), else BtS, else Warlords, else vanilla. SAS text files hold only what SAS changed, so SAS text stays clearly separate from inherited text.

- An identical entry fails with what to do: restore base AdvCiv's original block in its inherited file, or delete the SAS entry so the BtS/Warlords/vanilla text applies.
  - The 2026-11-04 cleanup found 25 such entries, for example `TXT_KEY_LEADER_TOKUGAWA` (lengthened, then shortened back to AdvCiv's "Tokugawa").
- The comparison is strict: only CRLF/LF line endings are ignored, because Git checkouts can change them. A fixed hyphen, quote mark or space keeps an entry as an SAS change.
- GitHub has no BtS/Warlords/vanilla text files, so the check reads [`xml_sas_text_inherited_hashes.tsv`](/_0_Legacy/Docs/Manifests/xml_sas_text_inherited_hashes.tsv): one tag, source and truncated SHA-256 per inherited entry, without copying Firaxis text. Overview and samples: [Manifests of the inherited layers](/README.md#manifests-of-the-inherited-layers).
  - Why hashes instead of the text: we do not know whether copyright allows republishing complete unmodified game text files, and this check only needs to know whether two English texts are identical.
    - A hash answers that without containing the text: `TXT_KEY_LEADER_LINCOLN bts 8d54efb91fed8018` cannot be read back as "Lincoln" or sorted by it.
    - Only the English text is hashed, as SAS's text files currently hold English only.
  - Hashes cannot be read or sorted, so `--write` also stores [`xml_sas_text_inherited_names.tsv`](/_0_Legacy/Docs/Manifests/xml_sas_text_inherited_names.tsv): readable English only for the about 120 leader and civilization name keys that CI checks use, such as `TXT_KEY_LEADER_LINCOLN` -> "Lincoln".
  - Both are plain TSV with one header row and no comment lines, so table tools read them cleanly; Rainbow CSV's CSVLint in VS Code had flagged earlier `#` header lines as rows with the wrong column count.
    - There is no separate CSV/TSV lint: the readers already fail on a missing header row or a row without exactly three fields, and these lists are almost the only tracked TSV files (the other is generated context under `LLM_Helpers/context/`).
  - BtS, Warlords and vanilla do not change, and the base AdvCiv snapshot is a fixed commit, so the file should not need refreshing. If needed, regenerate it locally with `python .github/workflows/build/xml/xml_sas_text_inherited.py --write --civ4-root "<Civ4 install root>"`.
  - Warlords text is included: the game loads it too, since only Warlords defines keys such as `TXT_KEY_CIV_KOREA_DESC`. A first draft left Warlords out and wrongly kept `TXT_KEY_CONCEPT_IRRIGATION` as SAS text.

#### `build/xml/xml_suspicious_angle_tags.py`

Verifies raw XML files under `Assets/XML` do not contain suspicious malformed-looking tag punctuation such as doubled opening angles or extra closing angles after tags, catching valid-but-wrong text like `<French>>...`. This helped [spot](https://github.com/wonderingabout/AdvCiv-SAS/actions/runs/27342682844/job/80783239087) and fix suspicious malformed-looking XML tag punctuation.

See [KI#151](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#ki-151).

#### `build/xml/xml_suspicious_text_chars.py`

Verifies XML text does not contain high-confidence corrupted characters such as `?` inside a word-like token, Unicode replacement characters in active/non-ignored text, common mojibake fragments, raw control characters, or web tracking query parameters such as `?utm_source=...` in active text; inherited non-English replacement-character noise is hidden by default and can be listed with `--show-ignored`. XML comments are ignored, allowing source/reference notes to retain their original URLs.

This intentionally does not enforce broader typography policy such as em dashes, curly quotes, or accented letters. This helped [spot](https://github.com/wonderingabout/AdvCiv-SAS/actions/runs/27400470104/job/80977135402) and fix the corresponding errors.

See [KI#152](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#ki-152).

#### `build/xml/xml_text_duplicate_tags.py`

Verifies each GameText `TXT_KEY`-style `<TEXT>/<Tag>` entry under `Assets/XML/Text` is defined only once, with source line numbers for duplicate definitions.

Inspired by the old AdvCiv-SAS blind [scan_xml_duplicates-3.3.py](/LLM_Helpers/audits/scan_xml_duplicates-3.3.py) (see [Legacy XML duplicate discovery scanner (``scan_xml_duplicates-3.3.py``)](/LLM_Helpers/README.md#legacy-xml-duplicate-discovery-scanner-scan_xml_duplicates-33py)).

This helped [spot](https://github.com/wonderingabout/AdvCiv-SAS/actions/runs/27332010214/job/80746523894) and fix XML text duplicate errors. See [KI#149](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#ki-149).

## CI markers in commit messages

A marker is one bracketed token in a commit message, title or body, usually on a body line such as `- [ci_update_dll]`. It states an intent the change alone cannot show, so CI checks the change against that intent.

- A marker never skips a check, unlike GitHub's `[skip ci]`, which stops CI from running at all and so lets a problem through unseen. Ours are handled exceptions: every check still runs, and the marker tells it which result is the intended one.
- Each intent has one spelling, kept once in [`lib/ci_markers.py`](/.github/workflows/lib/ci_markers.py), and all start with `[ci_`, so one search finds every marker in the history.
  - They were plain phrases before 2026-11-22, such as `Update DLL`, taken from base AdvCiv's commits; the bracketed form keeps them from prose, and older commits keep their phrases, as CI reads only new ones.
- A bracketed marker counts wherever it appears in the message, so a commit message that only talks about one, such as a commit changing these checks, writes it without brackets, as `ci_update_dll`.
  - Example (2026-11-22): the draft message of the commit introducing these markers listed them in its prose, and the DLL check failed on "contains '[ci_update_dll]' but no DLL/build-JSON pair changed".
- A new marker belongs here, and only where the change cannot show the intent: an SGR or Runtime revision bump shows itself, through its define and history entry, so it has none.

| Marker | Intent | What CI still checks |
| --- | --- | --- |
| `[ci_update_dll]` | the commit ships the DLL on purpose | a changed DLL and its `Release` build report together; a DLL change without the marker fails, which catches a local test build committed by mistake. See [`build/repository/dll_commit_message.py`](#buildrepositorydll_commit_messagepy). |
| `[ci_edit_dev_log]` | the commit edits earlier dev log entries on purpose, such as a typo fix | the logs' authors and commits. See [`build/repository/dev_logs.py`](#buildrepositorydev_logspy). |
| `[ci_convert_line_endings]` | the commit switches files' line endings on purpose | everything else in the commit. See [`build/hygiene/line_ending_churn.py`](#buildhygieneline_ending_churnpy). |
| `[ci_squash_pr]` | the PR is intended to be squash-merged | the SASGameRecord, Runtime and DLL/runtime revision checks judge the whole PR as the one commit it becomes, so it still needs exactly one correct bump. See [`lib/revision_history.py`](/.github/workflows/lib/revision_history.py). |

- `[ci_squash_pr]` is read from the PR's newest commit message, which states the intent as it stands; a PR without it is checked commit by commit, which is right for a rebase or plain merge.
  - Example (2026-11-22): PR#50's draft commits bumped SGR to 210, then 211, then back to 210. Judged one by one, its SGR step failed on "regressed 211->210", although the squash commit, 209 to 210, passes. A GitHub label, `revision:squash`, said the same before, but was not in use; the marker replaced it.
  - The squash commit's own SHA cannot be known before the merge, so the newest revision entry says `pending`, and the next commit on main, or an amend of the squash commit, fills it in.
  - The squash commit's message must still meet the rules that read a message, such as a bumped revision named in its title; [`build/repository/squash_message.py`](#buildrepositorysquash_messagepy) lists them and checks a drafted message.
  - The squash commit keeps the marker, which GitHub's squash body carries from the PR's commits as this repository has it set, and names its PR in its title as `PR#50`; [`build/repository/squash_pr_number.py`](#buildrepositorysquash_pr_numberpy) checks it on main.
  - With it, the DLL check judges the PR as one commit too, and a new `(Requires AdvCiv-SAS N+)` must name main's count + 1; see [`build/documentation/requires_version_markers.py`](#builddocumentationrequires_version_markerspy).
- Local options do the same for a local run: `--squash` on the revision checks judges a branch as one squash commit; `--staged` on the diagnostic-default checks reads staged content while unstaged development values stay on (see [Local `--staged` option for diagnostic defaults](#local---staged-option-for-diagnostic-defaults)); `ci_report.py --message` takes a draft commit message, so the commit-message checks read its markers.

## CI markers in source comments

A source marker is a token in a comment that tells one check why the line or function beside it is a handled exception, followed by that reason. Like the commit markers, it never skips the check: it states the intent, and review checks the reason is true.

- Each one's spelling is kept once in [`lib/ci_markers.py`](/.github/workflows/lib/ci_markers.py) too, and [`build/documentation/ci_markers_listed.py`](#builddocumentationci_markers_listedpy) requires a row below for each.
- Prefer a specific token over a common phrase: such words can appear in any prose, so an unrelated comment could exempt a line unnoticed, and a grep for the token would mix exemptions with ordinary comments.
  - Example (2026-11-25): the DLL define-cache check first took `Not cached:`, the wording AGENTS.md suggested, then `define-uncached:`; the user found both too generic, and `ci_define_uncached:` names a token only that check reads.
  - The two older tokens keep their spelling: renaming them would touch every comment that carries one.

| Marker | Intent | What CI still checks |
| --- | --- | --- |
| `ci_define_uncached:` | a define read by name outside a static runs once or rarely, so it needs no cache; in Python, a define other code sets during play, so `SASCurrentDefines` would miss the change | every other read in the DLL and in runtime Python, and a read inside a loop unless the marker sits in that loop. See [`build/source/cpp_define_reads_cached.py`](#buildsourcecpp_define_reads_cachedpy) and [`build/source/python_define_reads_cached.py`](#buildsourcepython_define_reads_cachedpy). |
| `ci_import_call:` | a module-level call whose define reads cannot run at import, for the reason given, such as `CvEventInterface.py`'s `initAfterReload()`, whose reads run only once `BugInit.init()` succeeds, not while the game is still initializing | every other module-level call, and reads made at module level or in a class body. See [`build/source/python_define_reads_import.py`](#buildsourcepython_define_reads_importpy). |
| `resource-cache-direct:` | a runtime Python lookup reads a resource directly instead of through its shared cache, for the concrete reason given | that a reason follows the token, and every other lookup. See [`build/source/python_resource_api.py`](#buildsourcepython_resource_apipy). |
| `sas-ci-string-compare-exemption:` | a runtime Python comparison with a short string literal is right as it is, such as a BUG option type | every other such comparison. See [`build/source/string_label_compares.py`](#buildsourcestring_label_comparespy). |

## Run Locally

[`ci_report.py`](/LLM_Helpers/README.md#ci_reportpy) runs every workflow's steps and writes all failures to one file, `LLM_Helpers/outputs/ci_report.txt`:

```bash
python LLM_Helpers/audits/ci_report.py
```

Each check step in `checks-*.yml` has `if: ${{ !cancelled() && steps.setup.outcome == 'success' }}`, so it runs even after an earlier check failed; the job still fails, and a failed setup still stops the checks. Give a new check step the same line. [`workflow_keep_going.py`](#buildrepositoryworkflow_keep_goingpy) enforces it.

Checks collect every problem and fail at the end, because each fix-and-rerun round is costly: the user waits for GitHub and pushes again, often force-pushing an amended commit, and an agent repeats a full run for one more error.

- Seeing all problems at once also shows when several share one cause.
- Stop early only when later results would mean nothing, such as a file that cannot be parsed. For example, `xml_text_duplicate_tags.py` used to return on a parse error and hide the duplicates it had already found.

Note for LLMs/Users: a single check can also be run locally, for example on Git Bash:

```bash
py "C:\Program Files (x86)\Steam\steamapps\common\Sid Meier's Civilization IV Beyond the Sword\Beyond the Sword\Mods\AdvCiv-SAS\.github\workflows\build\diagnostics\bbai_log.py"
```

## Not currently automated

The Python UI markup-escaping rule from `AGENTS.md` is intentionally not checked here yet. Raw dynamic/user text that reaches font-tagged UI renderers (`screen.setText`, `screen.setLabel`, `SASTextScale.labelText`, etc.) should keep raw text in state and escape only the display string (`&`, `<`, `>`), but broad static scanning would produce too many false positives in normal Python code, comparisons, comments, already-escaped text, and non-user-facing strings.

Only add a build check for this if it can be made targeted to a known risky path, such as a specific Sevopedia search-label rendering function or another function that displays raw user-entered text.

## Dependabot

[`.github/dependabot.yml`](/.github/dependabot.yml) enables Dependabot version updates for GitHub Actions. It is currently scheduled daily for initial testing so outdated action versions such as `actions/checkout` and `actions/setup-python` can produce an update PR quickly. If this becomes noisy, change the schedule to weekly or monthly.

For example, as of 2026-06-09, this was added to help address the following GitHub Actions maintenance warning, after which Dependabot was added to track action-version updates automatically:

```text
build-checks
Node.js 20 actions are deprecated. The following actions are running on Node.js 20 and may not work as expected: actions/checkout@v4, actions/setup-python@v5. Actions will be forced to run with Node.js 24 by default starting June 16th, 2026. Node.js 20 will be removed from the runner on September 16th, 2026. Please check if updated versions of these actions are available that support Node.js 24. To opt into Node.js 24 now, set the FORCE_JAVASCRIPT_ACTIONS_TO_NODE24=true environment variable on the runner or in your workflow file. Once Node.js 24 becomes the default, you can temporarily opt out by setting ACTIONS_ALLOW_USE_UNSECURE_NODE_VERSION=true. For more information see: https://github.blog/changelog/2025-09-19-deprecation-of-node-20-on-github-actions-runners/
```

Which it fixed here: [dependabot@PR#24](https://github.com/wonderingabout/AdvCiv-SAS/pull/24).
