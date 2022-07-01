import os
import sys

import pytest

from test_helpers import pict_utils
from test_helpers.mgs_backend_service_helpers.s2_client import S2Client
from test_helpers.mgs_validation_helpers.references import values_formats
from test_helpers.mgs_validation_helpers.references.values_formats import \
    AccountType
from test_helpers.pict_utils import get_user_from_config
from test_helpers.tag_coverage import MgsContext, tag_coverage_report

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.append(PROJECT_ROOT)
pytest_plugins = ["dash_core.utils.common.pytest_fixtures", ]


@pytest.fixture
def config_user(account_type):
    user_details = get_user_from_config(account_type.lower())
    username = user_details["USERNAME"]
    password = user_details["PASSWORD"]

    return username, password


@pytest.fixture
def s2_client(prepared_client):
    """
    Returns s2_client ready
    """
    s2_client = S2Client(prepared_client.client.user)
    return s2_client


@pytest.fixture
def account_type(request) -> str:
    """Default is Brokerage, if parametrized - request.param"""
    account_type = getattr(request, 'param',
                           values_formats.AccountType.Brokerage)
    return account_type


@pytest.fixture
def instrument_type(request) -> str:
    """Default is EQ, if parametrized - request.param"""
    instrument_type = getattr(request, 'param',
                              values_formats.InstrumentType.Stocks)
    return instrument_type


# ---------------------------------standard session
# fixtures----------------------------------------


def pytest_generate_tests(metafunc):
    if 'pict_case_args' in metafunc.fixturenames:
        pict_fixture = pict_utils.get_fixture_for_test_cases(metafunc)
        metafunc.parametrize('pict_case_args', list(pict_fixture.params))

    if 'mvp_case_args' in metafunc.fixturenames:
        pict_fixture = pict_utils.get_fixture_for_test_cases(metafunc)
        metafunc.parametrize('mvp_case_args', list(pict_fixture.params))


def pytest_terminal_summary(terminalreporter, exitstatus, config):
    if "tests/references" in config.args[0]:
        tag_coverage_report(terminalreporter)


def pytest_itemcollected(item):
    is_ref_test = "tests/references" in item.nodeid
    is_ref_paramertrized = item.get_closest_marker("reference_type")
    if is_ref_test and is_ref_paramertrized:
        reference_type = item.get_closest_marker("reference_type").args[0]
        request_type = item.callspec.params['request_type']
        tag_name = item.originalname.replace("test_", "")
        MgsContext.references_tag.update_covered(request_type,
                                                 reference_type,
                                                 tag_name)
