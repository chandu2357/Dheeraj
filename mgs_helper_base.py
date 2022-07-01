import json
import logging
import re

import xmltodict
import requests
from dash_common.constants.mgs_mobile_gateway_constants import \
    FrequentlyUsedTags, MgsViews, ReferencesObjectTypes, \
    ValuesValidationConstants, MsUserPreferenceReferenceTags, \
    MsUserReferenceCtaTags, BaseTags, SmsessionTags, \
    ApigeeDataTags, MsCompleteViewAccountSectionTags, \
    MsCompleteViewReferenceTags, MsCompleteViewTags, NasdaqloginTags
from dash_core.core.common.dash_assert.dash_assert import Assert
from dash_core.core.common.decorators.decorators import log_assertion

from test_helpers.mgs_backend_service_helpers.backend_requests import \
    get_portfolio_info
from test_helpers.mgs_backend_service_helpers.portfolio_backend_data_helper \
    import \
    PortfolioBackendDataHelper
from test_helpers.mgs_service_helpers.mgs_base_services import \
    MGSRedesignService
from test_helpers.mgs_validation_helpers.comments import Comments
from test_helpers.mgs_validation_helpers.mgs_mapping_helpers import \
    PositionsInstrumentsMap, ReferencesAccountsMapping, \
    ReferencesTaxLotMap
from test_helpers.mgs_validation_helpers.mgs_tag_helper import ReferencesTags
from test_helpers.mgs_validation_helpers.references.values_formats import \
    handle_value_formatting
from test_helpers.mgs_validation_helpers.uuid_mixin import \
    decode_account_uuid, \
    UuidMixin
from test_helpers.utils import get_ids_message

Tag = FrequentlyUsedTags


