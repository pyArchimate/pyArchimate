# Data Model: AI-Optimized Documentation

## Entities

### AI-Doc Artifact
Represents the generated `AI.md` documentation.
- **Fields**:
  - `path`: string
  - `content`: string
  - `checksum`: string

## Validation Rules
- Valid Markdown syntax required.
- Mandatory sections (Summary, Overview, Core Purpose, etc.) MUST exist.

## State Transitions
- `raw_source` -> `ai_generated` -> `validated_doc`
EOF
