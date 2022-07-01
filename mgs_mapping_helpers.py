"""Do not auto-format please"""
from collections import ChainMap

from test_helpers.mgs_backend_service_helpers.accounts_backend_data_helper import AccountsBackendDataHelper
from test_helpers.mgs_backend_service_helpers.backend_requests import get_stock_plan_user_balances
from test_helpers.mgs_validation_helpers.mgs_tag_helper import AccountListAccountsTags, AccountOverviewAccountsTags, \
    CompleteViewAccountsTags, AllBrokerageAccountsTags, IndividualAccountsTags
from test_helpers.mgs_validation_helpers.references.mgs_objects import Account, AccountUuid
from test_helpers.utils import _list, _dict_by_id
from test_helpers.mgs_validation_helpers.uuid_mixin import UuidMixin
import logging

INSTITUTION_MAP = {
    '666666': 'ADP',
    '1000001': 'TELEBANK'
}
INSTITUTION_ID_TO_ACCOUNT_TYPE_MAP = {
    "ADP": "Brokerage",
    "TELEBANK": "Bank",
    "OLINK": "ESP"
}

NO_DATA = '--'

IRA_TYPES = [
    'CONTRIBUTORY',
    'BENF ESTATE IRA',
    'BENF ROTH ESTATE IRA',
    'BENF ROTH TRUST IRA',
    'BENF TRUST IRA',
    'BENF MINOR IRA',
    'BENF ROTH MINOR IRA',
    'BENFIRA',
    'BENFROTHIRA',
    'CONVERSION ROTH IRA',
    'IRA ROLLOVER',
    'ROTH IRA MINORS',
    'ROTHIRA',
    'SARSEPIRA',
    'SEPIRA',
    'SIMPLE IRA',
    'TRD IRA MINORS',
    'COVERDELL ESA',
    'IRA',
    'PROFIT SHARING',
    'MONEY PURCHASE',
    'INDIVIDUAL K',
    'ROTH INDIVIDUAL K'
]

BALANCE_MAP = {
    'CASH_AVAILABLE_FOR_WITHDRAWAL': 'cashAvailableForWithdrawal',
    'MARGIN_AVAILABLE_FOR_WITHDRAWAL': 'marginAvailableForWithdrawal',
    'BUYPWR': 'purchasingPower',
    'TOTAL_AVAILABLE_FOR_WITHDRAWAL': 'totalAvailableForWithdrawal',
    'NET_MARKET_VAL': 'accountValue',
    'TOTAL_EQUITY': 'totalEquity',
    'AVAIL_BALANCE': 'availableBalance',
    'CASH_BALANCE': 'totalBalance',
    'TOTAL_GRANT_BAL': 'totalBalance'
}

PRD_TYPE_BOND = 'BOND'
PRD_TYPE_MF = 'MF'
PRD_TYPE_MMF = 'MMF'
PRD_TYPE_OPTN = "OPTN"
BOND_VFACTOR = '100.0'
OPTION_MULTIPLIER_DEFAULT = 100

service_name_to_AccountsTagSchema_map = {
    "accountList": AccountListAccountsTags,
    "accountOverview": AccountOverviewAccountsTags,
    "completeView": CompleteViewAccountsTags,
    "all": AllBrokerageAccountsTags,
    "individual": IndividualAccountsTags
}

streaming_to_account_type_map = {
    "Brokerage": True,
    "Managed": True,
    "Bank": False,
    "ESP": False,
    "EAS": False
}


class MGSMappingTools(UuidMixin):
    pass


