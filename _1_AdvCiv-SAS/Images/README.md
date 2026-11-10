# AdvCiv-SAS documentation images

This tree contains maintained AdvCiv-SAS screenshots and other documentation/reference images.

## Menu

- [Image numbering and naming](#image-numbering-and-naming)

## Image numbering and naming

Numbered AdvCiv-SAS image series use the `1.x` namespace. The corresponding legacy/base-AdvCiv reference tree uses `0.x` under [`_0_Legacy/Images/`](/_0_Legacy/Images/), making the source generation visible in filenames without changing the established category numbers inside each SAS series.

For example, existing SAS families such as main-menu `1.3xx`, UI `1.4xx`, advisor `1.5xx`, Sevopedia `1.6xx+`, and late/misc screen `1.9xx` retain the same suffix/grouping that they had before the namespace split; only the leading `0.` became `1.`. Descriptive unnumbered image names remain valid where a numbered series is not useful.

Image basenames are kept unique across `_0_Legacy/Images/` and `_1_AdvCiv-SAS/Images/`. This makes screenshots easier to identify in documentation, logs, agent handoffs and filename searches without depending on the containing folder to disambiguate them.

The two-client LAN walkthrough screenshots (`1.297_m_*`) have their own folder, [`multiple_instances/`](/_1_AdvCiv-SAS/Images/multiple_instances/), named after [README_Multiple_Instances.md](/_1_AdvCiv-SAS/Docs/README_Multiple_Instances.md) that shows them, rather than `diagnostics/`: they show the game's own menus, lobby and chat, not output from a diagnostic recorder.
