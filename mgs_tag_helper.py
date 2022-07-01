"""References "accounts"(brokerage, bank, stockplan) tags are defined here"""
from dash_common.constants.mgs_mobile_gateway_constants import AccountsTags, ReferencePositionsTags, \
    ReferenceInstrumentsTags, TaxLotsTags, NewWatchlistsServices, BondPositionTags, AccountPositionTags


class AccountsTagSchema(object):
    """
    Services with accounts objects:
    accountList: brokerage, bank, stock plan accounts
    accountOverview: brokerage, bank accounts
    completeView: brokerage, bank, stock plan accounts
    allBrokerage: brokerage accounts
    IndividualBrokerage: brokerage accounts

    All of the "service - account type" combinations has their own special set of tags and values to show
    To handle complexity, following approach used:
    All references accounts tags can be  separated on 5 big categories:
    1. Description: same for all types of accounts, values are always returned (like "accountMode": "CASH",
        "acctDesc": "Individual Brokerage")
    2. Flags: bool value( like mdvFlag, funded, streamingRestrictions)
    3. Balances: various balance types (like "purchasingPower": "$7,623,136.83",
        "totalAvailableForWithdrawal": "$7,623,136.83")
    4. Change: various balance change types (like "daysGain": "$0.00", "daysGainPercent": "0.00%")
    5. Special: some specific values, everything else (like "restrictionLevel": "0", accountIndex": "0")

    self.values_returns_in is dict with keys "description", "balances", "change", "flags", "special" and bool value,
    True - actual response should have data for this category
    False - tags are present, but values are muted: will be "--" or "0"
    Basically, this attribute is only needed in s2-services values comparing, to know,
    if this type of account shows values for balances and/or balances changes,
    which helps  avoid excessive calls to s2-services.
    """

    def __init__(self, description, balances, change, flags, specific_to_service, values_returns_in):
        self.description = description
        self.balances = balances
        self.change = change
        self.flags = flags
        self.spec = specific_to_service or set()
        self.returns_values_for = values_returns_in

    def account_tags_set(self):
        tags = set()
        tags.update(self.description, self.flags, self.balances, self.change, self.spec)
        return tags

    def get_empty_account(self):
        tags = self.account_tags_set()
        return {}.fromkeys(tags, 0)

    def is_balance_need(self):
        return self.returns_values_for["balances"]

    def is_change_need(self):
        return self.returns_values_for["change"]


tag = AccountsTags
standard_account_description = {tag.account_uuid, tag.account_id, tag.account_mode, tag.account_desc,
                                tag.account_short_name, tag.account_long_name, tag.account_type, tag.inst_type}
common_account_description = {tag.account_uuid, tag.account_id,  # tag.account_mode,
                              # tag.account_desc,
                              tag.account_short_name, tag.account_long_name,  # tag.account_type,
                              tag.inst_type}
standard_account_balance = {tag.cash_available_for_withdrawal, tag.margin_available_for_withdrawal,
                            tag.purchasing_power, tag.total_available_for_withdrawal, tag.ledger_account_value,
                            tag.account_value}
standard_account_change = {tag.days_gain, tag.days_gain_percent, tag.total_gain, tag.total_gain_percent}


class AccountListAccountsTags(object):
    brokerage_account = AccountsTagSchema(
        description=standard_account_description,
        balances=standard_account_balance,
        change=standard_account_change,
        flags={
            tag.flag_washsaleflag,
            tag.flag_is_ira,
            tag.flag_mdvflag,
            tag.flag_funded,
            tag.flag_streaming,
            tag.flag_ma_flag,
            # tag.flag_domestic
        },
        specific_to_service={
            tag.option_level,
            tag.restriction_level,
            tag.enc_account_id
        },
        values_returns_in={"description": True,
                           "balances": False,
                           "change": False,
                           "flags": True,
                           "special": True})

    bank_account = AccountsTagSchema(
        description=standard_account_description,
        balances={},
        change={},
        flags={
            tag.flag_is_ira,
            tag.flag_mdvflag,
            tag.flag_streaming
        },
        specific_to_service={
            tag.enc_account_id
        },
        values_returns_in={"description": True, "balances": False, "change": False, "flags": True, "special": False})

    stock_plan_account = AccountsTagSchema(
        description=standard_account_description,
        balances={
            tag.account_value
        },
        change={
            tag.days_gain,
            tag.days_gain_percent
        },
        flags={
            tag.flag_is_ira,
            tag.flag_mdvflag,
            tag.flag_streaming,
            # tag.flag_domestic
        },
        specific_to_service={
            tag.account_index,
            tag.symbol,
            tag.enc_account_id
        },
        values_returns_in={"description": True,
                           "balances": False,
                           "change": False,
                           "flags": True,
                           "special": True})


class AccountOverviewAccountsTags(object):
    brokerage_account = AccountsTagSchema(
        description=standard_account_description,
        balances=standard_account_balance,
        change=standard_account_change,
        flags={
            tag.flag_is_ira,
            tag.flag_ma_flag,
            tag.flag_funded,
            tag.flag_streaming
        },
        specific_to_service={
            tag.restriction_level,
            tag.prompts_for_funding,
            tag.enc_account_id
        },
        values_returns_in={"description": True,
                           "balances": True,
                           "change": True,
                           "flags": True,
                           "special": True})

    bank_account = AccountsTagSchema(
        description=standard_account_description,
        balances={},
        change={},
        flags={
            tag.flag_is_ira,
            tag.flag_streaming
        },
        specific_to_service={
            tag.prompts_for_funding,
            tag.enc_account_id
        },
        values_returns_in={"description": True,
                           "balances": False,
                           "change": False,
                           "flags": True,
                           "special": False})


