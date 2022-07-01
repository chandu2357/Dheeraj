from dash_common.service_requests.base_service import BaseService
from dash_common.service_requests.data_exchange_entity import DataExchangeEntity
from dash_common.service_requests.mobile_gateway.vo.accounts_vo import AccountOverviewVO


class AccountsService(BaseService):
    def get_service_name(self, api_v=1, platform='etm'):
        if api_v == 2:
            return f"/user/{platform}/services/v2/account/"
        if api_v == 1:
            return f'/{platform}/services/v1/account/'


class CompleteViewService(AccountsService):
    def get_service_name(self, api_v=1, platform='etm'):
        if api_v == 2:
            return f"/user/{platform}/services/v2/user/"
        if api_v == 1:
            return f'/{platform}/services/v1/account/'

    # noinspection PyPep8Naming
    class completeView(DataExchangeEntity):
        _root_value_ = ""

    request = completeView()

    class CompleteViewResponse(DataExchangeEntity):
        pass

    completeview_response = CompleteViewResponse()


class CompleteViewServiceDisplayPositions(AccountsService):
    def get_service_name(self, api_v=1, platform='etm'):
        if api_v == 2:
            return f"/user/{platform}/services/v2/user/"
        if api_v == 1:
            return f'/{platform}/services/v1/account/'

    # noinspection PyPep8Naming
    class completeView(DataExchangeEntity):
        _root_value_ = {"displayPositions": True, "displayPositionsForMultiAccount": True}

    request = completeView()

    class CompleteViewResponse(DataExchangeEntity):
        pass

    completeview_response = CompleteViewResponse()


class AccountListService(AccountsService):
    # noinspection PyPep8Naming
    class accountList(DataExchangeEntity):
        _root_value_ = ""

    request = accountList()

    class AccountListResponse(DataExchangeEntity):
        pass

    accountlist_response = AccountListResponse()


class AccountOverviewService(AccountsService):
    # noinspection PyPep8Naming
    class accountOverview(AccountOverviewVO, DataExchangeEntity):
        pass

    request = accountOverview()

    class AccountOverviewResponse(DataExchangeEntity):
        pass

    accountoverview_response = AccountOverviewResponse()


class AccountListDisplayNotificationService(AccountsService):
    # noinspection PyPep8Naming
    class accountList(DataExchangeEntity):
        _root_value_ = {"displayPersonalNotifications": True}

    request = accountList()

    class AccountListResponse(DataExchangeEntity):
        pass

    accountlist_response = AccountListResponse()


class AccountListDualAccountVisibility(AccountsService):
    # noinspection PyPep8Naming
    class accountList(DataExchangeEntity):
        _root_value_ = {"enableDualAccountVisibility": True}

    request = accountList()

    class AccountListResponse(DataExchangeEntity):
        pass

    accountlist_response = AccountListResponse()


class AccountListNonDualAccountVisibility(AccountsService):
    # noinspection PyPep8Naming
    class accountList(DataExchangeEntity):
        _root_value_ = {"enableDualAccountVisibility": False}

    request = accountList()

    class AccountListResponse(DataExchangeEntity):
        pass

    accountlist_response = AccountListResponse()


class MsCompleteView(AccountsService):
    def get_service_name(self, api_v=1, platform='etm'):
        if api_v == 2:
            return f"/user/{platform}/services/v2/user/"
        if api_v == 1:
            return f'/{platform}/services/v1/account/'

    class msCompleteView(DataExchangeEntity):
        _root_value_ = None

    request = msCompleteView()

    class msCompleteViewResponse(DataExchangeEntity):
        pass

    mscompleteview_response = msCompleteViewResponse()
