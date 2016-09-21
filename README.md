# Dash Sentinel

An all-powerful toolset for Dash.

Sentinel is an autonomous agent for persisting, processing and automating Dash V12.1 governance objects and tasks, and for expanded functions in the upcoming Dash V13 release (Evolution).

Sentinel is implemented as a Python application that binds to a local MySQL and v12.1 dashd instance on each Dash V12.1 Masternode.

This guide covers installing Sentinel onto an existing 12.1 Masternode in Ubuntu 14.04 / 16.04.

## Installation

### 1. Install Components

Make sure Python version 2.7.x is installed, 3.x and above are not supported

    python --version

Install MySQL Server 5.7.x and Sentinel dependencies, making sure you enter a strong root password when asked. Newer versions may have breaking changes.

    $ sudo apt-get update 
    $ sudo apt-get install mysql-server python-pytest
    $ sudo service mysql start

Make sure the local Dash daemon running is version 12.1 (120100), and is configured as a masternode

    $ dash-cli getinfo | grep '"version"'
    $ dash-cli masternode status | grep '"status"'

### 2. Get / Update Source

This section can be used to install Sentinel source or update it for new releases.

Clone the Sentinel code and install Python dependencies.

    $ git clone https://github.com/nmarley/sentinel.git && cd sentinel
    $ pip install -r requirements.txt

Recommended: Build the Sentinel database schemas from source and configure MySQL for Sentinel requirements.

    $ ./setup-mysql.sh

A reboot is recommended at this stage.

### 3. Setup Crontab

Setup a crontab to call Sentinel regularly, recommended every 2 minutes, by first opening a crontab editor.

    $ crontab -e

In the crontab editor, add the lines below, replacing '/home/YOURUSERNAME/sentinel' to the path where you cloned sentinel to:

    2 * * * * cd /home/YOURUSERNAME/sentinel && /usr/bin/python scripts/crontab.py >/dev/null 2>&1

### 4. Test the Configuration

Test the config by runnings all tests from the sentinel folder you cloned into

    $ py.test

With all tests passing and crontab setup, Sentinel will stay in sync with dashd and the installation is complete

## Troubleshooting

If data issues occur, you can reinitialize the database schema and data to the initial state by re-running the sql setup script.

    $ ./setup-mysql.sh

If Sentinel cannot communicate with dashd, check that RPC settings are configured in dash.conf...

    $ nano ~/.dashcore/dash.conf

...or if dash.conf is stored elsewhere, set a custom path in sentinel.conf with the dash\_conf parameter:

    $ nano sentinel.conf

To debug Sentinel's sync with dashd, run the crontab sync manually and examine the output

    $ python scripts/crontab.py

To run individual Sentinel tests, specify the test from the test folder, e.g.

    $ py.test test/test_config.py
    $ py.test test/test_jsonrpc.py
    $ py.test test/test_models.py

## Documentation

- [usage.md](docs/usage.md) - New system usage
- [conversion.md](docs/conversion.md) - How we will convert from 12.0 to 12.1
- [rules.md](docs/rules.md) - What the rules are for the new system
- [sentinel-cli.md](docs/sentinel-cli.md) - How to use the CLI to create and amend records
