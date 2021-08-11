import pytest


FAST_MODE = True


def pytest_addoption(parser):
    parser.addoption("--runslow", action="store_true", default=False, help="run slow tests")


def pytest_collection_modifyitems(config, items):
    skip_slow = pytest.mark.skip(reason='slow tests are disabled')

    # The CLI option will override the global variable.
    should_skip_slow_tests = FAST_MODE and not config.getoption('--runslow')
    for item in items:
        if 'slow' in item.keywords and should_skip_slow_tests:
            item.add_marker(skip_slow)
