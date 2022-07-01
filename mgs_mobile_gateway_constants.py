"""Tag Names and corresponding default values/regex for APIs"""
from dash_core.core.common.test_client_helpers.base_constant_methods import BaseConstantMethods


class ReferenceIds(BaseConstantMethods):
    ACCOUNTID = 'accountId'
    ACCOUNTUUID = 'accountUuid'
    POSITIONID = 'positionId'
    INSTRUMENTID = 'instrumentId'
    POSITIONLOTID = 'positionLotId'
    WATCHLISTID = "watchListId"
    ENTRYID = "entryId"
    SYMBOL = 'symbol'
    lastTradeTime = 'lastTradeTime'


class ReferencesObjectTypes(BaseConstantMethods):
    ACCOUNTS = 'accounts'
    POSITIONS = 'positions'
    INSTRUMENTS = 'instruments'
    TAXLOTS = 'taxlots'
    WATCHLIST_EDITENTRY = "watchList_editEntry"
    WATCHLIST_CREATE = "watchList_Create"
    EARNINGS_HISTORY_INFO = "earnings_history_info"
    EARNINGS_FORECAST_INFO = "earnings_forecast_info"

    COMPLETEVIEW = [ACCOUNTS]
    ACCOUNTLIST = [ACCOUNTS]
    ACCOUNTOVERVIEW = [ACCOUNTS]
    ALLBROKERAGE = [ACCOUNTS, POSITIONS, INSTRUMENTS]
    INDIVIDUAL = [ACCOUNTS, POSITIONS, INSTRUMENTS]
    TAX_LOTS = [POSITIONS, INSTRUMENTS, TAXLOTS]
    EARNINGS = [EARNINGS_HISTORY_INFO, EARNINGS_FORECAST_INFO]


class ViewsObjectTypes(BaseConstantMethods):
    NET_ASSETS_SUMMARY = 'net_assets_summary'
    NET_GAIN_SUMMARY = 'net_gain_summary'
    ACCOUNT_SUMMARY = 'account_summary'
    ACCOUNT_LIST = 'account_list'
    POSITIONS_LOTS_LIST = 'positions_lots_list'
    ACCOUNT_PORTFOLIO_LIST = 'account_portfolio_list'
    POSITION_LIST = 'positions_list'
    WATCHLIST_EDITENTRY = 'watchList_editEntry'
    WATCHLIST_CREATE = "watchList_Create"
    WATCHLIST_INDIVIDUAL = "watchList_Individual"
    EARNINGS_INFO = "earnings_info"

    COMPLETEVIEW = [NET_ASSETS_SUMMARY, NET_GAIN_SUMMARY, ACCOUNT_SUMMARY]
    ACCOUNTLIST = [ACCOUNT_LIST]
    ACCOUNTOVERVIEW = [ACCOUNT_SUMMARY]
    ALLBROKERAGE = [ACCOUNT_SUMMARY, ACCOUNT_PORTFOLIO_LIST]
    INDIVIDUAL = [ACCOUNT_SUMMARY, POSITION_LIST]
    TAXLOTS = [POSITIONS_LOTS_LIST]
    EARNINGS = [EARNINGS_INFO]


class ViewsObjectStreamableValue(BaseConstantMethods):
    NET_ASSETS_SUMMARY = 'NET_ASSETS'
    NET_GAIN_SUMMARY = 'DAYS_GAIN'

    COMPLETEVIEW = [NET_ASSETS_SUMMARY, NET_GAIN_SUMMARY]


class ViewsObjectDataLabel(BaseConstantMethods):
    NET_ASSETS_SUMMARY = 'Net Assets'
    NET_GAIN_SUMMARY = 'Days Gain'

    COMPLETEVIEW = [NET_ASSETS_SUMMARY, NET_GAIN_SUMMARY]


class ResponseEntryAction(BaseConstantMethods):
    ADD = "ADD"
    DELETE = "DELETE"
    MOVE = "MOVE"


