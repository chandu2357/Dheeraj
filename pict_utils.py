from typing import List

import pytest
from dash_common.constants.pict_constants import PICTHeaderLabels as PICT
from dash_core.utils.common.context import ConfigVars, Context


PICT_DIR = "configs/pict/mgs/"
TESTS_DIR = "tests/"
TEST_FILE_SUFFIX = "_test"
PICT_FILE_SUFFIX = ".txt"


def get_fixture_for_test_cases(metafunc):
    """
    Manage parsing PICT file, fetching PICT user and generating ids.
    Returns data as pytest fixture
    """
    pict_path: str = get_pict_path(metafunc)
    pict_data: List[dict] = parse_pict(pict_path)
    result_test_data: List[dict] = expand_with_config_details(pict_data)
    ids: list = generate_ids_strings(result_test_data)

    return pytest.fixture(params=result_test_data, ids=ids)


def generate_ids_strings(result_test_data) -> list:
    """ List of ids strings, each string represent set of (param=value),
    separated by "-"
    """
    return ['-'.join([f'({key}={value})' for key, value in p_.items()])
            for p_ in result_test_data]


def get_pict_path(metafunc) -> str:
    """
    Tries to find required path to PICT file.
    Path can be provided via cmd option -pict_path.
    By default, all tests are having corresponding PICT in configs/pict/mgs
    If path was provided via cmd option, it will have priority to default one
    """
    input_path = get_pict_file_path_from_options()
    default_path = get_default_pict_path_for_test(metafunc)
    pict_path = input_path if input_path else default_path
    return pict_path


def get_default_pict_path_for_test(metafunc) -> str:
    """
    By default configs/pict/mgs directory follows same structure as tests/
    PICT file name differs from test name by ending ".txt" instead "_test"
    E.g. for test file tests/portfolio/allbrokerage_test corresponding PICT
    will be configs/pict/mgs/portfolio/allbrokerage.txt
    Function is responsible for this calculation and returns path to PICT file
    """
    test_path = metafunc.module.__name__.replace(".", "/")
    _tests = TESTS_DIR
    _pict_dir = PICT_DIR
    pict_path = test_path.replace(_tests, _pict_dir).replace(TEST_FILE_SUFFIX,
                                                             PICT_FILE_SUFFIX)
    return pict_path


def get_pict_file_path_from_options() -> str:
    """
    Parse pytest's ConfigVars for --pict_path option
    If not success, returns empty str
    """
    try:
        input_pict_path = ConfigVars.config.getoption('--pict_path')
    except ValueError:
        input_pict_path = ""
    return input_pict_path


def read_pict_file(pict_path: str) -> list:
    """
    Read PICT file from pict_path and return parameters sets as list of lists
    Supports PICT data delimiters:  '|' , '\t', ' '
    """
    test_cases = []
    with open(pict_path, 'r') as pict_file:
        for line in pict_file.readlines():
            if "|" in line:
                params = line.strip().split('|')
            elif '\t' in line:
                params = line.strip().split('\t')
            else:
                params = line.strip().split(' ')

            test_cases.append(params)
    return test_cases


def parse_pict(pict_path) -> List[dict]:
    """
    Read PICT file, and return list of parameters mappings.
    Mapping uses  values from 1st row(headers) as keys,
    and it's corresponding value from row(test_cases)
    """
    pict_data = read_pict_file(pict_path)
    headers = pict_data[0]
    test_cases = pict_data[1:]
    keywords_list = []
    for case in test_cases:
        keywords = {header: value for header, value in zip(headers, case)}
        keywords_list.append(keywords)
    return keywords_list


def get_user_from_config(account_type="default") -> dict:
    """
    Context.config for fetching user details( from "mgs_users") by account_type
    PRD env user limited to just one, default for prd.json.
    Note: PRD user is not providing it's "user_id"
    Note: user_parameters keywords are converted to uppercase
    """
    if Context.env == 'prd':
        return {PICT.ACCOUNT_ID: Context.config["account"],
                PICT.USERNAME: Context.config["username"],
                PICT.PASSWORD: Context.config["password"]}
    else:
        mgs_users = Context.config["mgs_users"]
        user = mgs_users.get(account_type, mgs_users["default"])
        user_parameters = {key.upper(): value for (key, value) in user.items()}
        return user_parameters


def expand_with_config_details(pict_data_list) -> List[dict]:
    """
    Update parameters mapping in pict_data_list with user details from env.json
    return updated pict_data_list
    """
    for pict in pict_data_list:
        account_type = pict.get(PICT.ACCOUNT_TYPE, "default")
        user_details: dict = get_user_from_config(account_type)
        pict.update(user_details)
        pict[PICT.USERID] = pict["USER_ID"]
    return pict_data_list
