# Subsystem revisions

Some AdvCiv-SAS subsystems carry a revision number: a signal that the subsystem changed, so a downstream copy, parser or tool that supports revision N and meets N+1 knows to review its copy. It is not a compatibility promise.

The rules below are shared by every such subsystem, today the SASGameRecord and Runtime recorders, and any later one; each subsystem's history doc adds only what is its own, such as what counts as a change to it.

| Subsystem | Revision define | History | What counts as a change |
| --- | --- | --- | --- |
| SASGameRecord | `SAS_SGR_REVISION` | [SASGameRecord.md](/_1_AdvCiv-SAS/Docs/revisions/SASGameRecord.md) | its [Revision policy](/_1_AdvCiv-SAS/Docs/revisions/SASGameRecord.md#revision-policy) |
| Runtime | `SAS_RUNTIME_REVISION` | [SASRuntime.md](/_1_AdvCiv-SAS/Docs/revisions/SASRuntime.md) | its opening paragraphs |

## Shared rules

- Increment the revision once for each commit that changes the subsystem, its code comments included; never twice in one commit, never skip a number and never go back.
  - When in doubt, increment: do not debate whether a change is compatible or changes behavior.
  - Changes to documentation, history, examples or packages alone need no increment.
- The revision is a define in `Assets/XML/GlobalDefines_advciv_sas.xml`, so a Python-only revision needs no DLL rebuild; DLL, build and source provenance identify the loaded native code separately.
- Each increment adds a latest-first entry to the subsystem's history:

```markdown
### Revision N - SAS practical XXXX

- **Date:** YYYY-MM-DD
- **Git commit:** pending
- **Change:** What changed in the subsystem, and why it matters to its downstream users.
```

- Its **Git commit** says `pending` in the commit that introduces it, since a commit cannot contain its own SHA; the next commit fills it in, even if that commit does not change the subsystem. Only the newest entry may stay pending.
  - Never write the commit's own SHA into its entry: editing the document would change that SHA again.
- After an amend, rebase or squash, update the SHAs and practical numbers the histories cite; an ordinary merge keeps the original commits.
- A PR intended to be squash-merged carries [`[ci_squash_pr]`](/.github/workflows/README.md#ci-markers-in-commit-messages) in its newest commit message: the whole PR then needs exactly one increment, and its intermediate commits may bump and fold back, as PR#50's 210, 211 and 210 did (2026-11-22).
- CI checks all of this: [`sas_revision_history.py`](/.github/workflows/README.md#builddiagnosticssas_revision_historypy), [`runtime_revision_history.py`](/.github/workflows/README.md#builddiagnosticsruntime_revision_historypy) and [`revision_commit_references.py`](/.github/workflows/README.md#builddiagnosticsrevision_commit_referencespy).