class UuidConstants(BaseConstantMethods):
    SPLITTER = '|'
    ACCOUNTID = 'accountId'
    ACCTTYPE = 'acctType'
    INSTTYPE = 'instType'
    INSTNUMBER = 'instNumber'
    SYMBOLVAL = '-'
    CODING = "utf-8"
    MANAGEDACCOUNTTYPE = 'managedAccountType'


class ValuesValidationConstants(BaseConstantMethods):
    TOLERANCE = 0.05
    VALUES_FORMATS_CHARS = ['$', ',', '%']
    MULTIPLIER_MAP = {'K': 1e+3, 'M': 1e+6, 'B': 1e+9}


class FrequentlyUsedTags(BaseConstantMethods):
    TYPE = 'type'
    DATA = 'data'
    CTA = 'cta'
    ACTION = 'action'
    VIEWS = 'views'
    REFERENCES = 'references'
    MOBILE_RESPONSE = 'mobile_response'
    ACCOUNT_UUID = 'account_uuid'


class BaseTagsMethods(BaseConstantMethods):
    @classmethod
    def to_set(cls):
        cls_dict = cls.to_dict()
        tag_set = set(cls_dict.values())
        return tag_set


class BaseTags(BaseTagsMethods):
    mobile_response = 'mobile_response'
    type = 'type'
    data = 'data'
    views = 'views'
    references = 'references'
    meta = 'meta'
    cta = 'cta'
    action = 'action'
    account_uuid = 'accountUuid'
    position_id = 'positionId'
    accounts = 'accounts'
    instruments = 'instruments'
    positions = 'positions'
    tax_lots = 'taxlots'


class ReferenceInstrumentsTags(BaseTags):
    instrumentId = "instrumentId"
    symbol = "symbol"
    displaySymbol = "displaySymbol"
    typeCode = "typeCode"
    exchangeCode = "exchangeCode"
    bid = "bid"
    ask = "ask"
    marketValue = "marketValue"
    volume = "volume"
    marketCap = "marketCap"
    pe = "pe"
    eps = "eps"
    lastPrice = "lastPrice"
    week52High = "week52High"
    week52Low = "week52Low"
    impliedVolatilityPct = "impliedVolatilityPct"
    openInterest = "openInterest"
    delta = "delta"
    premium = "premium"
    gamma = "gamma"
    vega = "vega"
    theta = "theta"
    expirationDate = "expirationDate"
    underlyingTypeCode = "underlyingTypeCode"
    underlyingExchangeCode = "underlyingExchangeCode"
    underlyingSymbol = "underlyingSymbol"
    daysExpiration = "daysExpiration"
    markToMarket = "markToMarket"
    lastTradeTime = "lastTradeTime"
    previousClose = "previousClose"
    isPriceAdjusted = "isPriceAdjusted"
    adjLastTrade = "adjLastTrade"
    adjPreviousClose = "adjPreviousClose"
    dayChangeValue = "dayChangeValue"
    dayChangePerc = "dayChangePerc"
    extHrChangeValue = "extHrChangeValue"
    extHrChangePerc = "extHrChangePerc"
    extHrLastPrice = "extHrLastPrice"


