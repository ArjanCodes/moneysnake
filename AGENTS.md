# Moneysnake

Python client library for the Moneybird accounting API, published on PyPI as `moneysnake`.
Python 3.12+, httpx for HTTP, pydantic v2 for models, uv for tooling, hatchling for builds.

## Commands

```sh
uv sync                  # install runtime and dev dependencies
uv run pytest -q         # run the tests (CI runs this on every PR)
uv run mypy moneysnake   # typecheck (not in CI, run it yourself)
uv build                 # build sdist and wheel into dist/
```

There is no linter or formatter config. Match the style of the code around your change.

## Structure

- `moneysnake/client.py`: module-level config (`set_token`, `set_admin_id`, ...), the `http_*` helpers, retries, and `paginate`. All HTTP goes through here.
- `moneysnake/model.py`: the base model and the capability mixins `Loadable`, `Saveable`, `Deletable`, `Synchronizable`, and `CrudModel`.
- `moneysnake/exceptions.py`: the error hierarchy. Every error is a `MoneybirdError`, split into transient and permanent. The README lists it.
- One module per Moneybird resource. `document.py` is the shared base for purchase invoices and receipts.
- `moneysnake/__init__.py`: the public API. Export every new public name here and in `__all__`.

## Conventions

- A resource class subclasses only the mixins for the operations Moneybird supports for it. Do not use `CrudModel` if the API has no delete or update.
- The endpoint comes from the class name in snake_case plus `s`. Set the private `_endpoint` attribute only when that is wrong.
- Fields are optional with a default (`str | None = None`). Models use `extra="ignore"`, so unknown API fields are dropped.
- Writes send only the fields that are set (`model_dump(exclude_unset=True)`). Override `_write_data` to shape a write payload, for example nested `*_attributes`.
- Nested detail rows subclass `Updatable`, not `BaseModel`. Use `ensure_list_of` to turn dicts into models.
- Base fields and fixtures on the Moneybird API reference. Do not guess field names or types.
- Keep `uv run mypy moneysnake` clean. Add full type hints to new code.

## Tests

- Tests never call the real API. They patch the `http_*` helper where the module under test looks it up, for example `mocker.patch("moneysnake.model.http_patch")` or `mocker.patch("moneysnake.sales_invoice.http_post")`.
- Tests for client behavior (retries, errors, pagination) patch `moneysnake.client.httpx.request` and return real `httpx.Response` objects. They also patch `moneysnake.client.time.sleep`.
- `tests/conftest.py` holds full response fixtures that follow the Moneybird API response schemas. Reuse them and keep them realistic.
- Write a test that fails without your change.

## Releases

- `.github/workflows/release.yaml` builds the package and publishes it to PyPI through trusted publishing. It runs when a version tag such as `1.2.3` or `1.2.3rc1` is pushed, and it fails if the version is not newer than the one on PyPI.
- The workflow sets the version from the tag. A maintainer also bumps `version` in `pyproject.toml` in a `chore: bump version to X.Y.Z` commit.
- Agents never tag, release, or publish to PyPI by hand.

## Commits and PRs

- Use Conventional Commits, for example `fix: accept decimal numbers for detail price`.
- One change per PR, against `main`.
