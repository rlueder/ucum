# Working in this repository

UCUM publishes a specification, unit definitions, and XSLT publishing tools.
It does not contain a runtime validator or converter.

## Contribution workflow

- Keep development and review in the contributor's fork (`origin`). Open
  upstream PRs only when the user explicitly requests them.
- Post upstream issue comments only when requested. Keep outreach to a concise
  comment linking to the relevant fork PR; avoid batch submissions.
- Keep each PR focused. Check its base branch so it contains only the intended
  changes, and identify any dependency on another PR.
- Use Conventional Commits for commit messages and PR titles, such as
  `docs: clarify table headings` or `fix: correct case-insensitive references`.
- When a change is based on an upstream issue, link its full URL in the PR body
  using a reference such as `ucum-org/ucum#419`. Distinguish direct fixes from
  related context, and preserve these references in merged PR descriptions.

## Writing for reviewers

- Start PR descriptions with a sentence explaining the problem and why it
  matters, then show concrete before/after examples. For example,
  `MHO = 1 S` becomes `MHO = 1 SIE`: in the case-insensitive system, `S` means
  seconds and `SIE` means siemens.
- Use a short paragraph or small comparison table, followed by the validation
  command and result. Include implementation details only when needed to assess
  the change.
- Keep review comments and progress updates brief, usually one or two sentences.
  State the finding or decision; omit work diaries and repeated summaries.

## Sources and generated files

- Edit `ucum-source.xml` for specification prose and definitions; edit
  `build/*.xsl` for publishing behavior.
- Rebuild affected artifacts: `ucum.xml`, `ucum.html`, `ucum-essence.xml`,
  `ucum-cs.units`, and `ucum-ci.units`. Preserve existing line endings and avoid
  unrelated formatting changes.
- Preserve the distinction between `Code`/`Unit` and `CODE`/`UNIT`. Do not derive
  case-insensitive symbols by blindly uppercasing case-sensitive symbols.
- For scientific or normative corrections, cite primary evidence and show
  independently derived expected values. Preserve intentional aliases and
  distinguish proposed new definitions from corrections.

## Validation

- Publishing uses GNU Make, Java 17, and the bundled `build/saxon8.jar`.
  Regression tests use Python's standard library.
- For XML/XSLT changes, rebuild with `make -B` in a temporary copy and run
  `python3 -B -m unittest discover -s tests`. Use `make check` when available.
- Check generated definitions and both code systems. Publishing checks do not
  establish runtime UCUM conformance.
- For documentation-only changes, check examples, links, and `git diff --check`.
  Add regression tests for behavioral changes, not tests that merely repeat prose.
