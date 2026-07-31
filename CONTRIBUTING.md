# Contributing to ThreatVision AI

Thank you for your interest in contributing to **ThreatVision AI**! We welcome contributions from developers, researchers, and security specialists worldwide.

## Code of Conduct
Please review and adhere to our [Code of Conduct](CODE_OF_CONDUCT.md).

## Development Setup

1. Fork and clone the repository:
   ```bash
   git clone https://github.com/your-username/threatvision-ai.git
   cd threatvision-ai
   ```

2. Create a virtual environment and install in editable mode with development dependencies:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -e ".[dev,ml]"
   ```

3. Run test suite:
   ```bash
   pytest
   ```

## Code Style & Guidelines
- Code formatting: Run `black .` and `ruff check . --fix`.
- Type hint annotations are required for all public methods and functions.
- Follow Clean Architecture and SOLID principles.

## Pull Request Process
1. Create a descriptive feature branch (`git checkout -b feature/my-detector`).
2. Include unit tests for all new detectors or features.
3. Ensure test coverage remains >= 95%.
4. Submit your Pull Request detailing the changes and safety implications.
