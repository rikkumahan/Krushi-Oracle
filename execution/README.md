# Execution Scripts

This directory contains deterministic Python scripts that handle the actual work—API calls, data processing, file operations, etc.

## Principles

1. **Deterministic**: Same inputs → Same outputs
2. **Well-commented**: Code should be self-documenting
3. **Testable**: Each script should be runnable standalone
4. **Single responsibility**: One script, one job

## Creating New Scripts

Use `_template.py` as a starting point:
1. Copy the template: `cp _template.py new_script.py`
2. Update the docstring with purpose, inputs, outputs
3. Implement the logic
4. Test standalone before integrating

## Environment Variables

Scripts read secrets from `.env` in the project root. Use `python-dotenv`:

```python
from dotenv import load_dotenv
load_dotenv()

api_key = os.getenv("API_KEY")
```

## Testing

Run any script directly:
```bash
python execution/script_name.py --help
```
