# Quickstart: Modular Model Modules

1. **Setup the environment**  
   - `poetry install` (ensures Python >=3.10 and all dev dependencies are available).  
   - `uv venv use <name>` / `poetry shell` if you prefer an isolated shell.  

2. **Verify the refactor**  
   - `poetry run pytest` to execute the full suite (unit, integration, examples); confirm the new modules expose the same API as before.  
   - `poetry run ruff check src tests` to enforce style (line length ≤120, etc.).  
   - `poetry run pyright` / `mypy` as needed to catch import and typing issues.  

3. **Regenerate documentation**  
   - Update `docs/diagrams/package.puml` (and any other impacted `.puml` file such as `class.puml`) so the new module boundaries are depicted before generating images.  
   - `scripts/render_diagrams.sh` to refresh the PlantUML outputs so `docs/diagrams.rst` matches the modular structure.  
   - `scripts/create_documentation.sh` to rebuild the Sphinx site after the diagrams are updated.  

4. **Package sanity checks**  
   - `poetry check` to ensure the `src` layout and exports remain valid (pyArchimate package still publishes `Model`, `Element`, `Relationship`).

5. **Additional validation**  
   - Confirm `pyArchimate/__init__.py` re-exports the new helper modules (`helpers.diagram`, `helpers.properties`, `helpers.logging`).  
   - Ensure reader/writer scripts continue resolving `pyArchimate.Model` without touching the new modules directly.