class ReferencePositionsTags(BaseTags):
    symbol = "symbol"
    commission = "commission"
    todayCommissions = "todayCommissions"
    fees = "fees"
    quantity = "quantity"
    todayQuantity = "todayQuantity"
    displayQuantity = "displayQuantity"
    basisPrice = "basisPrice"
    baseSymbolPrice = "baseSymbolPrice"
    pricePaid = "pricePaid"
    todayPricePaid = "todayPricePaid"
    daysGainValue = "daysGainValue"
    totalGainValue = "totalGainValue"
    daysGainPercentage = "daysGainPercentage"
    totalGainPercentage = "totalGainPercentage"
    daysPurchase = "daysPurchase"
    todaysClose = "todaysClose"
    hasLots = "hasLots"
    inTheMoneyFlag = "inTheMoneyFlag"
    optionUnderlier = "optionUnderlier"
    strikePrice = "strikePrice"
    markToMarket = "markToMarket"
    lastTradeTime = "lastTradeTime"
    previousClose = "previousClose"
    volume = "volume"
    isPriceAdjusted = "isPriceAdjusted"
    adjLastTrade = "adjLastTrade"
    adjPreviousClose = "adjPreviousClose"
    dayChangeValue = "dayChangeValue"
    dayChangePerc = "dayChangePerc"
    extHrChangeValue = "extHrChangeValue"
    extHrChangePerc = "extHrChangePerc"
    extHrLastPrice = "extHrLastPrice"
    marketValue = "marketValue"
    displaySymbol = 'displaySymbol'


class BondPositionTags(BaseTags):
    bondRate = 'bondRate'
    bondFactor = 'bondFactor'
    maturity = 'maturity'


class AccountPositionTags(BaseTags):
    accountUuid = "accountUuid"
    accountId = "accountId"
    positionId = "positionId"


class AccountsTags(BaseTags):
    account_uuid = "accountUuid"
    account_id = "accountId"
    account_mode = "accountMode"
    account_desc = "acctDesc"
    account_short_name = "accountShortName"
    account_long_name = "accountLongName"
    account_type = "acctType"
    inst_type = "instType"

    cash_available_for_withdrawal = "cashAvailableForWithdrawal"
    margin_available_for_withdrawal = "marginAvailableForWithdrawal"
    purchasing_power = "purchasingPower"
    total_available_for_withdrawal = "totalAvailableForWithdrawal"
    ledger_account_value = "ledgerAccountValue"
    account_value = "accountValue"

    days_gain = "daysGain"
    days_gain_percent = "daysGainPercent"
    total_gain = "totalGain"
    total_gain_percent = "totalGainPercent"

    account_index = "accountIndex"
    symbol = "symbol"
    stock_spec = {account_index, symbol}

    option_level = 'optionLevel'
    restriction_level = 'restrictionLevel'
    prompts_for_funding = 'promptsForFunding'
    enc_account_id = "encAccountId"

    flag_washsaleflag = "washSaleFlag"
    flag_is_ira = "isIRA"
    flag_mdvflag = "mdvFlag"
    flag_funded = "funded"
    flag_streaming = "streamingRestrictions"
    flag_ma_flag = "maFlag"
    flag_domestic = "geoDomestic"


class TaxLotsTags(BaseTags):
    price = "price"
    termCode = "termCode"
    daysGain = "daysGain"
    daysGainPct = "daysGainPct"
    marketValue = "marketValue"
    totalCost = "totalCost"
    totalCostForGainPct = "totalCostForGainPct"
    totalGain = "totalGain"
    totalGainPct = "totalGainPct"
    lotSourceCode = "lotSourceCode"
    originalQty = "originalQty"
    remainingQty = "remainingQty"
    availableQty = "availableQty"
    orderNo = "orderNo"
    legNo = "legNo"
    acquiredDate = "acquiredDate"
    locationCode = "locationCode"
    exchangeRate = "exchangeRate"
    settlementCurrency = "settlementCurrency"
    paymentCurrency = "paymentCurrency"
    adjPrice = "adjPrice"
    commPerShare = "commPerShare"
    feesPerShare = "feesPerShare"
    shortType = "shortType"
    positionId = "positionId"
    positionLotId = "positionLotId"