class QuotesMapping(MGSMappingTools):
    """
    Class is responsible for providing general methods to return mgs references "positions" and "instruments" objects.
    Values in provided objects are corresponding values from s2 service response.
    Class is working with parsed s2 responses, that follow same structure for position info storing, like
    GetPortfolioInfoResponse, WatchList_GetPortfolioView, and contain "Portfolios", "BasicQuote",.. sections.

    To get s2-mapped-object you need to:
    - Implement __init__ method in child class, or method for getting s2 response as input data
    - Override  pos(self) in child class(define what kind of id will be used to get related info from parsed s2 dict)
     self.pos property should return {"some_object_id":"123", "Portfolios":{..}, "BasicQuote":{..},..} type of dict
    - Override position_ids_update and/or instrument_ids_update methods to get id key-value pair,specific to needed obj.

    """

    @property
    def pos(self):
        """
        Pointer to current position/entry
        :return: dict
        """
        return {}

    @property
    def portfolio(self):
        return self.pos['Portfolios']

    @property
    def basic_quote(self):
        return self.pos['BasicQuote']

    @property
    def detailed_quote(self):
        return self.pos['DetailedQuote']

    @property
    def options(self):
        return self.pos['Options']

    @property
    def expiration_date(self):
        exp_day_str = f"{self.options['Expiration']['Month']}/" \
                      f"{self.options['Expiration']['Day']}/" \
                      f"{self.options['Expiration']['Year']}"

        muted = exp_day_str == "0/0/0"
        return "--" if muted else exp_day_str

    # position:
    def get_position(self):
        """
        Method for getting position object.
        Will get "mgs-key":"s2-value" pairs separately from BasicQuote, Portfolios, Options sections, ids of positions
        and values hardcoded to zeroes by calling respective methods below.
        :return: dict
        """
        position = {}
        position.update(self.position_ids_update())
        position.update(self.position_portfolios_update())
        position.update(self.position_basic_quote_update())
        # position.update(self.position_zero_values_update())
        position.update(self.position_option_update())

        self.update_bond_position(position)
        self.update_option_position(position)

        return position

    def update_option_position(self, position: dict):
        update = {}
        if self.basic_quote['TypeCode'] == PRD_TYPE_OPTN:
            quantity = int(self.portfolio['Quantity']) * OPTION_MULTIPLIER_DEFAULT
            today_quantity = int(self.portfolio.get('TodayQuantity', 0)) * OPTION_MULTIPLIER_DEFAULT

            update = {
                'quantity': quantity,
                'todayQuantity': today_quantity,

            }
        position.update(update)

    def position_ids_update(self):
        return {}

    def position_portfolios_update(self):
        """
        Values for position that places in Portfolios section
        :return: dict
        """
        has_lots_flag = False  # TODO: behaviour undefined now
        commission = self.portfolio['Commissions']
        today_commissions = self.portfolio.get('TodayCommissions', 0)
        fees = self.portfolio['OtherFees']
        quantity = self.portfolio['Quantity']
        today_quantity = self.portfolio.get('TodayQuantity', 0)
        display_quantity = quantity
        basis_price = self.portfolio['PricePaid']
        price_paid = self.portfolio['PricePaid']
        today_price_paid = self.portfolio.get('TodayPricePaid', 0)
        days_gain_value = self.portfolio.get('DaysGainVal', 0)
        total_gain_value = self.portfolio.get('TotalGainVal', 0)
        days_gain_percentage = self.portfolio.get('DaysGainPct', 0)
        total_gain_percentage = self.portfolio.get('TotalGainPct', 0)
        days_purchase = self.portfolio.get('TodayQuantity', '0') != '0'
        market_value = self.portfolio['MarketValue']

        portfolio_update = {
            "hasLots": has_lots_flag,
            "commission": commission,
            "todayCommissions": today_commissions,
            "fees": fees,
            "marketValue": float(market_value),
            "quantity": quantity,
            "todayQuantity": today_quantity,
            "displayQuantity": display_quantity,
            "basisPrice": basis_price,
            "pricePaid": price_paid,
            "todayPricePaid": today_price_paid,
            "daysGainValue": days_gain_value,
            "totalGainValue": total_gain_value,
            "daysGainPercentage": days_gain_percentage,
            "totalGainPercentage": total_gain_percentage,
            "daysPurchase": days_purchase,
        }
        return portfolio_update

    def position_basic_quote_update(self):
        """
        Values for position that places in BasicQuote section
        :return: dict
        """
        symbol = self.basic_quote['Symbol']
        todays_close = self.basic_quote['LastTrade']
        mark_to_market = self.basic_quote['MarkToMarket']
        last_trade_time = self.basic_quote['LastTradeTime']
        previous_close = self.basic_quote['PreviousClose']
        volume = self.basic_quote['Volume']
        is_price_adjusted = self.basic_quote['IsPriceAdjusted']
        adj_last_trade = self.basic_quote['AdjLastTrade']
        ad_previous_close = self.basic_quote['AdjPreviousClose']

        day_change_value = self.basic_quote['ChangeVal']  # mapped in market hours
        day_change_perc = self.basic_quote['ChangePct']
        display_symbol = self.basic_quote['DisplaySymbol']

        basic_quote_update = {
            "symbol": symbol,
            "todaysClose": todays_close,
            "markToMarket": mark_to_market,
            "lastTradeTime": last_trade_time,
            "previousClose": previous_close,
            "volume": volume,
            "isPriceAdjusted": is_price_adjusted,
            "adjLastTrade": adj_last_trade,
            "adjPreviousClose": ad_previous_close,

            "dayChangeValue": day_change_value,
            "dayChangePerc": day_change_perc,
            "displaySymbol": display_symbol
        }
        return basic_quote_update

    @staticmethod
    def position_zero_values_update():

        ext_hr_change_value = 0
        ext_hr_change_perc = 0
        ext_hr_last_price = 0

        zero_values_update = {

            "extHrChangeValue": ext_hr_change_value, "extHrChangePerc": ext_hr_change_perc,
            "extHrLastPrice": ext_hr_last_price}
        return zero_values_update

    def position_option_update(self):
        base_symbol_price = self.options['BaseSymbolPrice']
        in_the_money_flag = self.options['InTheMoneyFlag']
        option_underlier = self.options['OptionUnderlier'] or 0
        strike_price = self.options['StrikePrice']

        option_update = {
            # "baseSymbolPrice": base_symbol_price,
            "inTheMoneyFlag": in_the_money_flag,
            "optionUnderlier": option_underlier,
            "strikePrice": strike_price,
        }
        return option_update

    def update_bond_position(self, position):
        bond_update = {}
        if self.pos['BasicQuote']['TypeCode'] == 'BOND':
            maturity = f"{self.pos['Bond']['Maturitydate']['Month']}/" \
                       f"{self.pos['Bond']['Maturitydate']['Day']}/" \
                       f"{self.pos['Bond']['Maturitydate']['Year']}"
            bond_update = {
                "symbol": self.pos['BasicQuote']['SymbolDesc'],
                "basisPrice": self.pos['BasicQuote']['SymbolDesc'],
                "bondRate": self.pos['Bond']['CouponRate'],
                "bondFactor": BOND_VFACTOR,
                "maturity": maturity,
            }
        position.update(bond_update)

    # instrument:
    def get_instrument(self):
        """
        Method for getting instrument object.
        Will get "mgs-key":"s2-value" pairs separately from BasicQuote, DetailedQuote, Portfolios, Options sections,
        ids of instrument and values hardcoded to zeroes by calling respective methods below.
        :return: dict
        """
        instrument = {}
        instrument.update(self.instrument_ids_update())
        instrument.update(self.instrument_portfolio_update())
        instrument.update(self.instrument_basic_quote_update())
        instrument.update(self.instrument_zero_values_update())
        instrument.update(self.instrument_option_update())
        instrument.update(self.instrument_detailed_quote_update())
        instrument.update(self.instrument_fundamentals_update())

        instrument.update(self.update_option_instrument())

        self.update_bond_instrument(instrument)

        return instrument

    def instrument_ids_update(self):
        return {}

    def instrument_portfolios_update(self):
        """
        Values for instrument that places in Portfolios section
        :return: dict
        """
        market_value = self.portfolio['MarketValue']
        return {"marketValue": market_value}

    def instrument_basic_quote_update(self):
        symbol = self.basic_quote['Symbol']
        display_symbol = self.basic_quote['DisplaySymbol']
        type_code = self.basic_quote['TypeCode']
        volume = float(self.basic_quote['Volume'])
        last_price = self.basic_quote['LastTrade']
        mark_to_market = self.basic_quote['MarkToMarket']
        last_trade_time = self.basic_quote['LastTradeTime']
        previous_close = self.basic_quote['PreviousClose']
        is_price_adjusted = self.basic_quote['IsPriceAdjusted']
        adj_last_trade = self.basic_quote['AdjLastTrade']
        adj_previous_close = self.basic_quote['AdjPreviousClose']

        day_change_value = self.basic_quote['ChangeVal']  # mapped in market hours
        day_change_perc = self.basic_quote['ChangePct']

        instrument_update = {
            "symbol": symbol,
            "displaySymbol": display_symbol,
            "typeCode": type_code,
            "volume": volume,
            "lastPrice": last_price,
            "markToMarket": mark_to_market,
            "lastTradeTime": last_trade_time,
            "previousClose": previous_close,
            "isPriceAdjusted": is_price_adjusted,
            "adjLastTrade": adj_last_trade,
            "adjPreviousClose": adj_previous_close,

            "dayChangeValue": day_change_value,
            "dayChangePerc": day_change_perc
        }

        return instrument_update

    @staticmethod
    def instrument_zero_values_update():
        open_interest = 0
        day_change_value = 0
        day_change_perc = 0
        ext_hr_change_value = 0
        ext_hr_change_perc = 0
        ext_hr_last_price = 0

        instrument_zero_values = {
            "openInterest": open_interest,
            # "dayChangeValue": day_change_value,
            # "dayChangePerc": day_change_perc,
            "extHrChangeValue": ext_hr_change_value,
            "extHrChangePerc": ext_hr_change_perc,
            "extHrLastPrice": ext_hr_last_price,
        }
        return instrument_zero_values

    def instrument_option_update(self):
        implied_volatility_pct = float(self.options['IvPct']) * 100  # fractions to percentage
        delta = self.options['Delta']
        premium = self.options['Premium']
        gamma = self.options['Gamma']
        vega = self.options['Vega']
        theta = self.options['Theta']
        expiration_date = self.expiration_date
        underlying_type_code = '--'  # check for type code will be in self.update_option_instrument
        underlying_exchange_code = '--'  # IF type= OPTN, this values will be overwritten
        underlying_symbol = '--'  # In other cases, as for MGS, this will be "--"
        days_expiration = self.options['DaysExpiration']

        instrument_option_update = {
            "impliedVolatilityPct": implied_volatility_pct,
            "delta": delta,
            "premium": premium,
            "gamma": gamma,
            "vega": vega,
            "theta": theta,

            "expirationDate": expiration_date,
            "underlyingTypeCode": underlying_type_code,
            "underlyingExchangeCode": underlying_exchange_code,
            "underlyingSymbol": underlying_symbol,

            "daysExpiration": days_expiration
        }
        return instrument_option_update

    def instrument_detailed_quote_update(self):
        exchange_code = self.detailed_quote['Exchange']
        bid = self.detailed_quote['Bid']
        ask = self.detailed_quote['Ask']
        market_cap = self.detailed_quote['MarketCap']
        week52_high = self.detailed_quote['Week52High']
        week52_low = self.detailed_quote['Week52Low']

        detailed_quote_update = {
            "exchangeCode": exchange_code,
            "bid": bid,
            "ask": ask,
            "marketCap": market_cap,
            "week52High": week52_high,
            "week52Low": week52_low
        }
        return detailed_quote_update

    def instrument_portfolio_update(self):
        return {"marketValue": float(self.pos['Portfolios']['MarketValue'])}

    def instrument_fundamentals_update(self):
        fundamentals = {
            "pe": self.pos['Fundamentals']['PeRatio'],
            "eps": self.pos['Fundamentals']['Eps'],
        }
        return fundamentals

    def get_has_lots(self):
        if self.portfolio.get("MultipleLotFlag"):
            has_lot = self.portfolio["MultipleLotFlag"]
            return int(has_lot) != 0
        return False

    def get_instrument_id(self):
        try:
            i_id = self.pos.get('PfAddlInfo')['InstrumentId']
            return i_id
        except TypeError:
            return ""

    def update_bond_instrument(self, instrument):
        bond_update = {}
        if self.pos['BasicQuote']['TypeCode'] == 'BOND':
            bond_update['symbol'] = self.pos['BasicQuote']["SymbolDesc"]
        instrument.update(bond_update)

    def update_option_instrument(self):
        update = {}
        if self.basic_quote['TypeCode'] == PRD_TYPE_OPTN:
            expiration_date = self.expiration_date
            underlying_type_code = self.options['UnderlyingProductId']['TypeCode']
            underlying_type_code = underlying_type_code or ""
            underlying_exchange_code = self.options['UnderlyingProductId']['ExchangeCode']
            underlying_exchange_code = underlying_exchange_code or ""
            underlying_symbol = self.options['UnderlyingProductId']['Symbol']
            open_interest = self.options['OpenInterest']

            update = {
                "expirationDate": expiration_date,
                "underlyingTypeCode": underlying_type_code,
                "underlyingExchangeCode": underlying_exchange_code,
                "underlyingSymbol": underlying_symbol,

                "openInterest": open_interest,
            }
        return update


