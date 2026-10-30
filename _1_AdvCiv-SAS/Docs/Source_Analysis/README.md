# Source Analysis

These tracked development records preserve LLM-assisted source investigations and their status. The folder is excluded from player release archives and generated historical commit patches, but its current files remain included in Git clones and AdvCiv-SAS light-source handoffs.

## Menu

- [Historical source archaeology](#historical-source-archaeology)
- [Current-tree audit albums](#current-tree-audit-albums)
- [Focused reviews](#focused-reviews)

## Historical source archaeology

[`historical_source_archaeology.txt`](/_1_AdvCiv-SAS/Docs/Source_Analysis/historical_source_archaeology.txt) records the completed commit-oriented BtS, K-Mod, AdvCiv and AdvCiv-SAS lineage sweep and subsequent repair status.

## Current-tree audit albums

[`cpp_file_audit_album.txt`](/_1_AdvCiv-SAS/Docs/Source_Analysis/cpp_file_audit_album.txt) preserves the currently discontinued C++ file and cross-file contract sweep.

As of 2026-10-30, development focuses on targeted AI changes and existing pending Known Issues; substantial intervening source changes make the old sweep unsuitable as a current-tree coverage claim.

Its findings and continuation cursor remain historical evidence, and it currently no longer reserves new KI numbers. Future file-oriented reviews can still belong beside it.

## Focused reviews

[`global_define_name_length_review.md`](/_1_AdvCiv-SAS/Docs/Source_Analysis/global_define_name_length_review.md) documents the completed GlobalDefine cleanup and current naming policy/census, compares it with inherited/reference XML, and separates the 42-byte desired naming maximum from KI#1001's hard 255-byte loader boundary.

Keep canonical filenames stable across checkpoints. Preserve each audit's completed results, false positives and exact continuation cursor; reconcile provisional KI numbers against current Known Issues before promotion.