class NewWatchlistsServices(BaseTags):
    watch_list_edit_entry = 'watchList_editEntry'
    watch_list_create = 'watchList_Create'
    watch_list_delete = 'watchList_Delete'
    watch_list_individual = 'watchList_Individual'
    watch_list_list = 'watchList_list'

    watch_list_uuid = 'watchListUuid'
    watch_list_name = 'watchListName'
    watch_list_id = 'watchListId'
    watch_list_uuuids = "watchListUuids"

    marker = 'marker'
    action = 'action'
    entries = 'entries'
    entry_id = 'entryId'
    symbol = 'symbol'
    new_index_id = 'newIndexId'
    typeCode = "typeCode"

    views_watchList_editEntry = {watch_list_uuid, watch_list_name, marker, action, entries}
    views_watchList_editEntry_entries = {entry_id, symbol}
    views_watchList_Create = {watch_list_name, watch_list_uuid, entries}
    views_watchList_Delete = {watch_list_uuid, entries}
    views_watchList_Individual = {watch_list_uuid, watch_list_name, marker, entries}
    views_watchList_Individual_entries = {entry_id, symbol, typeCode}


class HomeWidgetsServices(BaseTags):
    symbol = 'symbol'
    symbolDescription = 'symbolDescription'
    typeCode = 'typeCode'
    lastPrice = 'lastPrice'
    change = 'change'
    percentChange = 'percentChange'
    volume = 'volume'
    lastTradeTime = 'lastTradeTime'
    timezone = 'timezone'
    openPrice = 'openPrice'
    previousClose = 'previousClose'
    marketCap = 'marketCap'
    averageVolume = 'averageVolume'
    pe = 'pe'
    eps = 'eps'
    nextEarningDate = 'nextEarningDate'

    views_unauthendicated_user = {symbol, symbolDescription}

    references_unauthenticated_user = {symbol, symbolDescription,
                                       typeCode, lastPrice, change,
                                       percentChange, volume,
                                       lastTradeTime, timezone, openPrice,
                                       previousClose, marketCap, averageVolume,
                                       pe, eps, nextEarningDate}


class PortfolioNewsService(BaseTags):
    account_uuids = "account_uuids"
    accountId = "accountId"
    accountMode = "accountMode"
    acctDesc = "acctDesc"
    acctInstType = "acctInstType"
    instNo = "instNo"
    instType = "instType"
    accountShortName = "accountShortName"
    accountLongName = "accountLongName"
    acctType = "acctType"
    accountUuid = "accountUuid"
    isIRA = "isIRA"
    accountIndex = "accountIndex"
    encAccountId = "encAccountId"
    truncatedAccountID = "truncatedAccountID"
    washSaleFlag = "washSaleFlag"
    mdvFlag = "mdvFlag"
    employeeId = "employeeId"
    cSGLongDescription = "cSGLongDescription"
    cSGShortDescription = "cSGShortDescription"
    cSGMobileDescription = "cSGMobileDescription"

    symbols = "symbols"
    title = "title"
    source = "source"
    date = "date"
    url = "url"
    docId = "docId"

    news = "news"
    accounts = "accounts"

    VALID_ACCTUUID = "ODQ3MzAxMDd8QnJva2VyYWdlfEFEUHw2NjY2NjZ8LXwt"
    INVALID_ACCTUUID = "ODQczNDE0NTJ8TWFuYWdlZHxBRFB8NjY2NjY2fC18QmxlbmQgUG9ydGZvbGlvcw=="
    NEWS_SOURCE = {"PR Newswire", "MarketWatch", "Dow Jones",
                   "Reuters", "Briefing.com", "BusinessWire",
                   "TREFIS", "GlobeNewswire"}
    GENERIC_NEWS_DICT = {
        symbols: [],
        title: r"\s+",
        source: r"\s+",
        url: r"https://",
        date: "%Y-%m-%dT%H:%M:%SZ",
        docId: r"[a-z0-9\-]+"

    }

    MAX_LIMIT = 30
    VIEW_BY_SYMBOL_NEWS = []
    VIEW_BY_SYMBOL_NEWS_DICT = {}

    VIEW_DATA_TAG = {account_uuids}
    REF_TYPE = {news, accounts}
    REF_NEWS_TAGS = {symbols, title, source, date, url, docId}

    REF_ACCOUNT_TAGS = {accountId, accountMode, acctDesc, acctInstType,
                        instType, accountShortName, accountLongName, acctType,
                        accountUuid, isIRA, accountIndex, encAccountId}

    REF_SP_ACCOUNT_TAG = {accountId, accountMode, acctDesc, acctInstType,
                          instType, accountShortName, accountLongName, acctType,
                          accountUuid, isIRA, accountIndex, encAccountId,
                          employeeId, cSGLongDescription, cSGShortDescription, cSGMobileDescription}

    REF_BANK_ACCOUNT_TAG = {accountId, accountMode, acctDesc, acctInstType,
                            instType, accountShortName, accountLongName, acctType,
                            accountUuid, isIRA, accountIndex, encAccountId}