class MGSHelperBase(MGSRedesignService, UuidMixin):
    service = None
    values_assertions_fail_list = []
    view_types = None
    reference_types = None
    expected_tags = None

    @log_assertion()
    def verify_assertions_fail_list(self):
        """
        Print out all Cached Assertion errors, collected during values and tags comparing
        Asserts collected errors count is 0
        Clears the fails list afterward
        """
        fails_count = len(self.values_assertions_fail_list)
        fail_msg = f"Test not passed with {fails_count} assertion fails:\n"
        for assertion_fail in self.values_assertions_fail_list:
            fail_msg += str(assertion_fail) + '\n'
        self.values_assertions_fail_list.clear()

        Assert.log_assert(fails_count == 0, fail_msg)

    def collect_assertions_fails(self, assertion_e, reference_msg=None):
        """

        """
        reference_msg = reference_msg or ""
        message = '\n' + reference_msg + '\n' + str(assertion_e)
        self.values_assertions_fail_list.append(message)

    def verify_response_tags(self):
        """ Child class is responsible for
        response tags validation trough calling this method"""
        logging.info('Checking response tags:')

        self.verify_views_references_objects_types()
        logging.info('\tChecking views objects tags.')
        self.verify_views_tags()
        logging.info('\tChecking references objects tags.')
        self.verify_references_tags()
        logging.info('Response tags check complete')

    def verify_views_tags(self):
        """
        Implemented in child class
        """
        pass

    def verify_references_tags(self):
        logging.info('\tChecking accounts tags.')
        self.verify_references_accounts_tags()
        logging.info('\tChecking positions tags.')
        self.verify_references_positions_tags()
        logging.info('\tChecking instruments tags.')
        self.verify_references_instruments_tags()
        logging.info('\tChecking tax lots tags.')
        self.verify_references_tax_lots_tags()

        self.special_tags_verifications()

    def special_values_verifications(self):
        pass

    def special_tags_verifications(self):
        pass

    def verify_response_values(self):
        """Child class is responsible for
         response values validation and comparing with s2
          trough calling this method"""
        self.verify_views_values()

    def verify_views_values(self):
        """
        Implemented in child class
        """
        pass

    @log_assertion()
    def verify_references_positions_tags(self):
        """
        Method is parsing positions references
          for positions  and bond_positions separately
        Expected tags for account_positions and account_positions_bond
        will be compared with actual positions
        """
        positions = [position for position in self.parse_response().references.positions if
                     not position.get('maturity')]
        bond_positions = self.parse_response().references.positions(
            typeCode="BOND")
        logging.info(f"\t\tPositions({len(positions)})..")
        Comments.add_comments(f"Validating Position tags")
        self.check_objects_tags(positions,
                                ReferencesTags.position,
                                ReferencesObjectTypes.POSITIONS)
        Comments.add_comments(f"Validating bond position tags")
        self.check_objects_tags(bond_positions,
                                ReferencesTags.position_bond,
                                ReferencesObjectTypes.POSITIONS)

    @log_assertion()
    def verify_references_instruments_tags(self):
        """
        Method is parsing instruments references
         for instruments  and bond_instruments separately
        Expected tags for account_instrument and
         account_instrument_bond will be compared
        with actual instruments
        """
        instruments = [instrument for instrument in self.parse_response().references.instruments if
                       not instrument.get('maturity')]
        instr_bonds = [instrument for instrument in self.parse_response().references.instruments if
                       instrument.get('maturity')]

        logging.info(f"\t\tInstruments({len(instruments)})..")
        Comments.add_comments(f"Validation instruments tags")
        self.check_objects_tags(
            instruments,
            ReferencesTags.account_instrument,
            ReferencesObjectTypes.INSTRUMENTS)
        Comments.add_comments(f"Validating instruments bond tags")
        self.check_objects_tags(instr_bonds,
                                ReferencesTags.account_instrument_bond,
                                ReferencesObjectTypes.INSTRUMENTS)

    @log_assertion()
    def verify_references_tax_lots_tags(self):
        """
        Method is parsing lots references  for position lots
        Expected tags for all the tax lots are the same
         ( ReferencesTags.tax_lot)
        """
        tax_lots = self.parse_response().references.taxlots
        logging.info(f"\t\tTax lots({len(tax_lots)})..")
        self.check_objects_tags(
            tax_lots,
            ReferencesTags.tax_lot,
            ReferencesObjectTypes.TAXLOTS)

    @log_assertion()
    def verify_references_accounts_tags(self):
        """
        Method is parsing accounts references
          for brokerage, bank(acctType="Bank")
        and stockplan(acctType="ESP") accounts.
        Expected tags set is the combination of
         account_type and mgs service that provide response
        This is handled by self.expected_tags,
         and AccountsTagSchema methods
        Actual and expected tags sets will go
          for comparings  in check_objects_tags methods
        """
        request_name = self.prepared_request.get_name()
        brokerage_accounts = self.get_brokerage_accounts()
        logging.info(f"\t\tBrokerage accounts({len(brokerage_accounts)})..")
        expected_tags = self.get_brokerage_expected_tags()
        Comments.add_comments(Comments.brokerage_account_comment)
        self.check_objects_tags(
            brokerage_accounts,
            expected_tags,
            request_name)

        bank_accounts = self.parse_response().references.accounts(
            acctType="Bank")
        logging.info(f"\t\tBank accounts({len(bank_accounts)})..")
        expected_tags = self.get_bank_expected_tags()
        Comments.add_comments(Comments.bank_account_comment)
        self.check_objects_tags(bank_accounts, expected_tags, request_name)

        stock_plan_accounts = self.parse_response().references.accounts(
            acctType="ESP")
        logging.info(f"\t\tStock Plan accounts({len(stock_plan_accounts)})..")
        expected_tags = self.get_stock_plan_expected_tags()
        Comments.add_comments(Comments.stock_plan_account_comment)
        self.check_objects_tags(
            stock_plan_accounts,
            expected_tags,
            request_name)

    def get_brokerage_expected_tags(self):
        if hasattr(self.expected_tags, 'brokerage_account'):
            return self.expected_tags.brokerage_account.account_tags_set()
        else:
            return {}

    def get_bank_expected_tags(self):
        if hasattr(self.expected_tags, 'bank_account'):
            return self.expected_tags.bank_account.account_tags_set()
        else:
            return {}

    def get_stock_plan_expected_tags(self):
        if hasattr(self.expected_tags, 'stock_plan_account'):
            return self.expected_tags.stock_plan_account.account_tags_set()
        else:
            return {}

    def get_brokerage_accounts(self):
        """
        filter brokerage account excluding brokerage
        accounts with linked stock plan
        This will ensure getting response from
        AccountETS_GetAllPortfolioTotals
        for collecting account's balance change
        :return: list
        """
        no_stock_plan_linked = []
        brokerage_accounts = self.parse_response().references.accounts(
            instType="ADP")
        for account in brokerage_accounts:
            if self.is_linked_stock_plan(account):
                continue
            no_stock_plan_linked.append(account)
        return no_stock_plan_linked

    def is_linked_stock_plan(self, account):
        """Identify linked brokerage accounts,
        that is having the same accountId as related ESP account"""
        account_id = account['accountId']
        if account['acctType'] == 'ESP':
            return False
        return len(self.parse_response().references.accounts(
            accountId=account_id)) > 1

    @log_assertion()
    def verify_references_accounts_values(self, tag=None,
                                          account_type='brokerage'):
        """
        Method is fetching references accounts list from self.received_response
        If self.received_response have accounts references,
        method will create mapping of mgs accounts keys to s2_values.
        and compare two sources with self.check_values(mgs_account,
        s2_account) method.
        Brokerage accounts linked to stockplan will be skipped!
        """
        account_type.capitalize()
        logging.info(f'Checking {account_type}-accounts values..')
        mapping = ReferencesAccountsMapping(self._uid)
        accounts = self.parse_response().references.accounts(
            acctType=account_type)

        for account in accounts:
            uuid = account['accountUuid']
            mgs_account_id = account['accountId']
            if mgs_account_id == "83851862":
                # MGS-3140: this is some strange ESP account
                # that don't have linked brokerage to it
                continue
            if self.is_linked_stock_plan(account):
                continue

            s2_account = mapping.get_account(uuid, self.prepared_request)
            if tag:
                mgs_data = account[f'{tag}']
                s2_data = s2_account[f'{tag}']
                self.compare_equals(mgs_data, s2_data)
                logging.info(f'Complete verification of TAG::'
                             f' {tag} on Total Accounts({len(accounts)}) ')
            else:
                self.check_values(mgs_data=account, s2_data=s2_account)

    @log_assertion()
    def verify_references_tax_lots_values(self, mgs_lots=None):
        """
        If no mgs_lots provided, will try to fetch
        lots from self.received_response
        Method Makes call to AccountETS_GetPortfolioInfo
        with current user_id ,account_id, and position_id params.
        For lot in  mgs 'lots':
            Create mapping (by position_id) of mgs keys to s2 values
            Call check_values(mgs_lot, s2_lot) method
        :param mgs_lots: dict
        :return: None
        """
        logging.info('Checking tax lots values..')
        s2_lot_list = {}
        lots = mgs_lots or self.parse_response().references.taxlots
        if lots:
            account_id = self.get_account_id_from_uuid(
                self.prepared_request.accountUuid)
            position_id = self.prepared_request.positionId
            user_id = self._uid
            s2_lot_list = PortfolioBackendDataHelper().get_lots_data(
                account_id, user_id, position_id)

        for lot in lots:
            lot_id = lot['positionLotId']
            mapping = ReferencesTaxLotMap(s2_lot_list, lot_id)
            s2_lot = mapping.get_tax_lot()
            self.check_values(lot, s2_lot)
        logging.info(f'Tax Lots({len(lots)}) values verifying complete')

    @log_assertion()
    def verify_references_positions_values(self,
                                           mgs_positions=None,
                                           s2_data=None):
        """
        If no mgs_positions provided,
        will try to fetch positions from self.received_response
        If no s2_data provided,
        Method Makes call to AccountETS_GetPortfolioInfo
        with current user_id and account_id params.
        For position in  mgs 'positions':
            Create mapping (by position_id) of mgs keys to s2 values
            Call check_values(mgs_position, s2_position) method
        :param s2_data: dict
        :param mgs_positions: dict
        :param s2_data: dict
        :return: None
        """
        logging.info('Checking positions values..')
        positions = mgs_positions or self.parse_response().references.positions

        if positions and not s2_data:
            user_id = self._uid
            account_id = positions[0]['accountId']
            s2_data = get_portfolio_info(account_id, user_id)

        for position in positions:
            position_id = position['positionId']

            mapping = PositionsInstrumentsMap(s2_data, position_id)
            s2_position = mapping.get_position()

            self.check_values(position, s2_position)
        logging.info(f'Positions({len(positions)}) values verifying ends here')

    @log_assertion()
    def verify_references_instruments_values(self,
                                             mgs_instruments=None,
                                             s2_data=None,
                                             account_id=None):
        """
        If no mgs_instruments provided,
        will try to fetch instruments from self.received_response
        If no s2_data provided,
        Method Makes call to AccountETS_GetPortfolioInfo
        with current user_id and account_id params.
        For instrument in  mgs 'instruments':
            Create mapping (by position_id) of mgs keys to s2 values
            Call check_values(mgs_instrument, s2_instrument) method
        :param mgs_instruments: dict
        :param account_id: str
        :param s2_data: dict
        :return: None
        """
        logging.info('Checking instruments values..')
        curr_instruments = self.parse_response().references.instruments
        instruments = mgs_instruments or curr_instruments

        if instruments and not s2_data:
            user_id = self._uid
            account_id = account_id or self.get_account_id_from_uuid(
                self.prepared_request.accountUuid)
            s2_data = get_portfolio_info(account_id, user_id)

        for instrument in instruments:
            position_id = instrument['positionId']

            mapping = PositionsInstrumentsMap(s2_data, position_id)
            s2_instrument = mapping.get_instrument()

            self.check_values(mgs_data=instrument, s2_data=s2_instrument)
        logging.info(f'Instruments({len(instruments)}) '
                     f'values verifying ends here')

    @log_assertion()
    def verify_views_account_summary_tags(self, expected_tags=None):
        """
        Generalized approach to views account_summary tags verification
        Due to vary account_summary tags spec across responses,
        parameter expected_tags added
        Verify all account_summaries tags, additional_labels tags,
        streamable_values tags
        :param expected_tags: set
        :return: None
        """
        account_summary = self.parse_response().views.account_summary
        _summary = MgsViews.accounts_account_summary
        summary_expected_tags = expected_tags or _summary
        for summary in account_summary:
            self.check_tags(summary, summary_expected_tags)
            additional_labels = summary['account_additional_labels']

            for additional_label in additional_labels:

                labels_expected_tags = MgsViews.additional_labels
                if additional_label["account_additional_label_title"] == 'Cash':
                    cash_expected_tags = labels_expected_tags.copy()
                    cash_expected_tags.discard("account_additional_label_value_detail")
                    self.check_tags(additional_label, cash_expected_tags)
                else:
                    self.check_tags(additional_label, labels_expected_tags)

                streamable_values: dict = additional_label['account_additional_label_streamable_value']
                for streamable_value in streamable_values:
                    Comments.add_comments(Comments.streamable_value_comment.format(streamable_value))
                    Assert.log_assert(streamable_value in MgsViews.streamable_value)

    def verify_views_account_summary_values(self):
        """
        Verify values in views account summary match values in reference accounts
        # TODO: check mapping correct
        :return: None
        """
        account_summary = self.parse_response().views.account_summary()[0]
        account = self.parse_response().references.accounts[0]

        days_gain, total_gain, cash = account_summary['account_additional_labels']

        days_gain_initial_value = days_gain['account_additional_label_streamable_value']["initial"]
        Assert.log_assert(days_gain_initial_value == f"{account['daysGain']} ({account['daysGainPercent']})")

        total_gain_initial_value = total_gain['account_additional_label_streamable_value']["initial"]
        Assert.log_assert(total_gain_initial_value == f"{account['totalGain']} ({account['totalGainPercent']})")

        cash_initial_value = cash['account_additional_label_streamable_value']["initial"]
        Assert.log_assert(cash_initial_value == account['ledgerAccountValue'])

    @staticmethod
    def extract_dollar_to_num(value):
        """To convert dollar into float value"""
        val = re.findall(r"(-?\$[\d.,]+)", value)
        if val:
            return float("".join(val[0].replace("$", "").split(",")))
        logging.debug(value)
        return None

    @log_assertion()
    def check_objects_tags(self, obj_list, tags_set, obj_name):
        """
        Tags verification pattern extracted to method
        :param obj_list: list of dicts
        :param tags_set: set of expected tags
        :param obj_name: str
        :return: None
        """
        for _object in obj_list:
            self.check_tags(_object, tags_set, obj_name)

    @log_assertion()
    def check_tags(self, object_to_check: dict, expected_tags: set, message=''):
        """
        Fetch and compare tags sets from two dict-like objects
        Asserts actual_tags >= expected_tags
        """
        actual_tags = set(object_to_check.keys())
        ids = get_ids_message(object_to_check)
        missing_tags = expected_tags - actual_tags
        extra_tags = actual_tags - expected_tags
        message = f"{message}: Missing tags:{missing_tags}, " \
                  f"extra tags: {extra_tags}\n" \
                  f"Ids of object: {ids} "
        Comments.add_comments(Comments.check_tags_comment.format(actual_tags))
        Assert.log_assert(actual_tags >= expected_tags, message)

    @log_assertion()
    def verify_account_uuid_values(self):
        """
        Account uuid encoded values verification across
        references accounts and positions objects
        :return: None
        """
        # Try to validate with any other s2 service.
        for account in self.parse_response().references.accounts:
            uuid_values = decode_account_uuid(account["accountUuid"])
            Assert.log_assert(uuid_values["accountId"] == account["accountId"],
                              "accountId tag is wrong in accounts")

            Assert.log_assert(uuid_values["acctType"] == account["acctType"],
                              "acctType tag is wrong in accounts")

            Assert.log_assert(uuid_values["instType"] == account["instType"],
                              "instType tag is wrong in accounts")

        for position in self.parse_response().references.positions:
            uuid_values = decode_account_uuid(position["accountUuid"])
            Assert.log_assert(uuid_values["accountId"] == position["accountId"],
                              "accountId tag is wrong in positions")

    @log_assertion()
    def verify_views_references_objects_types(self):
        """
        Verify actual response have expected objects(types)
        in views and references
        :return: None
        """

        views = self.received_response["mobile_response"]["views"]
        references = self.received_response["mobile_response"]["references"]

        logging.info('\tChecking response views object types:')
        for type_value in self.view_types:
            logging.info(f'\tType: {type_value}')
            Comments.add_comments(
                Comments.verify_views_objects_types_comment.format(type_value))
            Assert.log_assert(
                any(obj.get('type') == type_value for obj in views))

        logging.info('\tChecking response references object types:')
        for type_value in self.reference_types:
            logging.info(f'\tType: {type_value}')
            Comments.add_comments(
                Comments.verify_refrences_objects_types_comment.format(
                    type_value))
            Assert.log_assert(
                any(obj.get('type') == type_value for obj in references))

    @log_assertion()
    def a_to_b_dict_comparing(self, a_dict: dict, b_dict: dict, to_skip=''):
        """
        Abstract method for two dicts values comparing,
        will iterate by a_dict keys,
        No tolerance to values divergence applied.
        :param a_dict: dict to iterate by keys
        :param b_dict: dict to compare values
        :param to_skip: this tags will be skipped
        :return:None
        """
        for a_key in a_dict.keys():
            if a_key in to_skip:
                logging.warning(f'Key "{a_key}" checking is skipped!')
                continue
            try:
                a_value = a_dict[a_key]
                b_value = b_dict[a_key]

                ids = get_ids_message(b_dict)
                msg = f'expected: {a_value}, actual: {b_value}, key:{a_key}, ' + ids

                Assert.log_assert(a_value == b_value, msg)
                Comments.add_comments(f'validated tags {a_key}: {b_value}')
            except KeyError:
                Assert.log_assert(a_key in b_dict, f"No expected key {a_key} found in {b_dict}!")
                Comments.add_comments(f'validated key: {a_key}')

            except AssertionError as assertion_error:
                self.collect_assertions_fails(assertion_error)

    def compare_view_to_reference_values(self, views_obj, reference_obj, to_skip=''):
        """
        Method for comparing view object with relater reference
        Will iterate by view.keys() asserting view and reference values is the same(==)
        Keys in to_skip are to skip keys
        :param views_obj:
        :param reference_obj:
        :param to_skip:
        :return:
        """
        self.a_to_b_dict_comparing(views_obj, reference_obj, to_skip)

    @log_assertion()
    def check_values(self, mgs_data, s2_data):
        """
        Iterating by s2_data.keys(), so not covered values will be skipped.
        If value represents float number(Money, Percentage):
         - compare values with compare_floats method
        If value represents not a float number (Name,  Id, Bool, None):
         - compare values with compare_equals method
         All not passed assertions will be collected and raised
        :param mgs_data: dict
        :param s2_data: dict
        :return: None
        """

        ids = get_ids_message(mgs_data)
        not_defined = set(mgs_data.keys()) - set(s2_data.keys())
        logging.debug(ids + f'Skipping not defined keys:{not_defined}')

        for key in s2_data.keys():  # iteration will be done by s2 keys

            mgs_value = mgs_data[key]
            temp_mgs_value = handle_value_formatting(mgs_value)

            s2_value = s2_data[key]
            temp_s2_value = handle_value_formatting(s2_value)

            Comments.add_comments(
                f"validating key: {key} with mgs value: {temp_mgs_value} and s2 value: {temp_s2_value}")
            try:
                if isinstance(temp_s2_value, float) or isinstance(temp_mgs_value, float):
                    self.compare_floats(temp_mgs_value, temp_s2_value)
                else:
                    self.compare_equals(temp_mgs_value, temp_s2_value)

            except AssertionError as assertion_error:
                ref = '\n' + ids + f'Key: "{key}", MGS value: "{mgs_value}", S2 value: "{s2_value}";'
                self.collect_assertions_fails(assertion_error, ref)

    @staticmethod
    @log_assertion()
    def compare_equals(prepared_value, s2_value):
        """
        Method to ensure that two values are the same
        If one of the values is None, asserts that second is also None
        If value is None, bool, str, int, dict - asserts a_val == b_val
        """
        failed_msg = f'Comparing prepared values:' \
                     f' mgs: "{prepared_value}"({type(prepared_value)}),' \
                     f' s2: "{s2_value}"({type(s2_value)}) '
        prepared_value = handle_value_formatting(prepared_value)
        s2_value = handle_value_formatting(s2_value)

        if prepared_value is None or s2_value is None:
            Assert.log_assert(s2_value is None, failed_msg)
            Assert.log_assert(prepared_value is None, failed_msg)
        if prepared_value == 'EAS':  # MGS-2982
            Assert.log_assert(s2_value == "Brokerage", failed_msg)
        else:
            Assert.log_assert(prepared_value == s2_value, failed_msg)

    @staticmethod
    @log_assertion()
    def compare_floats(prepared_mgs_value, s2_value):
        """
        Compare float values with tolerance applied
        If nor a_val== 0,0, nor b_val == 0,0:
            Assert ((abs(prepared_mgs_value - s2_value))/s2_value) <= tolerance

        If a_val == 0,0 or b_val == 0,0:
            Assert abs(prepared_mgs_value - s2_value) <= tolerance
        """
        tolerance = ValuesValidationConstants.TOLERANCE
        s2_value = float(s2_value)
        prepared_mgs_value = float(prepared_mgs_value)
        diff = abs(prepared_mgs_value - s2_value)
        if s2_value != 0 and prepared_mgs_value != 0:
            relative_error = diff / s2_value
        else:
            relative_error = diff

        failed_assert_msg = f'Diff: {diff}({prepared_mgs_value} - {s2_value}),' \
                            f' relative_error: {relative_error}, tolerance: {tolerance};'
        Assert.log_assert((relative_error <= tolerance), failed_assert_msg)

    def get_portfolio_backend_data(self, account_id) -> dict:
        """
        Method makes GetPortfolioInfo request to  AccountETS service
        Update response dict with nested objects BasicQuote, DetailedQuote, Fundamentals, etc. to simplify validations
        :param account_id: str
        :return: dict
        """
        user_id = self._uid
        s2_helper = PortfolioBackendDataHelper()
        s2_position_list = s2_helper.get_portfolio_data(acc_id=account_id, user_id=user_id)

        return s2_position_list

    def verify_stockplan_days_gain(self, mapping, account):
        account_no = account['accountId']
        if account['acctType'] == 'ESP':
            days_gain = account['daysGain']
            logging.info(f"{account}")
            employee_ids = mapping.accounts_descriptions[f'{account_no}']['CSGAccountInfo']['CSGRecordDetails']
            days_gain = handle_value_formatting(days_gain)
            days_gain = handle_value_formatting(days_gain)
            for employee in employee_ids:
                employee_id = employee['OlEmpId']
                s2_account = mapping.get_balance_for_stock_plan(employee_id)
                s2_days_gain = s2_account['daysGain']
                mgs = f"day's Gain s2 service:  {s2_days_gain} is  not matching with Mgs day's gain: {days_gain}"
                Assert.log_assert(days_gain == s2_days_gain, mgs)

    @staticmethod
    def from_dollar_to_float(dollar_value: str):
        _dollar_value = dollar_value
        for char in ValuesValidationConstants.VALUES_FORMATS_CHARS:
            _dollar_value = _dollar_value.replace(char, "")
        try:
            float_value = float(_dollar_value)
        except ValueError:
            logging.error(f'Dollar value "{dollar_value}" -  failed conversion to float')
            raise
        return float_value

    def verify_accoutlist_displaynotification_views_tags(self, account_list_response):
        account_list = account_list_response['mobile_response']['views']
        type_status = False
        for account in account_list:
            if "personal_notifications_list" == account["type"]:
                type_status = True
                if "external_account_verification" not in account["data"]:
                    assert False, "external_account_verification tag not present"
                if "pending_transactions" not in account["data"]:
                    assert False, "pending_transactions tag not present"

        assert type_status, "personal_notifications_list tag not present"

    def verify_accoutlist_displaynotification_pending_transactions(self, account_list_response, funding_response):
        account_list = account_list_response['mobile_response']['views']
        for account in account_list:
            if "personal_notifications_list" == account["type"]:
                pending_transactions = account["data"]["pending_transactions"]
                for pending_transaction in pending_transactions:
                    account_uuid = pending_transaction["accountUuid"]
                    Comments.add_comments("Validating pending transactions for account uuid: %s" % account_uuid)
                    transactions = pending_transactions["transactions"]
                    for transaction in transactions:
                        accout_list_fundAvailabilityDate = transaction["fundAvailabilityDate"]
                        account_list_fromAcctNumber = transaction["fromAcctNumber"]
                        account_list_amount = transaction["amount"]
                        account_list_activity_id = transaction["activityId"]
                        self.validate_accountlist_pending_transactions(funding_response, account_list_activity_id,
                                                                       account_list_fromAcctNumber, account_list_amount,
                                                                       accout_list_fundAvailabilityDate)

    def verify_fundavailability_date(self, account_list_response, funding_response):
        account_list = account_list_response['mobile_response']['references'][0]['data']
        for accountlist in account_list:
            if "transferActivity" not in accountlist:
                continue
            fund_activities = accountlist["transferActivity"]
            for fund_activity in fund_activities:
                fund_availability_date = fund_activity["fundAvailabilityDate"]
                from_acc_number = fund_activity["fromAcctNumber"]
                amount = fund_activity["amount"]
                trasnfer_activity_id = fund_activity['activityId']
                self.validate_accountlist_pending_transactions(funding_response, trasnfer_activity_id, from_acc_number,
                                                               amount, fund_availability_date)

    def validate_accountlist_pending_transactions(self, funding_response, activity_id, account_number,
                                                  amount, fund_availability_date):
        fundingcard_activites = funding_response['activityList']
        for fundingcard_activity in fundingcard_activites:
            fundingcard_activity_id = fundingcard_activity['activityId']
            if activity_id == fundingcard_activity_id:
                Comments.add_comments('validating transfer activityId: %s with mm-funding card activityId: %s'
                                      % (activity_id, fundingcard_activity_id))
                mm_fund_availability_date = fundingcard_activity['fundAvailabilityDate']
                from_acc = fundingcard_activity['fromAcctNumber']
                fund_amount = fundingcard_activity['amount']
                Comments.add_comments(
                    'Validating fundAvailabilityDate: %s with mm-funding fundAvailabilityDate: %s' % (
                        fund_availability_date, mm_fund_availability_date))
                assert fund_availability_date == mm_fund_availability_date
                Comments.add_comments('validating fromAcctNumber: %s with mm-funding card fromAcctNumber: %s'
                                      % (from_acc, account_number))
                assert from_acc == account_number
                Comments.add_comments('validating amount: %s with mm-funding card amount: %s' % (
                    amount, fund_amount))
                assert amount == fund_amount

    def get_individual_brokerage_account_id(self, response):
        references = response['mobile_response']['references']
        for reference in references:
            if "accounts" == reference['type']:
                account_id = reference['data'][0]['accountId']
                return account_id

    def get_saved_and_open_orders_count(self, response):
        open_orders = ''
        saved_orders = ''
        views = response['mobile_response']['views']
        for view in views:
            if "account_summary" == view['type']:
                ctas = view['cta']
                for cta in ctas:
                    if "Open Orders" in cta['cta_label']:
                        open_orders = cta['cta_label']
                    if "Saved Orders" in cta['cta_label']:
                        saved_orders = cta['cta_label']

        return open_orders, saved_orders

    def validate_saved_orders_count(self, account_id, userid, saved_orders):
        s2_saved_orders_response = self.get_saved_orders_request(account_id, userid)
        s2_saved_orders_response_dict = json.loads(
            json.dumps(xmltodict.parse(s2_saved_orders_response.text))
        )
        saved_prep_order_count = s2_saved_orders_response_dict[
            'OrderETS_ViewOrderPreparedResponse']['PreparedResponse']['PrepOrderCount']
        Comments.add_comments("Validating saved order: %s with s2 call: %s" % (saved_orders, saved_prep_order_count))
        Assert.log_assert(
            saved_prep_order_count in saved_orders, "Saved order count didn't match with s2 call"
        )

    def validate_open_order_count(self, account_id, user_id, open_orders):
        s2_open_orders_count_response = self.get_open_orders_request(account_id, user_id)
        s2_saved_orders_response_dict = json.loads(
            json.dumps(xmltodict.parse(s2_open_orders_count_response.text))
        )
        open_prep_order_count = s2_saved_orders_response_dict[
            'OrderETS_GetOpenOrderCountResponse']['Response']['TotalOrderCount']
        Comments.add_comments('Validating open oder count: %s with s2 call: %s' % (open_orders, open_prep_order_count))
        Assert.log_assert(
            open_prep_order_count in open_orders, "Open order count didn't match with s2 call"
        )

    def verify_individual_brokerage_order_count_response(self, userid, response):
        open_orders, saved_orders = self.get_saved_and_open_orders_count(response)
        if open_orders or saved_orders:
            account_id = self.get_individual_brokerage_account_id(response)
            if saved_orders:
                self.validate_saved_orders_count(account_id, userid, saved_orders)
            if open_orders:
                self.validate_open_order_count(account_id, userid, open_orders)

    def verify_portfolio_new_experience_tags(self):
        """Verifying portfolio 2.0 changes"""
        views = self.received_response["mobile_response"]["views"]
        references = self.received_response["mobile_response"]["references"]
        for view in views:
            view_type = view["type"]
            if view_type == "account_summary":
                account_label = view["data"]["account_detail_label"]
                Assert.log_assert(account_label == "Net Account Value", "Net Account Value not found")
                Comments.add_comments("Net Account Value validated successfully")
                self.verify_cta_lables(view)
                self.verify_account_extra_details(view)

        for reference in references:
            if "instruments" == reference["type"]:
                for data in reference["data"]:
                    Assert.log_assert("symbolDescription" in data, "symbolDescription not found")
                    Comments.add_comments("symbolDescription tag validated successfully")

    def verify_account_extra_details(self, view):
        """Verifying portfolio 2.0 changes"""
        account_extra_details_list = []
        account_extra_details = view["data"]["account_extra_details"]
        for account_details in account_extra_details:
            account_extra_details_list.append(account_details["account_additional_label_title"])

        Assert.log_assert("Cash" in account_extra_details_list, "Cash not found")
        Comments.add_comments("Cash value validated successfully")

    def verify_cta_lables(self, view):
        """Verifying portfolio 2.0 changes"""
        cta_labels = view["cta"]
        cta_labels_list = []
        for cta_label in cta_labels:
            cta_labels_list.append(cta_label["cta_label"])
        Assert.log_assert("Performance & Value" in cta_labels_list, "Performance & Value not found")
        Comments.add_comments("Performance & Value validated successfully")
        Assert.log_assert("News" in cta_labels_list, "News not found")
        Comments.add_comments("News validated successfully")
        Assert.log_assert("Dividend Re-Investment (DRIP)" in cta_labels_list,
                          "Dividend Re-Investment (DRIP) not found")
        Comments.add_comments("Dividend Re-Investment (DRIP) validated successfully")

    def get_dual_user_value(self, account_type):
        return True if "ms-et" in account_type.lower() else False

    def get_ms_user_response(self):
        """MS User Preference Data """
        received_response = self.received_response
        ms_user_data = {}
        try:
            response = received_response["mobile_response"]["references"][1]
            Assert.log_assert(response['type'] == "user_preferences", "User preferences not found.")
            data = response['data'][0]
            Assert.log_assert("ms_user_preferences" in data.keys(), "Ms User preferences not found.")
            ms_user_data = data['ms_user_preferences']

        except IndexError:
            self.verify_references_accounts_tags()

        except KeyError as e:
            logging.error(f'Service Error Returned instead of "{e}"-key ')

        except Exception as e:
            logging.error(f'The Exception Returned is "{e}"')

        return ms_user_data

    def verify_accountlist_dualaccountvisibility_references_tags(self, ms_user_data):
        """Validation of Dual Account visibility Reference Tags"""
        Assert.log_assert(MsUserPreferenceReferenceTags.login_uuid in ms_user_data.keys(),
                          "{0} not found.".format(MsUserPreferenceReferenceTags.login_uuid))
        Assert.log_assert(MsUserPreferenceReferenceTags.isMSfeatureEnabled in ms_user_data.keys(),
                          "{0} not found.".format(MsUserPreferenceReferenceTags.isMSfeatureEnabled))
        Assert.log_assert(MsUserPreferenceReferenceTags.isDualUser in ms_user_data.keys(),
                          "{0} not found.".format(MsUserPreferenceReferenceTags.isDualUser))
        Assert.log_assert(MsUserPreferenceReferenceTags.isFAVisibilityEnabled in ms_user_data.keys(),
                          "{0} not found.".format(MsUserPreferenceReferenceTags.isFAVisibilityEnabled))
        Assert.log_assert(MsUserPreferenceReferenceTags.msAccountVizPilotUser in ms_user_data.keys(),
                          "{0}not found.".format(MsUserPreferenceReferenceTags.msAccountVizPilotUser))
        Assert.log_assert(BaseTags.cta in ms_user_data.keys(),
                          "{0} not found.".format(BaseTags.cta))

    def verify_accountlist_dualaccountvisibility_references_tag_values(self, ms_user_data, dual_user):
        """ Validation of Dual Account Visibility Reference Values """
        Assert.log_assert(ms_user_data[MsUserPreferenceReferenceTags.isDualUser] == dual_user,
                          "{0} flag value not expected.".
                          format(MsUserPreferenceReferenceTags.isDualUser))
        Assert.log_assert(ms_user_data[MsUserPreferenceReferenceTags.isUserPilot] == dual_user,
                          "{0} flag value not expected.".
                          format(MsUserPreferenceReferenceTags.isUserPilot))
        Assert.log_assert(ms_user_data[MsUserPreferenceReferenceTags.isMSfeatureEnabled] is True,
                          "{0} flag value not expected.".
                          format(MsUserPreferenceReferenceTags.isMSfeatureEnabled))
        Assert.log_assert(ms_user_data[MsUserPreferenceReferenceTags.msAccountVizPilotUser] == dual_user,
                          "{0}flag value not expected.".
                          format(MsUserPreferenceReferenceTags.msAccountVizPilotUser))

    def verify_accountlist_dualaccountvisibility_references_cta_values(self, ms_user_data):
        """Validation of Dual Account Visibility CTA Values"""
        cta_values = ms_user_data.get('cta', [])
        for cta in cta_values:
            Assert.log_assert(cta[MsUserReferenceCtaTags.cta_label] in MsUserReferenceCtaTags.cta_label_default_values,
                              "cta labels doesn't have expected values.")
            Assert.log_assert(cta[MsUserReferenceCtaTags.cta_title] in MsUserReferenceCtaTags.cta_title_default_values,
                              "cta title doesn't have expected values")
            Assert.log_assert(cta[MsUserReferenceCtaTags.cta_action]['webview_url'] in
                              MsUserReferenceCtaTags.cta_action_webview_values,
                              "cta action key WebView url doesn't have expected values")

    def verify_ms_completeview_account_section_tags(self, view_response):
        """validating mscompleteview account_section tags"""
        for index, value in enumerate(view_response):
            Assert.log_assert(MsCompleteViewAccountSectionTags.account_uuid in value.keys(),
                              "account_uuid key not found in account_sections response, the index num is {}"
                              .format(index))
            Assert.log_assert("account_label" in value.keys(),
                              "account_label key not found in account_sections response, the index num is {}"
                              .format(index))
            Assert.log_assert("account_footnotes" in value.keys(),
                              "account_footnotes key not found in account_sections response, the index num is {}"
                              .format(index))
            Assert.log_assert("account_additional_labels" in value.keys(),
                              "account_additional_labels key not found in account_sections response, "
                              "the index num is {}".format(index))

    def verify_ms_completeview_reference_tags(self, reference_response):
        """validating mscompleteview reference tags"""
        for index, value in enumerate(reference_response):
            Assert.log_assert(FrequentlyUsedTags.TYPE in value.keys(),
                              "type key not found in references response, the index num is {}".format(
                                  index))
            Assert.log_assert(FrequentlyUsedTags.DATA in value.keys(),
                              "data key not found in references response, the index num is {}".format(
                                  index))
        for index, value in enumerate(reference_response[0]['data']):
            Assert.log_assert(MsCompleteViewReferenceTags.accountUuid in value.keys(),
                              "accountUuid key not found in references[0] data response, the index num is {}".format(
                                  index))
            Assert.log_assert(MsCompleteViewReferenceTags.accountType in value.keys(),
                              "accountType key not found in references[0] data response, the index num is {}".format(
                                  index))
            Assert.log_assert(MsCompleteViewReferenceTags.keyAccountId in value.keys(),
                              "keyAccountId key not found in references[0] data response, the index num is {}".format(
                                  index))
            Assert.log_assert(MsCompleteViewReferenceTags.platform in value.keys(),
                              "platform key not found in references[0] data response, the index num is {}".format(
                                  index))
            Assert.log_assert(MsCompleteViewReferenceTags.pledgeIndicator in value.keys(),
                              "pledgeIndicator key not found in references[0] data response, the index num is {}"
                              .format(index))
            Assert.log_assert(MsCompleteViewReferenceTags.accountDisplayName in value.keys(),
                              "accountDisplayName key not found in references[0] data response, the index num is {}"
                              .format(index))
            Assert.log_assert(MsCompleteViewReferenceTags.accountDisplayName in value.keys(),
                              "accountDisplayNumber key not found in references[0] data response, the index num is {}"
                              .format(index))
            Assert.log_assert(MsCompleteViewReferenceTags.instType in value.keys(),
                              "instType key not found in references[0] data response, the index num is {}"
                              .format(index))
            Assert.log_assert(MsCompleteViewReferenceTags.balanceType in value.keys(),
                              "balanceType key not found in references[0] data response, the index num is {}"
                              .format(index))
        Assert.log_assert(MsCompleteViewReferenceTags.ms_user_preferences in reference_response[1]['data'][0].keys(),
                          "ms_user_preferences is not found in reference response.")
        Assert.log_assert(MsCompleteViewReferenceTags.isEnrolledForDualAcctVisibility
                          in reference_response[1]['data'][0]['ms_user_preferences'],
                          "isEnrolledForDualAcctVisibility is not found in ms_user_preferences dict.")

    def verify_ms_completeview_tags(self, views_data_enabled):
        """validating mscompleteview view tags"""
        if not views_data_enabled:
            logging.info('There is no mobile_response views data.')
            return
        response = self.received_response
        view_response = response['mobile_response']['views'][0]
        Assert.log_assert(FrequentlyUsedTags.TYPE in view_response.keys(), "type key not found in view response.")
        Assert.log_assert(FrequentlyUsedTags.DATA in view_response.keys(), "type key not found in view response.")
        Assert.log_assert(MsCompleteViewTags.account_uuids in view_response['data'].keys(),
                          " account_uuid type key not found in view response.")
        Assert.log_assert(MsCompleteViewTags.account_summary_label in view_response['data'].keys(),
                          "account_summary_label key not found in view response.")
        Assert.log_assert(MsCompleteViewTags.account_additional_labels in view_response['data'].keys(),
                          "account_additional_labels key not found in view response.")
        Assert.log_assert(MsCompleteViewTags.account_sections in view_response['data'].keys(),
                          "account_sections key not found in view response.")

        # verifying account_sections list of values
        self.verify_ms_completeview_account_section_tags(view_response['data']['account_sections'])
        reference_response = response['mobile_response']['references']
        self.verify_ms_completeview_reference_tags(reference_response)

    def verify_ms_completeview_response(self, views_data_enabled, apige_data):
        """Validating MsCompleteview Total Assets and Total Liabilities"""
        if not views_data_enabled:
            logging.info('There is no mobile_response views data.')
            return
        response = self.received_response
        view_response = response['mobile_response']['views'][0]
        Assert.log_assert(view_response['type'].strip() == "ms_accounts_summary",
                          "view_response type value is not matched.")
        Assert.log_assert(view_response['data']['account_summary_label'].strip() == "Morgan Stanley Accounts", "")
        Assert.log_assert(view_response['data']['account_additional_labels'][0]
                          ['account_additional_label_title'].strip() == "Total Assets", "")
        view_res_total_asset_val = view_response['data']['account_additional_labels']
        total_assets = self.convert_to_float(view_res_total_asset_val[0]
                                             ['account_additional_label_streamable_value']['initial'])
        if total_assets > 0:
            apige_data_total_asset_val = apige_data['totalBalance'][0]['assetBalance']
            Assert.log_assert(abs(total_assets - apige_data_total_asset_val) <= 1,
                              "total bal was not matched, view_data: {0} and apgie_data: {1}"
                              .format(total_assets, apige_data_total_asset_val))
        Assert.log_assert(view_response['data']['account_additional_labels'][1]
                          ['account_additional_label_title'].strip() == "Total Liabilities", "")
        total_liabilites = self.convert_to_float(view_res_total_asset_val[1]
                                                 ['account_additional_label_streamable_value']['initial'])
        if total_liabilites > 0:
            apige_data_total_liability_val = apige_data['totalBalance'][0]['liabilityBalance']
            Assert.log_assert(abs(total_liabilites - apige_data_total_liability_val) <= 1,
                              "total bal was not matched, view_data: {0} and apgie_data: {1}".format(
                                  total_liabilites, apige_data_total_liability_val))

    def convert_to_float(self, val):
        """float conversion"""
        try:
            val = float(val.replace('$', '').replace(',', '').strip())
        except ValueError:
            print(val)
            val = 0
        return val

    def validate_account_balances(self, apige_value, account_value):
        """
        :param apige_value: dict of msaccount balance
        :param account_value: dict of ms complete view balance
        :return:
        We are validating the apigee ms balance with mscompleteview balances.
        """
        balance_type = apige_value['balanceType']
        if balance_type == "Investment" and apige_value['hasSecurityHoldings']:
            apige_bal = apige_value['investment']['accountValue']
            if apige_value['investment'].get('accruedInterest'):
                apige_bal += apige_value['investment']['accruedInterest']
            account_asset = account_value['account_additional_labels'][0]['account_additional_label_streamable_value']
            account_bal = account_asset['initial']
            Assert.log_assert(abs(apige_bal - self.convert_to_float(account_bal)) <= 1, "")
        elif balance_type == "Liability" and apige_value.get('liability', ""):
            apige_bal = apige_value['liability']['outstandingBalance']
            account_liability = account_value['account_additional_labels'][1]
            account_bal = account_liability['account_additional_label_streamable_value']['initial']
            Assert.log_assert(abs(apige_bal - self.convert_to_float(account_bal)) <= 1, "")

    def verify_ms_completeview_accounts(self, views_data_enabled, apige_data):
        """validating mscompleteview account_section data with apigee response"""
        if not views_data_enabled:
            logging.info('There is no mobile_response views data.')
            return
        response = self.received_response
        account_section_data = response['mobile_response']['views'][0]['data']['account_sections']
        apige_account_data = apige_data['accountBalances']

        apige_uuids = [self.as_base64_string(i['accountInfo'].get('keyAccountID',
                                                                  i['accountInfo'].get('loanAccountNumber')))
                       for i in apige_account_data]
        for index, account_value in enumerate(account_section_data):
            Assert.log_assert(account_value['account_uuid'] in apige_uuids, "uuid is not matched")
            apige_val = apige_account_data[apige_uuids.index(account_value['account_uuid'])]
            self.validate_account_balances(apige_val, account_value)

    def get_views_data_enabled(self):
        response = self.received_response
        view_data = response['mobile_response']['views']
        if not view_data or view_data[0]['data'] == {}:
            return False
        return True

    def get_sm2_access_token(self, env):
        """sm2 access token generation"""
        sm2_url = SmsessionTags.sm_tag_url.format(env)

        body = {"smSession": self.user.session.cookies.get_dict()['SMSESSION'],
                SmsessionTags.transormation_clientid: SmsessionTags.transormation_clientid_value,
                SmsessionTags.transformationType: SmsessionTags.transformationType_value,
                "nonce": "string of characters"
                }
        headers = {"Content-Type": "application/json"}
        response = requests.request("POST", sm2_url, headers=headers, data=json.dumps(body), verify=False)
        access_token = response.json().get('access_token', '')
        return access_token

    def get_et_auth_details(self, mapped_user_id):
        """et-auth-details generation"""
        details = {"customer": {"userId": mapped_user_id, "userName": ""},
                   "x": {"platform": "MS", "platformUUID": "123456789", "source": "ET", "channel": "ET-MOBILE"},
                   "anon": False}
        details_as_json_str = json.dumps(details)
        details_encrypted = self.as_base64_string(details_as_json_str)
        return details_encrypted

    def get_apige_data(self, env, views_data_enabled, username):

        """apigee data response """

        if not views_data_enabled:
            logging.info('There is no mobile_response views data.')
            return {}
        mapped_user_id = MsCompleteViewTags.account_uuids_dict.get(username, {})
        if mapped_user_id:
            mapped_user_id = mapped_user_id.get(env, '')
        else:
            logging.info('There is no external uuid for this account')
            return {}
        access_token = self.get_sm2_access_token(env)
        et_auth = self.get_et_auth_details(mapped_user_id)
        url = ApigeeDataTags.apigee_url.format(env)
        body = {ApigeeDataTags.requestType: ApigeeDataTags.requestType_value,
                ApigeeDataTags.timePeriod: ApigeeDataTags.timePeriod_value,
                ApigeeDataTags.expand: ApigeeDataTags.expand_value}
        headers = {"Content-Type": "application/json", "x-et-auth-details": et_auth,
                   "Authorization": "Bearer {0}".format(access_token)}
        response = requests.request("POST", url, headers=headers, data=json.dumps(body),
                                    verify=False)
        return response.json()

    def verify_display_positions_tags(self):
        positions = self.parse_response().references.positions()
        intruments = self.parse_response().references.instruments()
        Assert.log_assert(len(positions) != 0, "Positions list is empty")
        Assert.log_assert(len(intruments) != 0, "Instruments list is empty")

    def verify_node_response(self):
        response_body = list(self.received_response.keys())[0]
        if response_body != 'mobile_response':
            logging.info(f"checking the error code for the response body")
            Assert.verify_response_code(200, self.received_response['ApiAggregatorResponse']['responseCode'],
                                        f"Actual Error code :: "
                                        f"{self.received_response['ApiAggregatorResponse']['responseCode']}")
        else:
            expected_views_tags = MgsViews.type_data
            views_tag = self.received_response["mobile_response"]["views"]
            logging.info(f"Verifying view tags")
            for item in views_tag:
                Assert.verify_required_fields(set(item.keys()),
                                              expected_views_tags)

    def verifynasdaq(self, response, env, username):
        quote_type = NasdaqloginTags.quote_type_dict.get(username)
        if quote_type:
            quote_type_id = quote_type.get(env)
        response_quote_type = response['login']['QuoteType']
        if quote_type_id != response_quote_type:
            Assert.log_assert("Quotetype doesn't match with login")


