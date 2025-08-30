# Changelog

All notable changes to this project will be documented in this file.

## [0.1.0] - 2025-01-30

### Added
- **ManifoldReader**: Read-only access to Manifold Markets API
  - `get_markets()` - Get list of markets with pagination
  - `get_market()` - Get specific market by ID
  - `get_market_by_slug()` - Get market by slug
  - `get_user()` - Get user information
  - `get_user_markets()` - Get markets created by a user
  - `get_market_bets()` - Get bets on a specific market
  - `search_markets()` - Search markets by query

- **ManifoldWriter**: Authenticated access for trading and market management
  - `place_bet()` - Place market and limit orders
  - `place_limit_yes()` / `place_limit_no()` - Convenience methods for limit orders
  - `cancel_bet()` - Cancel pending bets
  - `get_bet()` - Get bet details
  - `create_market()` - Create new markets
  - `close_market()` - Close markets with resolution
  - `get_balance()` - Get current balance
  - `get_portfolio()` - Get portfolio summary
  - `get_positions()` - Get user positions
  - `post_comment()` - Post comments on markets
  - `get_me()` - Get authenticated user info
  - `update_user()` - Update user profile
  - `calculate_market_impact()` - Calculate bet impact on market probability
  - `place_bet_with_impact_limit()` - Place bets with impact limits
  - `is_authenticated()` - Check authentication status

- **Configuration Management**
  - Pydantic-based settings with YAML and environment variable support
  - Automatic API key loading from environment variables
  - Configurable retry logic and timeouts

- **Comprehensive Testing**
  - Unit tests with mocked API calls
  - Real API integration tests
  - GitHub Actions CI/CD pipeline
  - Test coverage for all major functionality

- **Documentation**
  - Complete API reference
  - Tutorial with examples
  - Quick start guide
  - Best practices and error handling guides

- **Package Distribution**
  - `setup.py` for package installation
  - `MANIFEST.in` for including non-code files
  - Support for development and test dependencies

### Technical Details
- Built on top of `requests` library with retry logic
- Full type hints throughout the codebase
- Proper error handling for API failures
- Support for both market orders and limit orders
- Automatic expiration handling for limit orders (6 hours default)
- Rate limiting and retry logic for robust API interactions

### API Compatibility
- Compatible with Manifold Markets API v0
- Supports all major trading operations
- Handles pagination for list endpoints
- Graceful handling of API limitations (some endpoints marked as NotImplemented)

### Dependencies
- `requests` - HTTP client
- `pydantic` - Data validation and settings
- `PyYAML` - YAML configuration support
- `python-dotenv` - Environment variable loading
- `click` - Command-line interface
- `loguru` - Logging

### Development Dependencies
- `pytest` - Testing framework
- `flake8` - Linting
- `black` - Code formatting
- `isort` - Import sorting
- `pytest-mock` - Mocking utilities
- `requests-mock` - HTTP request mocking
