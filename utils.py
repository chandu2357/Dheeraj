import logging
import re
from collections import UserList

import requests
from dash_common.constants.mgs_mobile_gateway_constants import ReferenceIds
from dash_core.conftest import ConfigVars
from dash_core.utils.common.context import Context


def get_ids_message(reference: dict) -> str:
    """
    Parse references obj for ids
    Format and return ids string
    ReferenceIds is list of ids keys from mgs_constants
    :param reference: dict
    :return: str
    """
    msg = ''
    no_msg = 'No ids found in object!'
    for ids in ReferenceIds.to_list():
        value = reference.get(ids)
        if value:
            msg += f'{ids}:{value}\n'

    return msg or no_msg


def _list(value):
    """
    Parsing xml single element is returning as "element_name":{object}
    And not single as "element_name":[{object},{object}]
    To unify approach in single element  case, method is ensuring to return
    list of elements
    :param value: list or dict
    :return: list
    """
    return value if isinstance(value, list) else [value]


class SearchList(UserList):
    """
    Call this SearchList with **kwargs to get filtered list by this arguments
    If elements are dicts, the **kwargs will be used as key=value
    Else: **kwargs will be used as attribute_name=attribute_value
    Convert underlying elements by self.convert(func)
    """

    def __call__(self, **kwargs):
        if kwargs:
            filtered: list = self.search_by(**kwargs)
            return SearchList(filtered)
        else:
            return self

    def convert(self, method):
        _l = self.data[:]
        self.data = [method(obj) for obj in _l]

    @property
    def entries_are_dicts(self):
        return all([isinstance(entry, dict) for entry in self.data])

    def search_by(self, **kwargs) -> list:
        list_to_search = self.data[:]
        result = []
        if self.entries_are_dicts:  # list of dicts
            for key, value in kwargs.items():
                result = filter(lambda x: x.get(key) == value, list_to_search)
        else:
            for attr, value in kwargs.items():
                result = filter(lambda x: getattr(x, attr) == value,
                                list_to_search)
        return list(result)


def map_instrument_on_position(instruments, positions):
    instruments = SearchList(instruments)
    positions = SearchList(positions)
    _map = []
    for instrument in instruments:
        position = positions(positionId=instrument.positionId).pop()
        _map.append((instrument, position))
    return _map


def _dict_by_id(objects: list, id_key: str) -> dict:
    """
    Will parse this structure:
    [{'id':"123", 'balances':{..},..}, {'id':"321", 'balances':{..},..},..]
    And return this:
    {"123":{'id':"123", 'balances':{..},..}, "321":{'id':"321", 'balances':{
    ..},..},..}
    Id value can be wrapped inside some input dict like:
    {'Key':{id_key: "123"..},..} or {'Acct':{id_key: "123"..},..}
    will also try get id via keys 'Key', 'Acct'
    :param objects: list, [_object={'id_key':object_id},…]
    :param id_key: str, id key
    :return: dict {'object_id':object,…}
    """
    id_dict = {}
    try:
        id_dict = {str(_object[id_key]): _object for _object in objects}
        return id_dict
    except KeyError:
        pass

    for id_object in ['Key', 'Acct', 'Lot']:
        try:
            id_dict = {str(_object[id_object][id_key]): _object for _object in
                       objects}
            return id_dict
        except KeyError:
            continue
    return id_dict


def build_url(service, request, platform, node, api_v):
    """Build and return url from service:BaseService,
    request:DataExchangeEntity and other kwargs provided"""
    platform_host: str = map_platform_on_host()[platform]
    #  No agreement in config's urls about trailing slash
    phx = "phx" if platform_host.endswith("/") else "/phx"
    phx_host: str = platform_host + phx
    hosting: str = node or phx_host
    service_part: str = get_service_path(service, platform, api_v)
    request_part: str = request.get_name()
    url: str = hosting + service_part + request_part

    return url


def map_platform_on_host() -> dict:
    platform_to_host = {"pet": Context.config['base_url'],
                        "etm": Context.config['mobile_url']}
    return platform_to_host


def get_service_path(service, platform, api_v):
    try:
        return service.get_service_name(api_v=api_v, platform=platform)
    except TypeError:
        logging.info(f"Service object for {service.get_service_name()} "
                     f"is not supporting additional parameters yet!")
        return service.get_service_name()


def update_mvp_result():
    results = ConfigVars.test_result["result"]
    test_names = []
    for _, _, testname in ConfigVars.test_result["location"]:
        test_names.append(testname)
    durations = ConfigVars.test_result["duration"]
    errors = ConfigVars.test_result["error"]
    heading = "MBL_TEST_Details"
    for test_name, duration, test_status, error in zip(test_names, durations, results, errors):
        if test_status == "passed":
            test_stat = "0"
        else:
            test_stat = "1"
        test_name = re.sub(r'[^a-zA-Z0-9]', '', test_name.split(".")[0])
        if test_name.startswith("Test"):
            test_name = test_name.lstrip("Test")
        payload = f"http://uatdashboard.etrade.com/cgi-bin/wpmStatus.cgi?action=post&heading=" \
            f"{heading}&test={test_name}&status={test_stat}&perf={duration}&msg={error}"
        requests.get(payload, timeout=2.001)