class PositionsInstrumentsMap(QuotesMapping):
    """
    All Brokerage, Individual Brokerage, Tax Lots services, references objects "positions", "instruments"
    """

    def __init__(self, portfolio_info: dict, position_id: str):
        self.response = portfolio_info
        self._position_id = position_id
        self.position_by_id = self.get_position_by_id(portfolio_info)

    def get_position_by_id(self, portfolio_info):
        portfolio_info = portfolio_info['Output']
        position_list = _list(portfolio_info['PositionList'])
        position_by_account = _dict_by_id(position_list, 'PositionId')
        return position_by_account

    @property
    def pos(self):
        return self.position_by_id[self._position_id]

    def position_ids_update(self):
        account_id = self.pos['AccountId']
        position_id = self.pos['PositionId']
        account_uuid = ""

        position_ids_update = {"accountUuid": account_uuid,
                               "accountId": account_id,
                               "positionId": position_id
                               }
        return position_ids_update

    def instrument_ids_update(self):
        instrument_id = self.get_instrument_id()
        position_id = self.pos['PositionId']

        instrument_ids_update = {
            "instrumentId": instrument_id,
            "positionId": position_id
        }
        return instrument_ids_update


class WatchlistEntryMap(QuotesMapping):
    def __init__(self, portfolio_view_response, entry_id):
        self.response = portfolio_view_response
        self.entry_id = entry_id
        self.entry_by_id = self.get_element_by_id(portfolio_view_response)

    def get_element_by_id(self, response):
        output = response['Output']
        entry_list = _list(output["EntryList"])
        entry_by_id = _dict_by_id(entry_list, 'EntryId')
        return entry_by_id

    @property
    def pos(self):
        return self.entry_by_id[self.entry_id]

    def position_ids_update(self):
        watchlist_id = self.response['Output']['PortfolioId']
        entry_id = self.pos['EntryId']

        entry_id_update = {
            "watchListUuid": self.as_base64_string(watchlist_id),
            "watchListId": watchlist_id,
            "entryId": entry_id
        }
        return entry_id_update

    def instrument_ids_update(self):
        watchlist_id = self.response['Output']['PortfolioId']
        entry_id = self.pos['EntryId']
        instrument_id = 0

        return {"watchListId": watchlist_id, "entryId": entry_id, "instrumentId": instrument_id}

    def get_watchlist_entry(self):
        """Entry Object from AddWatchlistEntry response"""
        default_map = {
            "entryId": self.pos['EntryId'],
            "symbol": self.pos['BasicQuote']['Symbol'],
            "commission": 0,
            "todayCommissions": 0,
            "fees": 0,
            "quantity": 1,
            "basisPrice": 0,
            "baseSymbolPrice": 0,
            "pricePaid": self.pos['BasicQuote']['LastTrade'],
            "todayPricePaid": self.pos['BasicQuote']['LastTrade'],
            "daysGainValue": self.pos['BasicQuote']['ChangeVal'],
            "totalGainValue": 0,
            "daysGainPercentage": 0,
            "totalGainPercentage": 0,
            "daysPurchase": True,
            "todaysClose": 0,
            # "lastTradeTime": self.pos['BasicQuote']['LastTradeTime']
        }
        return default_map


