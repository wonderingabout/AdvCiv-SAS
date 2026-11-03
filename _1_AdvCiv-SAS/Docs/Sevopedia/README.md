# Sevopedia development references

This folder contains static Sevopedia development/reference artifacts rather than runtime Python modules.

## Debug dumps

[`Debug/`](/_1_AdvCiv-SAS/Docs/Sevopedia/Debug/) contains Python API introspection dumps captured while developing Sevopedia pages. They are useful when a getter is missing or unclear because they record what the Civ4 Python objects exposed when the dumps were generated.

The dumps can become stale after DLL/Python-binding changes, so prefer a fresh runtime inspection when current behavior matters. The helper code that generates or assists these inspections remains in [`_sevopedia_debuggers.py`](/Assets/Python/Contrib/Sevopedia/_sevopedia_debuggers.py); only the static output files were moved out of the runtime source tree.
