# Source audit

As of the first working build:

- Original report: `Scenarios (1).pdf`, 42 pages, 32 numbered cases.
- Original diagram files: `scenario1.png` through `scenario32.png` (32 files).
- Dialogue references: the supplied photos `IMG_6224 3.JPG` (decision tree)
  and `IMG_6223 3.JPG` (seven types table). Their content is summarized in
  `labeling_guide.md`.
- Proposed additions: 10 authored cases (33–42), stored separately from the
  original report. They are not faculty-approved original data.
- Original case extraction: 32 JSON records. All have a scenario, entities,
  communication type, description, and dialogue prompt text. Some later
  cases omit solutions, PEAS, or cascading problems in the source. Run
  `python3 scripts/audit_sources.py` for the exact field counts.
- Review status: all 32 original records are **machine extracted, pending
  human review**. No definitive dialogue label has been assigned to them.
- Diagram mapping: **unverified** in the data. The filenames are not reliable
  case numbers. The earlier compatibility review inspected class names and
  operations in all 32 images; it found that image 14 is byte-identical to
  image 8. A full written-case ↔ diagram mapping still requires individual
  content review with the faculty or student.

The application uses the written case text as retrieval data. It does not
pretend the incomplete diagram mapping is a verified training label. The
diagram vocabulary guides participant names and future annotation.
