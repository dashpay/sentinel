import config

def func(x):
    return x + 2

def test_answer():
    assert func(3) == 5

def test_config():
    test_db_cfg = config.db['production']
    assert test_db_cfg['host'] == '127.0.0.1'
    assert test_db_cfg['user'] == 'dashdrive'
    assert test_db_cfg['passwd'] == 'dashdrive'
    assert test_db_cfg['database'] == 'sentinel'

    # assert config.dash_cli == '/Users/nmarley/Dash/code/dash/src/dash-cli'
    # assert config.datadir == '/Users/nmarley/Library/Application Support/DashCore'
