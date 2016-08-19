import config

def func(x):
    return x + 2

def test_answer():
    assert func(3) == 5

def test_config():
    assert config.hostname == '127.0.0.1'
    assert config.username == 'dashdrive'
    assert config.password == 'dashdrive'
    assert config.database == 'sentinel'
    assert config.dash_cli == '/Users/nmarley/Dash/code/dash/src/dash-cli'
    assert config.datadir == '/Users/nmarley/Library/Application Support/DashCore'