class DefaultEntries(BaseConstantMethods):
    EQ = {'symbol': 'AAPL', 'typeCode': 'EQ', "exchangeCode": "NSDQ"}
    OPTN = {'symbol': 'AAPL--220916C00145000', 'typeCode': 'OPTN', "exchangeCode": "CINC"}
    MF = {'symbol': 'VARAX', 'typeCode': 'MF', "exchangeCode": "BETA"}
    INDX = {'symbol': 'SPX', 'typeCode': 'INDX', "exchangeCode": "UNKN"}
    MMF = {'symbol': 'TOSXX', 'typeCode': 'MMF', "exchangeCode": "BETA"}
    BOND = {'symbol': '472319AG7', 'typeCode': 'BOND', "exchangeCode": "NSDQ"}


class MgsViews(BaseTags):
    type_data = {BaseTags.type, BaseTags.data}
    type_data_cta_action = {BaseTags.type, BaseTags.data, BaseTags.cta, BaseTags.action}

    account_uuids = 'account_uuids'
    account_summary_label = 'account_summary_label'
    account_summary_streamable_value = 'account_summary_streamable_value'
    completeview_net_access = {account_uuids,
                               account_summary_label,
                               account_summary_streamable_value}

    account_uuid = 'account_uuid'
    account_name = 'account_name'
    account_detail_label = 'account_detail_label'
    account_detail_value = 'account_detail_value'
    account_additional_labels = 'account_additional_labels'
    account_extra_details = 'account_extra_details'
    accounts_account_summary = {account_uuid, account_name,
                                account_detail_label,
                                account_detail_value,
                                account_additional_labels}

    allbrokerage_account_summary = {account_detail_label,
                                    account_detail_value,
                                    account_additional_labels,
                                    account_extra_details}

    individual_account_summary = {account_uuid,
                                  account_detail_label,
                                  account_detail_value,
                                  account_additional_labels,
                                  account_extra_details}

    account_additional_label_title = "account_additional_label_title"
    account_additional_label_streamable_value = "account_additional_label_streamable_value"
    account_additional_label_value_detail = "account_additional_label_value_detail"
    additional_labels = {account_additional_label_title,
                         account_additional_label_streamable_value,
                         account_additional_label_value_detail}

    completeview_additional_label_cash = {account_additional_label_title,
                                          account_additional_label_streamable_value}

    initial = 'initial'
    local_field_name = 'local_field_name'
    stream_id = 'stream_id'
    movement_type = 'movement_type'
    streamable_value = {initial,
                        local_field_name,
                        stream_id,
                        movement_type}

    accountUuid = 'accountUuid'
    position_lots = 'position_lots'
    positions = 'positions'
    position_lot_list = {accountUuid,
                         position_lots}
    position_list = {accountUuid,
                     positions}
    account_portfolio_list = {account_uuid,
                              positions}
    account_list = {account_uuids}
    net_assets_summary = {account_uuids,
                          account_summary_label,
                          account_summary_streamable_value}

    watchList_editEntry = {}


