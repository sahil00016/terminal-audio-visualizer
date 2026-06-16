# Claude Code — Project Rules

## Git workflow (ALWAYS follow this)

1. **Never commit directly to `main`.** Always create a feature branch first:
   ```
   git checkout -b <type>/<short-description>
   ```
2. **Commit messages must follow Conventional Commits:**
   ```
   <type>(<scope>): <description>
   ```
   Allowed types: `feat` `fix` `docs` `style` `refactor` `test` `chore` `ci` `perf` `build` `revert`
   Example: `feat(ui): add seek-bar keyboard shortcut`

3. **Never add `Co-Authored-By: Claude` or any AI tag** to commit messages.

4. **Open a PR** from the feature branch to `main` using `gh pr create` after pushing.

5. **Branch protection is enabled on `main`.** Force-push to main is blocked.

## Pre-commit hooks

Run before committing:
```bash
pre-commit install          # first time only
pre-commit run --all-files  # manual check
```

Hooks enforce: trailing whitespace, end-of-file newlines, YAML/JSON/TOML validity,
no debug statements, ruff linting + formatting, conventional commit message format.

## Docs to update on significant changes

- `docs/HLD.md`  — high-level architecture, system context, data flow
- `docs/LLD.md`  — module-level interface and algorithm notes
- `docs/ERD.md`  — entity relationships, state machines, sequence diagrams
- `CHANGELOG.md` — add entry under the next unreleased version

## Testing

```bash
pytest tests/ -v
```

All new modules need unit tests in `tests/test_<module>.py`.

## Code conventions

- Python 3.9+, type hints, `from __future__ import annotations`
- `ruff` for linting and formatting (config in `ruff.toml`)
- No `print()` inside library modules — only in `__main__.py`
- No `Co-Authored-By` in commits
