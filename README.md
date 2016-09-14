# Dash Sentinel

An all-powerful toolset for Dash

## Installation

Requires Python 2.7 and a running MySQL database server

Make sure dashd is running at least v12.1.

Install Python dependencies via:

    pip install -r requirements.txt

## Documentation

- [usage.md](docs/usage.md) - New system usage
- [conversion.md](docs/conversion.md) - How we will convert from 12.0 to 12.1
- [rules.md](docs/rules.md) - What the rules are for the new system
- [sentinel-cli.md](docs/sentinel-cli.md) - How to use the CLI to create and amend records

## Testing

The py.test framework is used for testing. Please ensure the test database configured in config.py has been created. To run all tests from the top-level project directory, just run:

    py.test

Individual test files can be specified:

    py.test test/test_governance_methods.py