class MainMenuTagsConstant(BaseConstantMethods):
    LABEL_MAP = {
        "Alerts": {
            "display_type": "MenuItemViewWithCount", "icon": "ic_alerts",
            "app_url": "etrade://show/alerts", "webview_url": ""
        },
        "Check Deposit": {
            "display_type": "MenuItemView", "icon": "ic_check_deposit",
            "app_url": "etrade://show/checkDeposit", "webview_url": ""
        },
        "Transfer": {
            "display_type": "MenuItemView", "icon": "ic_transfer",
            "webview_url": "", "app_url": "etrade://menu/transfer"
        },
        "My Profile": {
            "display_type": "MenuItemView", "icon": "ic_profile", "webview_url": "",
            "app_url": "etrade://menu/myProfile"
        },
        "Tax Documents": {
            "display_type": "MenuItemView", "icon": "ic_tax_documents", "webview_url": "",
            "app_url": "etrade://menu/taxDocuments"
        },
        "Settings": {
            "display_type": "MenuItemView", "icon": "ic_settings", "webview_url": "",
            "app_url": "etrade://show/settings"
        },
        "Customer Service": {
            "display_type": "MenuItemView", "icon": "ic_customer_service", "webview_url": "",
            "app_url": "etrade://menu/customerService"
        },
        "Quotes": {
            "display_type": "MenuItemView", "icon": "ic_quotes", "webview_url": "",
            "app_url": "etrade://show/quotes"
        },
        "News": {
            "display_type": "MenuItemView", "icon": "ic_news", "webview_url": "",
            "app_url": "etrade://show/news"
        },
        "Learn": {
            "display_type": "MenuItemView", "icon": "ic_knowledge", "webview_url": "",
            "app_url": "etrade://show/learn"
        },
        "Open Account": {
            "display_type": "MenuItemView", "icon": "", "webview_url": "",
            "app_url": "etrade://show/openAccount"
        },
        "Knowledge Base": {
            "display_type": "MenuItemView", "icon": "ic_knowledge",
            "webview_url": "/knowledge/investing-basics", "app_url": ""
        }
    }


class TransferActivityTagsConstants(BaseTags):
    type_data_cta_action = {BaseTags.type, BaseTags.data, BaseTags.cta, BaseTags.action}
    type_data = {BaseTags.type, BaseTags.data}
    account_uuids = "account_uuids"
    transfer_activity_ids = "transferActivityIds"
    accountId = "accountId"
    accountMode = "accountMode"
    acctDesc = "acctDesc"
    acctInstType = "acctInstType"
    instNo = "instNo"
    instType = "instType"
    accountShortName = "accountShortName"
    fromAccountShortName = "fromAccountShortName"
    toAccountShortName = "toAccountShortName"
    accountLongName = "accountLongName"
    acctType = "acctType"
    accountUuid = "accountUuid"
    isIRA = "isIRA"
    accountIndex = "accountIndex"
    encAccountId = "encAccountId"
    truncatedAccountID = "truncatedAccountID"
    reference_type_accounts_data_tags = {accountId, accountMode, acctDesc, acctInstType, instNo, instType,
                                         accountShortName, accountLongName, acctType, accountUuid, isIRA, accountIndex,
                                         encAccountId, truncatedAccountID}

    transferType = "transferType"
    status = "status"
    from_key = "from"
    to = "to"
    amount = "amount"
    date = "date"
    repeat = "repeat"
    confirmationNumber = "confirmationNumber"
    activity_id = "activityId"
    reference = "reference"
    id = "paymentId"
    memo = "memo"
    app_name = "appName"
    refrence_type_transfer_activity_tags = {accountUuid, fromAccountShortName, toAccountShortName, transferType,
                                            status, from_key, to, amount, date, repeat, activity_id, reference,
                                            id, memo, app_name}
    status_dict = {"PENDING": "In process", "RETRY": "In process", "UNDER_REVIEW": "In process",
                   "COMPLETED": "Complete", "PROCESSED": "Complete", "SCHEDULED": "Scheduled",
                   "CANCELLED": "Canceled", "DELETED": "Canceled", "RETURNED": "Rejected",
                   "FAILED": "Failed", "ERROR": "Failed", "VOID": "Canceled", "ACTION_REQUIRED": "Action Required",
                   "DONE": "DONE"}


