import json
import logging

import pytest
import requests
from dash_common.common_helpers.bapi_helpers.order_management_params import \
    market_hours_check
from dash_common.constants.base_constants import HeaderContentTypes
from dash_common.service_requests.mobile_gateway import accounts_services, \
    earnings_dividend_services
from dash_common.service_requests.mobile_gateway import home_widget_services
from dash_common.service_requests.mobile_gateway import mgs_backend_s2_services
from dash_common.service_requests.mobile_gateway import portfolio_services
from dash_common.service_requests.mobile_gateway.portfolionews_services \
    import \
    PortfolioNewsService
from dash_core.conftest import Context

from test_helpers import utils
from test_helpers.mgs_service_helpers.client.api_client import BaseAPIClient
from test_helpers.mgs_service_helpers.client.constants import Req
from test_helpers.mgs_validation_helpers.references.mgs_objects import \
    MobileResponse
from test_helpers.mgs_validation_helpers.uuid_mixin import UuidMixin
from test_helpers.utils import build_url

MAX_TO_FETCH = 1


class MGSRedesignService(UuidMixin):
    prepared_request = None
    received_response = None
    client = BaseAPIClient()

    @property
    def _uid(self):
        return self.client.user.user_id

    def mobile_authenticate(self, *args, **kwargs):
        return self.client.mobile_authenticate(*args, **kwargs)

    def parse_response(self, mgs_res: dict = None):
        """
        Parse response(mgs_res or self.received_response) to python object.
        'references' and 'views' can be accessed by object's attributes
        Data lists of same type('accounts'/'account_summary',..)assigned to
        related references/views attributes
        self.parse_response(mgs_res=self.received_response).references
        .accounts(): return SearchList([{accountId:123},
        fetch needed objects from list with keyword=value
        self.parse_response().references.accounts(accountId=321): return
        SearchList([{accountId:321}])
        """
        mgs_res = mgs_res or self.received_response
        return MobileResponse(mgs_res)

    def get_et_auth_details(self):
        """
        Returns encrypted str for node level authorization, Uses current
        username and user_id values
        :return: str
        """
        details = {"customer": {
            "userId": self.client.user.user_id,
            "userName": self.client.user.username},
            "anon": False}
        details_as_json_str = json.dumps(details)
        details_encrypted = self.as_base64_string(details_as_json_str)
        return details_encrypted

    def get_node_headers(self):
        return {
            'Content-Type': 'application/json',
            'x-et-auth-details': self.get_et_auth_details()}

    def mobile_node_post(self, service, request):
        """
        Send request directly to node
        :param service: BaseService
        :param request: DataExchangeEntity
        :return: str
        """
        node = Context.config['mobile_gateway']['node']
        path = node + service.get_service_name() + request.get_name()
        request_body = request.as_json()
        headers = self.get_node_headers()
        response = requests.post(url=path, data=request_body, headers=headers,
                                 verify=False)
        response_text = response.text

        return response_text

    def mgs_post(self, service, request,
                 cache_response=True,
                 error_expected=False,
                 code_expected=200, **params) -> requests.Response:
        """Post to MGS services on regular purpose.

        :param service: BaseService
        :param request: DataExchangeEntity
        :param cache_response: if True, save prepared request
            and received response to self.prepared_request/received_response
        :param error_expected: False, if expecting 200 response
        :param code_expected: 200 by default
        :return: requests.Response
        """
        self.prepare_request_parameters(service, request, params)
        response = self.client.post(data=request.as_json(), **params)
        service_metadata_update(service, request, response, params)
        self.response_basic_validation(response, error_expected, code_expected)
        self.response_caching(request, response, cache_response)
        return response

    def mgs_get(self, path):
        """GET to MGS services on regular purpose

        :param path:BaseService
        :return:  dict, response.json()
        """
        host = Context.config['mobile_url'] + "/"
        url = host + path
        response: requests.Response = self.client.get(url=url)
        return response

    def prepare_request_parameters(self, service, request, params):
        """Parse, check and prepare necessary request parameters.
        Basic needed request parameters  are:
         1."url" - build via  build_url with help of service, request objects
         2."headers" -  if this keyword is specified,
                        will use value(must be a dict) untouched as headers
                        if no - will try to get value from build_headers method
        """
        logging.info(f"{':'*10}{request.get_name()} starts {':'*10}")

        platform: str = params.pop('platform', 'etm')
        node: str = params.pop('node', False)
        api_v = params.pop('api_v', 1)

        if Req.URL not in params:
            params[Req.URL] = build_url(service, request,
                                        platform, node, api_v)
        if Req.HEADERS not in params:
            params[Req.HEADERS] = self.build_headers(platform, node, params)
        logging.info(f"mgs_post:Prepared request: {request.get_name()}")
        logging.info(f"mgs_post:Prepared request body: {request.as_json()}")
        logging.info(f"mgs_post:Request parameters: {params}")

    @staticmethod
    def response_basic_validation(response, error_expected, exp_code):
        debug_text = response.text
        if not error_expected and not response.ok:
            pytest.fail(f"Got unexpected response status code from server:"
                        f"Actual code: {response.status_code}, "
                        f"But error_expected is set to {error_expected}\n"
                        f"URL:{response.url}\n"
                        f"Request body:{response.request.body}\n"
                        f"Response text:\n{debug_text}")
        if response.status_code != exp_code:
            pytest.fail(f"Got unexpected response status code from server:"
                        f"Actual code: {response.status_code}, "
                        f"Expected code: {exp_code}\n\n"
                        f"Response text:\n{debug_text}")

    def response_caching(self, request, response, cache_response_flag):
        if cache_response_flag is True:
            try:
                json_to_cache = response.json()
                self.prepared_request = request
                logging.info(f"Received response: {json_to_cache.keys()}")
                self.received_response = json_to_cache
            except Exception as error:
                invalid_json = response.text
                pytest.fail(f"Failed to parse response json with {error}:\n"
                            f"Request: {request} \n"
                            f"Response[{response.status_code}]:{invalid_json}")
            finally:
                logging.info(f"{':'*10}{request.get_name()} ends {':'*10}")

    def build_headers(self, platform, node, params):
        # Most common/default headers: content type and origin
        # 'Origin' should be platform-specific
        headers = {
            Req.ORIGIN_HEADER_KEY: utils.map_platform_on_host()[platform],
            Req.CONTENT_TYPE_HEADER_KEY: Req.CONTENT_TYPE_JSON}
        # Check if user specified headers by passing keyword argument
        # Known cases (as for now): 'Origin', 'user_agent'
        possible_headers = [Req.ORIGIN_HEADER_KEY, Req.USER_AGENT_HEADER_KEY]
        params_headers = {key: params.pop(key) for key in possible_headers
                          if key in params}
        headers.update(params_headers)

        # Stk-token adding, if user is logged-in
        if self.client.user and self.client.user.token:
            headers.update({Req.STK1_HEADER_KEY: self.client.user.token})

        # Node-specific headers, setting params["verify"] for requests
        if node:
            headers.update(self.get_node_headers())
            params["verify"] = False
        return headers

    # Portfolio services:
    def all_brokerage_request(self, api_v=1, is_enable_new_experiance=False,
                              **kwargs):
        """Get all brokerage response"""
        request = portfolio_services.AllBrokerageService().request
        request.enableNewExperience = is_enable_new_experiance
        response: requests.Response = self.mgs_post(
            portfolio_services.AllBrokerageService(),
            request, api_v=api_v,
            **kwargs)

        return self.prepared_request, response

    def individual_brokerage_request(self, account_uuid, api_v=1, is_enable_new_experience=False, **kwargs):
        """Get individual brokerage response."""
        service = portfolio_services.IndividualBrokerageService()
        request = service.request
        request.enableNewExperience = is_enable_new_experience
        request.accountUuid = account_uuid
        response = self.mgs_post(service, request, api_v=api_v, **kwargs)

        return request, response

    def individual_brokerage_order_count_request(self, account_uuid, **kwargs):
        """Get individual brokerage order count"""
        service = portfolio_services.IndividualBrokerageService()
        request = service.request

        request.accountUuid = account_uuid
        request.orderCount = True

        response_txt = self.mgs_post(service, request, **kwargs)
        response = service.individualbrokerage_response.parse(
            response_txt.text, True)
        return request, response

    def tax_lots_request(self, account_uuid, position_id, api_v=1, **kwargs):
        """Get lots response"""
        service = portfolio_services.LotsService()
        request = service.request

        request.accountUuid = account_uuid
        request.positionId = position_id

        response = self.mgs_post(service, request, api_v=api_v, **kwargs)

        return request, response

    def get_account_and_position_pairs(self, max_=MAX_TO_FETCH):
        request_all, response_all = self.all_brokerage_request()
        positions = self.parse_response(
            response_all.json()).references.positions
        account_uuids = [(position['accountUuid'], position['positionId']) for
                         position in positions]
        if max_:
            account_uuids = account_uuids[:max_]
        return account_uuids

    # Account services:
    def account_list_request(self, api_v=1, **kwargs):
        """Get account list API response"""
        service = accounts_services.AccountListService()
        request = service.request
        response = self.mgs_post(service, request, api_v=api_v, **kwargs)

        return request, response

    def accountlist_displaynotification_request(self, api_v=1, **kwargs):
        service = accounts_services.AccountListDisplayNotificationService()
        request = service.request
        response = self.mgs_post(service, request, api_v=api_v, **kwargs)

        return request, response

    def account_overview_request(self, acc_uuid: str, api_v=1, **kwargs):
        """Get account overview response."""
        service = accounts_services.AccountOverviewService()
        request = service.request

        request.accountUuid = acc_uuid
        if not market_hours_check(market_session="extended"):
            request.extendedHours = True

        response = self.mgs_post(service, request, api_v=api_v, **kwargs)

        return request, response

    def complete_view_request(self, api_v=1, **kwargs):
        """Get complete_view API response."""
        service = accounts_services.CompleteViewService()
        request = service.request

        response = self.mgs_post(service, request, api_v=api_v, **kwargs)

        return request, response

    def complete_view_request_display_posistions_true(self, api_v=1, **kwargs):
        """Get complete_view API response."""
        service = accounts_services.CompleteViewServiceDisplayPositions()
        request = service.request
        response = self.mgs_post(service, request, api_v=api_v, **kwargs)

        return request, response

    def get_users_brokerage_accounts(self, max_=MAX_TO_FETCH):
        self.account_list_request()
        uuids = []
        accounts = self.parse_response().references.accounts(
            instType="ADP",
            acctType="Brokerage")
        for account in accounts:
            uuids.append(account['accountUuid'])
        if max_:
            uuids = uuids[:max_]
        return uuids

        # Home Widget services:

    def unauthenticated_users_widget_request(self, symbol=None, api_v=1, **kwargs):
        """ Get unauthenticated widgets API response"""
        service = home_widget_services.UnauthenticatedUserService()
        unauthenticated_users_request = service.request
        unauthenticated_users_request.symbol = symbol
        response_txt = self.mgs_post(service, unauthenticated_users_request,
                                     api_v=api_v, **kwargs).text
        response = service.unauthenticateduser_response.parse(response_txt, True)
        return unauthenticated_users_request, response

    def get_unauthenticated_users_home_widgets(self, symbol=None):
        """
         Makes call to Unauthenticated user's home widget services
        :param symbol:
        :return: dict
        """
        logging.info("Making call to unauthenicated user home widget")
        _, unauthenticated_users_response = self.unauthenticated_users_widget_request(symbol)
        return _, unauthenticated_users_response

    def get_tranferfunding_activity_request(self, user_id, env):
        transfer_activity_endpoint = "https://mm-restapi.%s.etrade.com/movemoney/fundingcard-transfer-activity" % env
        body = {"transactionFilter": "ALL", "transferTypeFilter": "ACH,RETIREMENT,INTERNAL", "userId": user_id}
        headers = {"Content-Type": "application/json", }
        response = requests.request("POST", transfer_activity_endpoint, headers=headers, data=json.dumps(body),
                                    verify=False)

        return response.json()

    def get_saved_orders_request(self, account_id, user_id):
        service = mgs_backend_s2_services.SavedOrderServices()
        s2_endpoint_url = service.get_service_name()
        request = service.request

        request.PreparedRequest.AccountId = account_id
        request.PreparedRequest.UserId = user_id
        headers = {"Content-Type": HeaderContentTypes.CONTENT_TYPE_TEXT_XML}

        response = requests.request("POST", s2_endpoint_url, headers=headers, data=request.as_xml(),
                                    verify=False)

        return response

    def get_open_orders_request(self, account_id, user_id):
        service = mgs_backend_s2_services.OpenOrdersServices()
        s2_endpoint_url = service.get_service_name()
        request = service.request
        request.Request.UserId = user_id
        request.Request.Accounts = account_id
        headers = {"Content-Type": HeaderContentTypes.CONTENT_TYPE_TEXT_XML}

        response = requests.request("POST", s2_endpoint_url, headers=headers, data=request.as_xml(),
                                    verify=False)

        return response

    def accountlist_dual_account_visibility(self, api_v=1, **kwargs):
        """Dual Account Visibility"""
        service = accounts_services.AccountListDualAccountVisibility()
        request = service.request
        self.mgs_post(service, request, api_v=api_v, **kwargs)

    def accountlist_nondual_account_visibility(self, api_v=1, **kwargs):
        """Non Dual Account Visibility"""
        service = accounts_services.AccountListNonDualAccountVisibility()
        request = service.request
        response = self.mgs_post(service, request, api_v=api_v, **kwargs)
        return request, response

    def mscompleteview_request(self, api_v=2, **kwargs):
        """MsCompleteview Request"""
        service = accounts_services.MsCompleteView()
        request = service.request
        self.mgs_post(service, request, api_v=api_v, **kwargs)

    # News Portfolios
    def portfolio_news_request(self, acc_uuid, api_v=1, **kwargs):
        """ Get portfolio news API response"""
        stockplan: str = kwargs.pop('stockplan', False)
        isnewsrequestforallaccounts: str = kwargs.pop('isnewsrequestforallaccounts', False)
        viewbysymbol: str = kwargs.pop('viewbysymbol', False)

        service = PortfolioNewsService()
        portfolio_news_request = service.request
        portfolio_news_request.accountUuid = acc_uuid
        portfolio_news_request.stockplan = stockplan
        portfolio_news_request.viewBySymbol = viewbysymbol
        portfolio_news_request.isNewsRequestForAllAccounts = isnewsrequestforallaccounts
        response_txt = self.mgs_post(service=service, request=portfolio_news_request,
                                     error_expected=True, api_v=api_v, **kwargs).text
        response = service.portfolionews_response.parse(response_txt, True)
        return portfolio_news_request, response

    def earnings_request(self, api_v=2, pict_case_args=None, **kwargs):
        """Get complete_view API response."""
        service = earnings_dividend_services.EarningsService()
        request = service.request
        request.symbol = pict_case_args["symbol"]
        request.fiscalPeriod = pict_case_args["fiscalPeriod"]
        request.fiscalPeriodCount = int(pict_case_args["fiscalPeriodCount"])

        response = self.mgs_post(service, request, api_v=api_v, **kwargs)
        return request, response


def service_metadata_update(service, request, response, params):
    api_v, service_name, endpoint = params['url'].split('/')[-3:]
    service_id = f'{api_v}-{service_name}/{endpoint}'
    text = response.text
    cache_service_metadata: dict = Context.cache['services'].get(service_id)
    if not cache_service_metadata:
        logging.info(f"service_metadata_update:Not found yet {service_id}")
        Context.cache['services'][service_id] = {}
        collect_responses = [text]
        collect_requests = [request.as_json()]
        new_service_metadata = dict(
            service=service_name,
            request=collect_requests,
            response=collect_responses,
            outcome=response.ok,
            hits=1,
            endpoint=endpoint)
    else:
        logging.info(f"service_metadata_update: Found record for {service_id}")
        new_service_metadata = cache_service_metadata.copy()
        new_service_metadata['hits'] = cache_service_metadata['hits'] + 1
        new_service_metadata['response'].append(text)
        new_service_metadata['request'].append(request.as_json())
    Context.cache['services'][service_id].update(new_service_metadata)
    logging.info(f"service_metadata_update: \n {service_id}")
