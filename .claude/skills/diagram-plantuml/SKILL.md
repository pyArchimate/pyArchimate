---
name: diagram-plantuml
description: Author, validate, and render PlantUML diagrams (sequence, class, component, deployment, activity, state, ERD, etc.). Use by default whenever a diagram is requested as PlantUML or `.puml`/`.plantuml`, or when adding/editing diagrams in docs where PlantUML is already the convention. Validates syntax against the local `plantuml` binary when installed, falling back to the public PlantUML server, and consults the online PlantUML docs when syntax is uncertain.
---

# diagram-plantuml

Default workflow for producing PlantUML diagrams. Write the diagram from
knowledge first; reach for the online docs only when syntax is genuinely
uncertain; always validate before handing back.

## Steps

1. **Write the diagram.** Use fenced `@startuml` / `@enduml` (or
   `@startmindmap`, `@startgantt`, etc.). Prefer explicit, readable names;
   add a `title`. Keep skinparam tweaks minimal unless the surrounding docs
   already use them.

2. **Validate syntax.** In order of preference:
   - **Local binary** — check with `command -v plantuml`. If present:
     `plantuml -checkonly -failfast2 path/to/diagram.puml`
     (exit 0 = clean). To also produce output: `plantuml -tsvg` / `-tpng`.
     No file yet? Pipe it: `plantuml -failfast2 -checkonly -pipe < diagram.puml > /dev/null`
     (only errors print; exit code is what matters).
   - **No local binary** — check for `java` + a local `plantuml.jar`, then
     fall back to the **public server**: POST the source to
     `https://www.plantuml.com/plantuml/svg/` using the standard
     hex/deflate encoding, or use WebFetch against a rendered URL. Note in
     your reply that validation used the public server (source leaves the
     machine).
   - **No network either** — state clearly that the diagram is
     unvalidated and eyeball it against known syntax.

3. **Fix and re-validate** until clean. Read the parser error line/column;
   most failures are a missing arrow token, unbalanced `{}`/`note`, or a
   participant used before declaration.

4. **Render if asked** (`-tsvg` preferred for docs, `-tpng` for chat).
   Place output next to the source unless told otherwise.

5. **Report** the file path(s), how validation was done (local / server /
   none), and any rendering output.

## Reference docs (fallback only)

When a diagram type or directive is unfamiliar, use WebFetch against the
official docs — do not consult them for routine diagrams:

- Per-diagram-type pages: `https://plantuml.com/sequence-diagram`,
  `/class-diagram`, `/component-diagram`, `/deployment-diagram`,
  `/activity-diagram-beta`, `/state-diagram`, `/mindmap-diagram`, etc.
- Language reference guide (HTML): `https://plantuml.com/guide`
- Command-line options: `https://plantuml.com/command-line`

If offline, fall back to known syntax and flag the diagram as
docs-unverified.

## Conventions

- One diagram per `.puml` file; name it after what it shows.
- Match the diagram style already present in the target docs.