class CompleteViewAccountsTags(object):
    brokerage_account = AccountsTagSchema(
        description=standard_account_description,
        balances=standard_account_balance,
        change=standard_account_change,
        flags={
            tag.flag_is_ira,
            tag.flag_ma_flag,
            tag.flag_funded,
            tag.flag_streaming
        },
        specific_to_service={
            tag.restriction_level,
            tag.prompts_for_funding,
            tag.enc_account_id
        },
        values_returns_in={"description": True,
                           "balances": True,
                           "change": True,
                           "flags": True,
                           "special": True})

    bank_account = AccountsTagSchema(
        description=standard_account_description,
        balances={},
        change={},
        flags={
            tag.flag_is_ira,
            tag.flag_streaming
        },
        specific_to_service={
            tag.prompts_for_funding,
            tag.enc_account_id
        },
        values_returns_in={"description": True, "balances": False, "change": False, "flags": True, "special": False})

    stock_plan_account = AccountsTagSchema(
        description=standard_account_description,
        balances={
            tag.account_value
        },
        change={
            tag.days_gain,
            tag.days_gain_percent
        },
        flags={
            tag.flag_is_ira,
            tag.flag_streaming
        },
        specific_to_service={
            tag.account_index,
            tag.symbol,
            tag.prompts_for_funding,
            tag.enc_account_id
        },
        values_returns_in={"description": True, "balances": True, "change": True, "flags": True, "special": True})


class AllBrokerageAccountsTags(object):
    brokerage_account = AccountsTagSchema(
        description=standard_account_description,
        balances=standard_account_balance,
        change=standard_account_change,
        flags={
            tag.flag_ma_flag,
            tag.flag_funded,
            tag.flag_streaming
        },
        specific_to_service={
            tag.restriction_level,
            tag.prompts_for_funding,
            # tag.enc_account_id
        },
        values_returns_in={"description": True,
                           "balances": True,
                           "change": False,
                           "flags": True,
                           "special": True})


class IndividualAccountsTags(object):
    brokerage_account = AccountsTagSchema(
        description=standard_account_description,
        balances=standard_account_balance,
        change=standard_account_change,
        flags={
            tag.flag_is_ira,
            tag.flag_ma_flag,
            tag.flag_funded,
            tag.flag_streaming
        },
        specific_to_service={
            tag.restriction_level,
            tag.prompts_for_funding,
            tag.enc_account_id
        },
        values_returns_in={"description": True,
                           "balances": True,
                           "change": True,
                           "flags": True,
                           "special": True})


class ReferencesTags:
    """
    Easy access to all references instruments, positions, tax lots, watchlist entries variants
    Just keep constants updated correct
    """
    pos_tags = ReferencePositionsTags
    bond_tags = BondPositionTags
    acc_tag = AccountPositionTags
    inst_tag = ReferenceInstrumentsTags
    lot_tag = TaxLotsTags
    wl_tag = NewWatchlistsServices

    # 'positions'
    base_position: set = pos_tags.to_set()

    position: set = base_position.copy()
    position.update(acc_tag.to_set())

    position_bond: set = position.copy()
    position_bond.update(bond_tags.to_set())

    watchlist_position: set = base_position.copy()
    watchlist_position.update({wl_tag.watch_list_uuid, wl_tag.watch_list_id, wl_tag.entry_id})

    watchlist_position_bond: set = watchlist_position.copy()
    watchlist_position_bond.update(bond_tags.to_set())

    # 'instruments'
    base_instrument: set = inst_tag.to_set()
    account_instrument: set = base_instrument.copy()
    account_instrument.update({acc_tag.positionId})

    account_instrument_bond = account_instrument.copy()
    account_instrument_bond.update(bond_tags.to_set())

    watchlist_instrument = base_instrument.copy()
    watchlist_instrument.update({wl_tag.watch_list_id, wl_tag.entry_id})
    watchlist_instrument_bond: set = watchlist_instrument.copy()
    watchlist_instrument_bond.update(bond_tags.to_set())

    # 'tax lots'
    tax_lot: set = lot_tag.to_set()

    # "watchList_editEntry"
    watch_list_edit_entry = {wl_tag.watch_list_uuid, wl_tag.watch_list_id, wl_tag.watch_list_name, wl_tag.entries}

    # "entries" from "watchList_editEntry"
    edit_entry = {wl_tag.entry_id, wl_tag.new_index_id}

    # "watchList_list"
    watch_list_list = {wl_tag.watch_list_uuid, wl_tag.watch_list_id, wl_tag.watch_list_name}

    # "watchList_Delete"
    watchlist_delete = {wl_tag.watch_list_uuid, wl_tag.watch_list_id}

    # "watchList_Create"
    watchlist_create = {wl_tag.watch_list_name, wl_tag.watch_list_uuid, wl_tag.watch_list_id}

    # "addWatchListEntry"
    add_entry = {wl_tag.entry_id,
                 pos_tags.symbol,
                 pos_tags.commission,
                 pos_tags.todayCommissions,
                 pos_tags.fees,
                 pos_tags.quantity,
                 pos_tags.basisPrice,
                 pos_tags.baseSymbolPrice,
                 pos_tags.pricePaid,
                 pos_tags.todayPricePaid,
                 pos_tags.daysGainValue,
                 pos_tags.totalGainValue,
                 pos_tags.daysGainPercentage,
                 pos_tags.totalGainPercentage,
                 pos_tags.daysPurchase,
                 pos_tags.todaysClose,
                 pos_tags.lastTradeTime}