class HomeWidgetMap(MGSMappingTools):
    def __init__(self, s2_backend_response):
        self.response = s2_backend_response

    def get_instruemt_widges(self):
        addlstock = self.response['Qaddl']['Addlstock']
        qcommon = self.response['Qcommon']

        instruments_widgets = {}
        instruments_widgets.update(self.instrument_widgets_qcommon_update(qcommon))
        instruments_widgets.update(self.instrument_widgets_addlstock_update(addlstock))
        return instruments_widgets

    def instrument_widgets_qcommon_update(self, qcommon):
        """
        Values for instruments_widgets that places in QCommon section
        :return: dict
        """

        symbol = qcommon['Pid']['Symbol']
        type_code = qcommon['Pid']['TypeCode']
        change = qcommon['Change']
        volume = round(float(qcommon['Volume']), 2)
        last_trade_time = round(float(qcommon['Timestamp']), 2)
        timezone = qcommon['Timezone']
        open_price = qcommon['Open']
        previous_close = qcommon['PrevClose']
        market_cap = qcommon['MarketCap']

        qcommon_quote_update = {
            "symbol": symbol,
            "typeCode": type_code,
            "change": change,
            "volume": volume,
            "lastTradeTime": last_trade_time,
            "timezone": timezone,
            "openPrice": open_price,
            "previousClose": previous_close,
            "marketCap": market_cap,

        }
        return qcommon_quote_update

    def instrument_widgets_addlstock_update(self, addlstock):
        """
        Values for instruments_widgets that places in Addlstock section
        :param addlstock:
        :return: dict
        """

        last_price = addlstock['AdjustedLast']
        average_volume = addlstock['Avgvol10d']
        pe = addlstock['Pe']
        eps = addlstock['Eps']
        next_earnings_date = self.next_earnings_date(addlstock)

        addlstock_quote_update = {

            "lastPrice": last_price,
            "averageVolume": average_volume,
            "pe": pe,
            "eps": eps,
            "nextEarningDate": next_earnings_date
        }
        return addlstock_quote_update

    def next_earnings_date(self, addlstock):
        """
        dict value of s2 data reoragnaised according to mgs dict
        :param addlstock:
        :return: dicts
        """

        day = addlstock['Nextearningsdate']['Day']
        month = addlstock['Nextearningsdate']['Month']
        year = addlstock['Nextearningsdate']['Year']

        next_earnings_date = {

            "day": day,
            "month": month,
            "year": year
        }
        return next_earnings_date


