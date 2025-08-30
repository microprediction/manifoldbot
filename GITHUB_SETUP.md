# GitHub Setup for ManifoldBot Tests

## Quick Setup

To make tests pass in GitHub, you just need to:

### 1. Add Repository Secrets

Go to your GitHub repository → Settings → Secrets and variables → Actions

Add these secrets:

- **`MANIFOLD_API_KEY`**: Your Manifold Markets API key
- **`OPENAI_API_KEY`**: Your OpenAI API key (optional)

### 2. That's it!

The GitHub Actions workflow will:
- Load the secrets into environment variables
- Run the exact same tests as locally: `pytest tests/ -v`
- Test across Python 3.9, 3.10, 3.11, 3.12
- Generate coverage reports

## How to Get API Keys

### Manifold API Key
1. Go to [manifold.markets](https://manifold.markets)
2. Sign in → Account Settings → API
3. Generate new API key

### OpenAI API Key (Optional)
1. Go to [platform.openai.com](https://platform.openai.com)
2. Sign in → API Keys
3. Create new secret key

## Testing Locally

Same setup as GitHub:

```bash
export MANIFOLD_API_KEY="your_key"
export OPENAI_API_KEY="your_key"
pytest tests/ -v
```

## What Tests Run

- **Unit tests**: Mocked API tests (always pass)
- **Real API tests**: Tests with actual Manifold API calls (need API key)
- **Writer tests**: Authentication and trading functionality tests

The tests will automatically skip real API tests if no API key is provided, so the workflow will still pass even without secrets.
