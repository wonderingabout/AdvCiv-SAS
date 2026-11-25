# Subsystem revisions

Some AdvCiv-SAS subsystems carry a revision number: a signal that the subsystem changed, so a downstream copy, parser or tool that supports revision N and meets N+1 knows to review its copy. It is not a compatibility promise.

Together with each history's entries, the revisions trace which commit changed what in a recorder, in any respect, so whoever keeps a copy of one, a mod reusing our recorders or we ourselves in another branch, may find it easier to follow the changes since the revision it started from and stay in sync.

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
- **Functional:** Yes, or No (brief reason)
- **Change:** What changed in the subsystem, and why it matters to its downstream users.
```

- Its **Functional** line says `Yes` when the change altered what the subsystem records, publishes or does, such as a new row or field, a changed value, gate, file name or timing, and `No` with a brief reason in parentheses when it touched only comments, layout, names with no change in output, docs or tooling, such as `No (comments only)`.
  - A `Yes` needs no reason, as its Change text says what behavior changed; a `No`'s reason lets a reader checking for behavior changes see at a glance why it can skip that revision, without reading its Change text.
  - Since the revision counts comment changes too, a reader of the history needs this line to tell which revisions changed behavior without reading each Change text; before 2026-11-25 only 3 of 230 entries said so, as "Comments only" or "Layout only".
  - The labels of entries older than 2026-11-25 were added then from each entry's description, checking the commit where it was unclear, so they are our reading and may be wrong; correct one when evidence shows it.
  - CI requires exactly one such line on every entry, and a commit adding a revision after SASGameRecord 211 or Runtime 19, the last ones written before the line existed, must label it in that same commit.
- Its **Change** text is a lead sentence, then child bullets for the details, such as the rows and fields added; CI rejects a loose paragraph after the list, since it renders outside the entry, as 193 did in revisions 80 to 149 until 2026-11-25.
- Its **Git commit** says `pending` in the commit that introduces it, since a commit cannot contain its own SHA; the next commit fills it in, even if that commit does not change the subsystem. Only the newest entry may stay pending.
  - Never write the commit's own SHA into its entry: editing the document would change that SHA again.
- A commit that edits earlier entries, beyond filling in a pending SHA, says which ones and how, so a later correction can trace what changed: in its own entry when it bumps the revision, as SASGameRecord 212 lists its relabeled, detailed and reformatted entries, or in its commit message when it edits history alone, which needs no increment.
- After an amend, rebase or squash, update the SHAs and practical numbers the histories cite; an ordinary merge keeps the original commits.
- A PR intended to be squash-merged carries [`[ci_squash_pr]`](/.github/workflows/README.md#ci-markers-in-commit-messages) in its newest commit message: the whole PR then needs exactly one increment, and its intermediate commits may bump and fold back, as PR#50's 210, 211 and 210 did (2026-11-22).
- CI checks all of this: [`sas_revision_history.py`](/.github/workflows/README.md#builddiagnosticssas_revision_historypy), [`runtime_revision_history.py`](/.github/workflows/README.md#builddiagnosticsruntime_revision_historypy) and [`revision_commit_references.py`](/.github/workflows/README.md#builddiagnosticsrevision_commit_referencespy).