class ReferencesTaxLotMap(MGSMappingTools):
    def __init__(self, portfolio_info_lot, position_lot_id):
        self.response = portfolio_info_lot
        self.position_lot_id = position_lot_id
        self.lot_by_position = self.get_lot_by_position_id(portfolio_info_lot)

    def get_lot_by_position_id(self, response):
        _position_list = response['Output']["PositionList"]
        _lot_list = _list(_position_list['LotList'])
        lot_by_position = _dict_by_id(_lot_list, 'PositionLotId')
        return lot_by_position

    @property
    def pos(self):
        return self.lot_by_position[self.position_lot_id]

    @property
    def lot(self):
        return self.pos['Lot']

    def get_tax_lot(self):
        lot = {}
        lot.update(self.lot_ids_update())
        lot.update(self.lot_hardcoded_values())
        lot.update(self.position_lot_change_update())
        lot.update(self.position_lot_update())

        return lot

    def lot_ids_update(self):
        position_lot_id = self.lot['PositionLotId']
        position_id = self.lot['PositionId']

        lot_ids_update = {
            'positionLotId': position_lot_id, 'positionId': position_id
        }
        return lot_ids_update

    def position_lot_update(self):
        term_code = self.lot['TermCd']
        price = self.lot['Price']
        lot_source_code = self.lot['LotSourceCd']
        original_qty = self.lot['OriginalQty']
        remaining_qty = self.lot['RemainingQty']
        available_qty = self.lot['AvailableQty']
        order_no = self.lot['CreateOrderNo']
        leg_no = self.lot['CreateLegNo']
        acquired_date = self.lot.get('AdjCreatePsnDt', 0)
        location_code = self.lot['LocationCd']
        exchange_rate = self.lot['ExchgRate']['Rate']
        settlement_currency = self.lot['ExchgRate']['SettlementCurrency'] or ""
        payment_currency = self.lot['ExchgRate']['PaymentCurrency'] or ""
        comm_per_share = self.lot['CommPerShare']
        fees_per_share = self.lot['FeesPerShare']

        position_lot_update = {
            "termCode": term_code,
            "price": price,
            "lotSourceCode": lot_source_code,
            "originalQty": original_qty,
            "remainingQty": remaining_qty,
            "availableQty": available_qty,
            "orderNo": order_no,
            "legNo": leg_no,
            "acquiredDate": acquired_date,
            "locationCode": location_code,
            "exchangeRate": exchange_rate,
            "settlementCurrency": settlement_currency,
            "paymentCurrency": payment_currency,
            "commPerShare": comm_per_share,
            "feesPerShare": fees_per_share,
        }
        return position_lot_update

    def position_lot_change_update(self):
        days_gain = self.pos['DaysGainVal']
        days_gain_pct = self.pos['DaysGainPct']
        market_value = self.pos['MarketValue']
        total_cost = self.pos['TotalCost']
        total_cost_for_gain_pct = self.pos['TotalCostGainPct']
        total_gain = self.pos['TotalGainVal']
        total_gain_pct = total_cost_for_gain_pct

        lot_change_update = {
            "daysGain": days_gain,
            "daysGainPct": days_gain_pct,
            "marketValue": market_value,
            "totalCost": total_cost,
            "totalCostForGainPct": total_cost_for_gain_pct,
            "totalGain": total_gain,
            "totalGainPct": total_gain_pct
        }
        return lot_change_update

    @staticmethod
    def lot_hardcoded_values():
        hardcoded_update = {

            "adjPrice": '0.0',
            "shortType": '1',
        }
        return hardcoded_update