class MsUserPreferenceReferenceTags():
    ms_user_preferences = 'ms_user_preferences'
    login_uuid = 'login_uuid'
    isMSfeatureEnabled = 'isMSfeatureEnabled'
    isUserPilot = 'isUserPilot'
    isDualUser = 'isDualUser'
    msAccountVizPilotUser = 'msAccountVizPilotUser'
    isFAVisibilityEnabled = 'isFAVisibilityEnabled'


class MsUserReferenceCtaTags():
    cta_label = 'cta_label'
    cta_title = 'cta_title'
    cta_action = 'cta_action'
    cta_label_default_values = ["MS Settings", "MS Enrollment"]
    cta_title_default_values = ["Morgan Stanley Settings", "Display Accounts"]
    cta_action_webview_values = ["/etx/hw/mssettings",
                                 "/etx/pxy/morgan-stanley/account-visibility-enrollment"]


class SmsessionTags():
    sm_tag_url = 'https://us.{0}.etrade.com/auth/api/sm2access'
    transormation_clientid = 'transformationClientId'
    transormation_clientid_value = 'b6bc50a1-40d5-464e-846a-a6ca8f95ac20'
    transformationType = 'transformationType'
    transformationType_value = 'sm2jwt'


class ApigeeDataTags():
    apigee_url = 'https://msout-shared.{0}.etrade.com/phx/et-ebc-positions-business-pc/balances-business/v1/' \
                 'balances/getDetails'
    requestType = 'requestType'
    requestType_value = 'CLIENT'
    timePeriod = 'timePeriod'
    timePeriod_value = 'INTRADAY'
    expand = 'expand'
    expand_value = 'TOTALBALANCE,LIABILITYCLASSIFICATION'


class MsCompleteViewAccountSectionTags():
    account_uuid = 'account_uuid'
    account_label = 'account_label'
    account_footnotes = 'account_footnotes'
    account_additional_labels = 'account_additional_labels'


class MsCompleteViewReferenceTags():
    accountUuid = 'accountUuid'
    accountType = 'accountType'
    keyAccountId = 'keyAccountId'
    platform = 'platform'
    pledgeIndicator = 'pledgeIndicator'
    accountDisplayName = 'accountDisplayName'
    accountDisplayNumber = 'accountDisplayNumber'
    instType = 'instType'
    balanceType = 'balanceType'
    balance = 'balance'
    ms_user_preferences = 'ms_user_preferences'
    isEnrolledForDualAcctVisibility = 'isEnrolledForDualAcctVisibility'


class MsCompleteViewTags():
    account_uuids = 'account_uuids'
    account_summary_label = 'account_summary_label'
    account_additional_labels = 'account_additional_labels'
    account_sections = 'account_sections'
    account_uuids_dict = {"ms-et-post1": {"sit": "CCFDBBD5-0589-402D-8CB8-1A4EBC60CA88",
                                          "uat": "BBEA1F7A-6942-4BF1-BCC1-6451C1F99873", "prd": ""},
                          "ms-et-post2": {"sit": "A99A00B1-88AE-46F3-9016-6EE3E4CAF39E",
                                          "uat": "CBCD85AA-96E4-4717-A459-E108F156FE9A", "prd": ""},
                          "ms-et-pre2": {"sit": "92691D63-B76D-4819-9E1A-4BB622805984"}

                          }


class NasdaqloginTags():
    quote_type_dict = {"nasdaq1": {"sit": "1", "uat": "1"},
                       "nasdaq2": {"sit": "2", "uat": "2"},
                       "nasdaq4": {"sit": "4", "uat": "4"},
                       "nasdaq5": {"sit": "5", "uat": "5"}
                       }
