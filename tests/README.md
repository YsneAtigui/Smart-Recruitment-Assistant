# Testing Framework for Smart Recruitment Assistant

This directory contains comprehensive tests for the Smart Recruitment Assistant using pytest.

## Structure

```
tests/
├── conftest.py              # Shared fixtures
├── fixtures/                # Test data and fixtures
├── unit/                    # Unit tests
│   ├── test_models.py      # Entity model tests
│   ├── test_validation.py  # Validation tests
│   ├── test_scoring.py     # Scoring function tests
│   ├── test_skills.py      # Skill matching tests
│   └── test_embeddings.py  # Embedding generation tests
└── integration/             # Integration tests
    ├── test_integration.py # Integration helper tests
    └── test_matcher.py     # AdvancedMatcher tests
```

## Running Tests

### Install Dependencies

```bash
pip install pytest pytest-cov pytest-mock
```

### Run All Tests

```bash
pytest
```

### Run Specific Test Types

```bash
# Unit tests only
pytest -m unit

# Integration tests only
pytest -m integration

# Exclude slow tests
pytest -m "not slow"
```

### Run with Coverage

```bash
pytest --cov=src --cov-report=html
```

The coverage report will be generated in `htmlcov/index.html`.

### Run Specific Test File

```bash
pytest tests/unit/test_models.py
pytest tests/integration/test_matcher.py
```

### Run with Verbose Output

```bash
pytest -v
```

## Test Markers

- `@pytest.mark.unit` - Unit tests
- `@pytest.mark.integration` - Integration tests
- `@pytest.mark.slow` - Slow tests (e.g., embedding generation, API calls)
- `@pytest.mark.requires_gemini` - Tests requiring Gemini API

## Writing New Tests

### Using Fixtures

```python
def test_my_function(sample_cv_entity, sample_jd_entity):
    """Test with pre-built entities."""
    result = my_function(sample_cv_entity, sample_jd_entity)
    assert result is not None
```

### Available Fixtures

- `sample_cv_text` - Raw CV text
- `sample_jd_text` - Raw JD text
- `sample_cv_data` - Structured CV dictionary
- `sample_jd_data` - Structured JD dictionary
- `sample_cv_entity` - Complete CV entity with embedding
- `sample_jd_entity` - Complete JD entity with embedding
- `mock_embedding` - Mock embedding vector
- `mock_gemini_cv_response` - Mock Gemini CV response
- `mock_gemini_jd_response` - Mock Gemini JD response

### Mocking Gemini API

```python
def test_with_gemini_mock(mocker, mock_gemini_cv_response):
    """Test with mocked Gemini API."""
    mock_response = mocker.Mock()
    mock_response.text = mock_gemini_cv_response
    
    mocker.patch(
        'src.extraction.genai_model.generate_content',
        return_value=mock_response
    )
    
    # Your test code here
```

## Coverage Goals

- **Overall:** >80%
- **Critical modules:** >90%
  - models.py
  - integration.py
  - matcher.py

## Continuous Integration

These tests are designed to run in CI/CD pipelines. Example GitHub Actions workflow:

```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
      - run: pip install -r requirements.txt
      - run: pytest --cov=src --cov-report=xml
```

## Troubleshooting

### "Module not found" errors

Make sure you're running pytest from the project root:

```bash
cd /path/to/SmartRecru
pytest
```

### Slow tests

Skip slow tests during development:

```bash
pytest -m "not slow"
```

### API rate limits

Use mocking for Gemini API tests to avoid rate limits and costs.
