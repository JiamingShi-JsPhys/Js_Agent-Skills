# Test Fixtures

This directory holds static sample data for tests (if needed). The current
test suite mainly uses dynamically built `tmp_path`-based fixtures in
`tests/conftest.py` (`sample_task`, `empty_task`, `task_with_readonly`),
so only one example file is kept here to demonstrate the "static fixture"
conventions.

## Conventions

- Use ASCII file names to avoid platform encoding issues.
- Put any binary files (e.g. `.xlsx` samples) here; tests locate them via
  `Path(__file__).parent`.
- Do not commit fixtures larger than 100KB; put large samples in CI
  artifacts or object storage.
