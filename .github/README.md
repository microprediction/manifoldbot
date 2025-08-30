# GitHub Actions Setup

This directory contains GitHub Actions workflows for testing ManifoldBot.

## Required Repository Secrets

To run the full test suite, you need to add these secrets to your GitHub repository:

### 1. Go to Repository Settings
- Navigate to your repository on GitHub
- Click on "Settings" tab
- Click on "Secrets and variables" → "Actions"

### 2. Add Required Secrets

#### `MANIFOLD_API_KEY`
- **Description**: Your Manifold Markets API key
- **How to get**: 
  1. Go to [Manifold Markets](https://manifold.markets)
  2. Sign in to your account
  3. Go to Account Settings → API
  4. Generate a new API key
- **Required for**: Real API tests, authenticated operations

#### `OPENAI_API_KEY` (Optional)
- **Description**: Your OpenAI API key
- **How to get**:
  1. Go to [OpenAI Platform](https://platform.openai.com)
  2. Sign in to your account
  3. Go to API Keys section
  4. Create a new secret key
- **Required for**: AI-powered features (if implemented)

## Workflow

### `test.yml` - Complete Test Suite
- Runs on every push and PR to main/develop branches
- Tests across Python versions 3.9, 3.10, 3.11, 3.12
- Loads secrets into environment variables
- Runs the same tests as locally: `pytest tests/ -v`
- Includes coverage reporting on Python 3.12
- **Simple and straightforward** - just like running tests locally

## Local Testing

You can test locally with the same setup:

```bash
# Set environment variables (same as GitHub Actions)
export MANIFOLD_API_KEY="your_manifold_api_key"
export OPENAI_API_KEY="your_openai_api_key"

# Run the same tests as GitHub Actions
pytest tests/ -v

# Or run with coverage
pytest tests/ --cov=manifoldbot --cov-report=html
```

## Test Categories

### Unit Tests (No API Keys Required)
- `TestManifoldReader` - Mocked API tests
- `TestManifoldWriter` - Mocked API tests
- Package installation and basic functionality

### Real API Tests (API Keys Required)
- `TestManifoldReaderReal` - Real API integration tests
- Tests with actual Manifold Markets API calls
- Tests user market iteration (like MikhailTal's markets)

## Troubleshooting

### Tests Failing in GitHub Actions

1. **Check if secrets are set**:
   - Go to repository Settings → Secrets and variables → Actions
   - Ensure `MANIFOLD_API_KEY` is set

2. **Check API key validity**:
   - Verify the API key works locally
   - Ensure the key has necessary permissions

3. **Check rate limits**:
   - Manifold API has rate limits
   - Tests may fail if rate limits are exceeded

4. **Check network connectivity**:
   - GitHub Actions runners need internet access
   - Some corporate networks may block API calls

### Local Testing Issues

1. **Environment variables not set**:
   ```bash
   export MANIFOLD_API_KEY="your_key"
   export OPENAI_API_KEY="your_key"
   ```

2. **Package not installed**:
   ```bash
   pip install -e .
   ```

3. **Dependencies missing**:
   ```bash
   pip install -r requirements.txt
   ```
