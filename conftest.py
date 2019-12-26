import os


def pytest_addoption(parser):
    parser.addoption(
        '--base-url',
        required=True,
    )
    parser.addoption(
        '--local-dir',
        default=os.path.join(os.path.dirname(__file__), 'testcase')
    )


def pytest_configure(config):
    global BASE_URL, LOCAL_DIR
    BASE_URL = config.getoption('--base-url')
    LOCAL_DIR = config.getoption('--local-dir')