class ReferencesAccountsMapping(MGSMappingTools):
    """
    mapping = ReferencesAccountsMapping(user_id)
    mapping.get_description(uuid)
    mapping.get_balances(uuid)
    ...
    mapping.get_account(account_uuid, service_request)
    """
    _AcctCommonGet_response = None
    _GetAllBalances_response = None
    _SPUserBalances_response = None
    _GetPortfolioTotals_response = None

    def __init__(self, user_id):
        logging.debug(f"Creating AccountsMapping with {user_id} user id")
        self._user_id = user_id

        self._current_acct = None

    @property
    def current_acct(self) -> AccountUuid:
        return self._current_acct

    @current_acct.setter
    def current_acct(self, account_uuid):
        account = AccountUuid.from_string(account_uuid)
        logging.debug(f"Setting {account} as current")
        self._current_acct = account

    @property
    def AcctCommonGet(self):
        if not self._AcctCommonGet_response:
            self._AcctCommonGet_response = self.prepare_accounts_description()
        return self._AcctCommonGet_response[self.current_acct.accountId]

    @property
    def GetAllBalances(self):
        if not self._GetAllBalances_response:
            self._GetAllBalances_response = self.prepare_accounts_balances()
        return self._GetAllBalances_response[self.current_acct.accountId]

    @property
    def SPUserBalances(self):
        if not self._SPUserBalances_response:
            self._SPUserBalances_response = self.get_stock_plan_balance()
        return self._SPUserBalances_response

    @property
    def GetPortfolioTotals(self):
        if not self._GetPortfolioTotals_response:
            self._GetPortfolioTotals_response = self.prepare_account_change()
        return self._GetPortfolioTotals_response

    @property
    def CSGAccountInfo(self):  # AcctCommonGet
        stock_account_desc = {}
        for stock_desc in _list(self.AcctCommonGet['CSGAccountInfo']['CSGRecordDetails']):
            if stock_desc['Symbol'] == self._current_acct.symbol:
                stock_account_desc = stock_desc
                break
        return stock_account_desc

    @property
    def custom_mappings(self):
        return {
            "institution_map": INSTITUTION_MAP,
            "institution_id_to_accountType": INSTITUTION_ID_TO_ACCOUNT_TYPE_MAP,
            "ira_types": IRA_TYPES,
            "balances_map": BALANCE_MAP,
            "streaming_map": streaming_to_account_type_map
        }

    def prepare_accounts_description(self):
        account_description = AccountsBackendDataHelper().prepare_accounts_description(self._user_id)
        description_list = _list(account_description["Acctcommons"])
        account_description_by_id = _dict_by_id(description_list, "AcctNo")
        return account_description_by_id

    def prepare_accounts_balances(self):
        all_balances = AccountsBackendDataHelper().prepare_all_balances(self._user_id)
        accounts_balances_info_list = _list(all_balances['AccountBalInfo'])
        accounts_balances_by_id = _dict_by_id(accounts_balances_info_list, 'AcctNo')
        accounts_balances_by_id = self.format_account_balances(accounts_balances_by_id)
        return accounts_balances_by_id

    def get_stock_plan_balance(self):
        balances_moneys = ["ns3:Sellable", "ns3:Exercisable", "ns3:Blocked", "ns3:PreExe", "ns3:PreStl",
                           "ns3:UnsettledCash"]
        potential_benefit_moneys = ["ns3:Unvested", "ns3:ReqAccept", "ns3:PendingRelease", "ns3:Deferred"]

        def calc_balance(balances, money_types):
            balance = 0
            if balances:
                for money_type in money_types:
                    balance = + float(balances[money_type])
            return balance

        employee_id = self.CSGAccountInfo['OlEmpId']
        stock_balances = get_stock_plan_user_balances(employee_id)
        stock_balances = stock_balances['soap:Envelope']['soap:Body']['ns3:getAccountBalancesResponse'][
            'ns3:SPUserBalancesResponse']

        todays_balance = calc_balance(stock_balances.get('ns3:TodayBalances'), balances_moneys)
        yesterday_balance = calc_balance(stock_balances.get('ns3:YesterdayBalances'), balances_moneys)
        potential_benefit = calc_balance(stock_balances.get('ns3:TodayBalances'), potential_benefit_moneys)
        days_gain = todays_balance - yesterday_balance
        account_value = todays_balance + potential_benefit
        if yesterday_balance > 0:
            days_gain_percent = (days_gain / yesterday_balance) * 100
        else:
            days_gain_percent = 0.0
        stock_balances = {
            'today_balance': todays_balance,
            'yesterday_balance': yesterday_balance,
            'daysGain': days_gain,
            'daysGainPercent': days_gain_percent,
            'potentialBenefitValue': potential_benefit,
            'accountValue': account_value
        }
        return stock_balances

    def prepare_account_change(self):
        change_response = AccountsBackendDataHelper(). \
            prepare_brokerage_account_change(user_id=self._user_id, account_id=self.current_acct.accountId)
        change_not_available = {"TodaysGainLoss": 0,
                                'TodaysGainLossPct': 0,
                                "TotalGainLoss": 0,
                                "TotalGainPct": 0}
        account_change = change_response.get('Output', change_not_available)
        return account_change

    @staticmethod
    def format_account_balances(accounts_balances_by_id):
        for account in accounts_balances_by_id:
            account_info_balances = accounts_balances_by_id[account]
            balance_list = account_info_balances.get('Balance')
            if balance_list:
                balance_as_dict = {}
                for balance_type in balance_list:
                    s2_balance_name = balance_type['Name']
                    balance_value = balance_type['Value']
                    # if not in our BALANCE_MAP, use s2 name for balance
                    balance_as_dict.update({s2_balance_name: balance_value})
                    mgs_balance_name = BALANCE_MAP.get(s2_balance_name, s2_balance_name)
                    balance_as_dict.update({mgs_balance_name: balance_value})
                account_info_balances['MGS-Balance'] = balance_as_dict
        return accounts_balances_by_id

    def get_account_attributes(self):
        attributes = {}
        if self.GetAllBalances.get('Attrib'):
            _attributes = _list(self.GetAllBalances.get('Attrib'))
            for attribute in _attributes:
                attributes.update({attribute['Name']: attribute['Value']})
        return attributes

    def get_description_by_uuid(self, uuid):

        self.current_acct = uuid
        return self.account_description()

    def account_description(self):

        account_id = self.AcctCommonGet["Key"]['AcctNo']
        institution_id = self.AcctCommonGet["Key"]['InstNo']
        account_mode = self.AcctCommonGet['Mode']
        account_description = self.AcctCommonGet.get('AcctDescription')
        account_short = self.AcctCommonGet.get('ShortDescription')
        account_long = self.AcctCommonGet.get('LongDescription')

        institution_type = INSTITUTION_MAP[institution_id]
        if self.current_acct.is_stock_plan():
            institution_type = "OLINK"

        account_type = INSTITUTION_ID_TO_ACCOUNT_TYPE_MAP[institution_type]
        if self.current_acct.is_managed():
            account_type = "Managed"

        if self.current_acct.is_stock_plan():
            account_short = self.CSGAccountInfo['CSGShortDescription']
            account_long = self.CSGAccountInfo['CSGLongDescription']

        description = {
            "accountUuid": self.current_acct.uuid,
            "accountId": account_id,
            "accountMode": account_mode,
            "acctDesc": account_description,
            "accountShortName": account_short,
            "accountLongName": account_long,
            "acctType": account_type,
            "instType": institution_type
        }
        return description

    def get_balance_by_uuid(self, uuid):
        self.current_acct = uuid
        return self.account_balance()

    def account_balance(self):

        if self.current_acct.is_stock_plan():
            return {"accountValue": self.SPUserBalances['accountValue']}

        cash_withdrawal = self.GetAllBalances.get("MGS-Balance", {}).get('cashAvailableForWithdrawal')
        margin_withdrawal = self.GetAllBalances.get("MGS-Balance", {}).get('marginAvailableForWithdrawal')
        purchasing_power = self.GetAllBalances.get("MGS-Balance", {}).get('purchasingPower', {})
        total_withdrawal = self.GetAllBalances.get("MGS-Balance", {}).get('totalAvailableForWithdrawal')
        ledger_account_value = self.GetAllBalances.get("MGS-Balance", {}).get('totalBalance')
        account_value = self.GetAllBalances.get("MGS-Balance", {}).get('totalEquity')

        account_mode = self.GetAllBalances['AcctMode']
        account_description = self.GetAllBalances['AcctDesc']
        ma_flag = self.get_ma_flag()
        balances = {
            "cashAvailableForWithdrawal": cash_withdrawal,
            "marginAvailableForWithdrawal": margin_withdrawal,
            "purchasingPower": purchasing_power,
            "totalAvailableForWithdrawal": total_withdrawal,
            "ledgerAccountValue": ledger_account_value,  # no reference
            "accountValue": account_value,

            'accountMode': account_mode,  # this values will be rewrited only if balances needed for this service
            # 'acctDesc': account_description,
            # "maFlag": ma_flag
        }
        return balances

    def get_account_change_by_uuid(self, uuid):

        self.current_acct = uuid
        return self.account_change()

    def account_change(self):
        if self.current_acct.is_stock_plan():
            return {
                'daysGain': self.SPUserBalances['daysGain'],
                "daysGainPercent": self.SPUserBalances['daysGainPercent']
            }

        days_gain = self.GetPortfolioTotals['TodaysGainLoss']
        days_gain_percent = round(float(self.GetPortfolioTotals['TodaysGainLossPct']), 2)  # "0.97444":str-> 97.00:float
        total_gain = self.GetPortfolioTotals['TotalGainLoss']
        total_gain_percent = round(float(self.GetPortfolioTotals['TotalGainPct']), 2)

        change = {
            "daysGain": days_gain,
            "daysGainPercent": days_gain_percent,
            "totalGain": total_gain,
            "totalGainPercent": total_gain_percent
        }
        return change

    def get_account(self, uuid, request, proofs=False, factory=False):

        tag_method_map = {
            "isIRA": self.get_is_ira,
            # "maFlag": self.get_ma_flag,
            "streamingRestrictions": self.get_streaming_restrictions_flag,
            # "washSaleFlag": self.get_wash_sale_flag,
            # "mdvFlag": self.get_mdv_flag,
            "geoDomestic": self.get_geo_domestic_flag,
            "funded": self.get_funded_flag
        }

        self.current_acct = uuid
        account_tags = self.map_request_and_account(request)
        sources_list = []
        account = self.account_description()
        sources_list.append("AcctCommonGet")

        if account_tags.returns_values_for['balances']:
            account.update(self.account_balance())
            sources_list.append("GetAllBalances")

        if account_tags.returns_values_for['change']:
            account.update(self.account_change())
            sources_list.append("GetPortfolioTotals")
        for flag_name in account_tags.flags:
            if flag_name in tag_method_map:
                logging.debug(f"Getting value for flag '{flag_name}'..")
                account.update({flag_name: tag_method_map[flag_name]()})

        for spec_name in account_tags.spec:
            if spec_name in tag_method_map:
                logging.debug(f"Getting value for tag '{spec_name}'..")
                account.update({spec_name: tag_method_map[spec_name]()})
        if factory:
            account = Account.from_dict(account)

        if proofs:
            return account, {
                "AcctCommonGet": self.AcctCommonGet,
                "GetAllBalances": self.GetAllBalances,
                "GetPortfolioTotals": self.GetPortfolioTotals
            }
        return account

    def map_request_and_account(self, request):
        if isinstance(request, str):
            request_name = request
        else:
            request_name = request.get_name()
        service_expected_accounts = service_name_to_AccountsTagSchema_map[request_name]
        account_tags = service_expected_accounts.brokerage_account
        if self.current_acct.is_stock_plan():
            account_tags = service_expected_accounts.stock_plan_account
        if self.current_acct.is_bank():
            account_tags = service_expected_accounts.bank_account
        return account_tags

    def get_funded_flag(self):
        return True  # TODO: funded flag handling

    def get_is_ira(self):
        return True if self.GetAllBalances['AcctType'] in IRA_TYPES else False

    def get_ma_flag(self):
        return True if self.get_account_attributes().get('CMAFlag') == 'Y' else False

    def get_wash_sale_flag(self):
        return self.GetPortfolioTotals.get('WashSaleToggleFlag') == 1

    def get_streaming_restrictions_flag(self):
        value = streaming_to_account_type_map[self.current_acct.acctType]
        return {"accountStreaming": value}

    def get_mdv_flag(self):
        return True  # TODO: mdv flag handling

    def get_geo_domestic_flag(self):
        return False  # TODO: geo_domestic flag handling or delete if outdated
