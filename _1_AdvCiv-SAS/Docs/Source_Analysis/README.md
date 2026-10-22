# Source Analysis

These tracked development records preserve resumable LLM-assisted source investigations. The folder is excluded from player release archives and generated historical commit patches, but its current files remain included in Git clones and AdvCiv-SAS light-source handoffs.

## Historical source archaeology

[`historical_source_archaeology.txt`](/_1_AdvCiv-SAS/Docs/Source_Analysis/historical_source_archaeology.txt) records the completed commit-oriented BtS, K-Mod, AdvCiv and AdvCiv-SAS lineage sweep and subsequent repair status.

## Current-tree audit albums

[`cpp_file_audit_album.txt`](/_1_AdvCiv-SAS/Docs/Source_Analysis/cpp_file_audit_album.txt) reviews current C++ files and cross-file contracts. Future Python, XML or other file-oriented albums belong beside it.

## Focused reviews

[`global_define_name_length_review.md`](/_1_AdvCiv-SAS/Docs/Source_Analysis/global_define_name_length_review.md) documents the completed GlobalDefine cleanup and current naming policy/census, compares it with inherited/reference XML, and separates the 42-byte desired naming maximum from KI#1001's hard 255-byte loader boundary.

Keep canonical filenames stable across checkpoints. Preserve each audit's completed results, false positives and exact continuation cursor; reconcile provisional KI numbers against current Known Issues before promotion.
