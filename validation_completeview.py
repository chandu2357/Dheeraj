import logging

from dash_common.constants.mgs_mobile_gateway_constants import MgsViews, \
    ReferencesObjectTypes, ValuesValidationConstants, ViewsObjectDataLabel, \
    ViewsObjectStreamableValue, ViewsObjectTypes
from dash_core.core.common.dash_assert.dash_assert import Assert

from test_helpers.mgs_validation_helpers.accounts.accounts_base import \
    AccountsBaseHelper
from test_helpers.mgs_validation_helpers.comments import Comments
from test_helpers.mgs_validation_helpers.mgs_mapping_helpers import \
    ReferencesAccountsMapping
from test_helpers.mgs_validation_helpers.mgs_tag_helper import \
    CompleteViewAccountsTags
from test_helpers.mgs_validation_helpers.references.values_formats import \
    handle_value_formatting


class CompleteViewHelper(AccountsBaseHelper):
    """
    reference to actual Complete View response:
    tests/test_helpers/mgs/helper_test/mock/valid.json
    """
    view_types = ViewsObjectTypes.COMPLETEVIEW
    reference_types = ReferencesObjectTypes.COMPLETEVIEW
    streamable_values = ViewsObjectStreamableValue.COMPLETEVIEW
    streamable_labels = ViewsObjectDataLabel.COMPLETEVIEW
    expected_tags = CompleteViewAccountsTags

    def verify_views_tags(self):
        Comments.add_comments(Comments.view_net_asset_summary_comment)
        self.verify_views_net_assets_summary_tags()
        Comments.add_comments(Comments.views_account_summary_comment)
        self.verify_views_account_summary_tags(
            expected_tags=MgsViews.accounts_account_summary)

    def verify_views_values(self):
        self.verify_views_net_assets_summary_account_uuid_values()
        self.verify_views_net_assets_summary_values()
        self.verify_views_account_summary_values()

    def verify_views_net_assets_summary_values(self):
        """
        Verify views net_assets_summary values.

        :return:
        """
        net_assets_summary = self.parse_response().views.net_assets_summary()[0]

        account_uuids = net_assets_summary['account_uuids']
        accounts = self.parse_response().references.accounts()
        for uuid, account in zip(account_uuids, accounts):
            Assert.log_assert(uuid == account['accountUuid'])

        label = net_assets_summary['account_summary_streamable_value']
        net_assets = label['initial']
        _net_assets = self.from_dollar_to_float(net_assets)

        calculated_net_assets = 0
        account_summaries = self.parse_response().views.account_summary()
        for summary in account_summaries:
            account_value = summary['account_detail_value']
            account_value = self.from_dollar_to_float(account_value)
            calculated_net_assets += account_value

        delay = calculated_net_assets * ValuesValidationConstants.TOLERANCE
        _max = calculated_net_assets + delay
        _min = calculated_net_assets - delay

        Assert.log_assert(_min <= _net_assets <= _max,
                          f'Net assets : {net_assets},'
                          f' calculated net assets: {calculated_net_assets}')

    def verify_views_net_assets_summary_tags(self):
        views = self.received_response["mobile_response"]["views"]
        net_assets_summary = views[0]

        net_assets_summary_tags = set(net_assets_summary.keys())
        com_content = Comments.summary_tags_comment
        Comments.add_comments(com_content.format(net_assets_summary_tags))
        Assert.verify_required_fields(
            net_assets_summary_tags,
            MgsViews.type_data_cta_action)

        net_assets_summary_data_tags = set(net_assets_summary["data"].keys())
        log = Comments.summary_data_comment
        Comments.add_comments(log.format(net_assets_summary_data_tags))
        Assert.verify_required_fields(net_assets_summary_data_tags,
                                      MgsViews.net_assets_summary)
        label_name = "account_summary_streamable_value"
        stream_value = net_assets_summary["data"][label_name]
        summary_streamable_value = set(stream_value.keys())
        log = Comments.summary_streamable_comment
        Comments.add_comments(log.format(summary_streamable_value))
        Assert.verify_required_fields(summary_streamable_value,
                                      MgsViews.streamable_value)

    def verify_views_net_assets_summary_account_uuid_values(self):
        acc_uuids = self.parse_response().views.net_assets_summary()[0][
            "account_uuids"]
        account_summary = self.parse_response().views.account_summary()
        references_accounts = self.parse_response().references.accounts()
        Assert.log_assert(
            len(acc_uuids) == len(account_summary) == len(references_accounts),
            "account uuids not matching with reference")
        for uuid, summary, account in zip(acc_uuids, account_summary,
                                          references_accounts):
            Assert.log_assert(
                summary["account_uuid"] == account["accountUuid"] == uuid,
                "account_uuid is not matching")
            Assert.log_assert(
                summary["account_name"] == account["accountShortName"],
                "account_name and accountShortName is not matching.")

    def verify_net_summary_tag(self, tag):
        if tag == "net_assets_summary":
            self.net_assets_summary_values(tag)
        if tag == "net_gain_summary":
            self.net_gain_summary_values(tag)

    def tag_based_verification(self, tag):
        common_tag = {"ledgerAccountValue", "daysGain", "totalGain",
                      "daysGainPercent", "totalGainPercent"}

        if tag in common_tag:
            self.verify_views_tag_based(tag)

        if tag in ViewsObjectTypes.COMPLETEVIEW:
            self.verify_net_summary_tag(tag)

    def net_assets_summary_values(self, tag):
        """
        Verify views net_assets_summary values with S2 value.
        :return:
        """
        net_assets_summary = self.parse_response().views.net_assets_summary()[0]
        account_uuids = net_assets_summary['account_uuids']
        accounts = self.parse_response().references.accounts()
        for uuid, account in zip(account_uuids, accounts):
            Assert.log_assert(uuid == account['accountUuid'])

        value = net_assets_summary['account_summary_streamable_value']
        net_assets = value['initial']
        _net_assets = self.from_dollar_to_float(net_assets)

        s2_calculated_net_assets = 0
        logging.info(f"verification on Tag:: {tag} ....")
        for account in self.parse_response().references.accounts():
            if account['accountId'] == "83851862":  # MGS-2982
                continue
            mapping = ReferencesAccountsMapping(self._uid)
            if self.is_linked_bank_account_type(account):
                val = self.get_s2_account_value(account)
                s2_account_value = handle_value_formatting(val)
                s2_calculated_net_assets += s2_account_value
                logging.info(f"added account Value::{s2_account_value}")
            else:
                account_uuid = account['accountUuid']
                s2_account, s2_calls = mapping.get_account(
                    account_uuid,
                    request=self.prepared_request,
                    proofs=True)
                val = s2_account['accountValue']
                s2_account_value = handle_value_formatting(val)
                s2_calculated_net_assets += s2_account_value
                logging.info(f"added account Value::{s2_account_value}")
        self.compare_floats(_net_assets, s2_calculated_net_assets)
        logging.info(
            f'Completed verification on Net assets : {_net_assets} S2 Net '
            f'Asset:{s2_calculated_net_assets}')

    def net_gain_summary_values(self, tag):
        """
        Verify views net_gain_summary values with S2 value.
        :return:
        """
        net_gain_summary = self.parse_response().views.net_gain_summary()[0]
        references_accounts = self.parse_response().references.accounts()
        val = net_gain_summary['account_summary_streamable_value']
        net_gain = val['initial']
        account_uuids = net_gain_summary['account_uuids']
        _net_gain = handle_value_formatting(net_gain)
        s2_calculated_net_gain = 0

        logging.info(f"verification on Tag:: {tag} based ")
        for account in references_accounts:
            if account['accountId'] == "83851862":  # MGS-2982
                continue
            mapping = ReferencesAccountsMapping(self._uid)
            if account['accountUuid'] in account_uuids:
                s2_account, s2_calls = mapping.get_account(
                    account['accountUuid'],
                    request=self.prepared_request,
                    proofs=True)
                s2_net_gain = handle_value_formatting(s2_account['daysGain'])
                s2_calculated_net_gain += s2_net_gain
                logging.info(
                    f"s2 Net Gain  :: {s2_calculated_net_gain} dayGain added "
                    f"{s2_net_gain}")
        self.compare_floats(_net_gain, s2_calculated_net_gain)
        logging.info(
            f"Completed Verification on Tag:: {tag} Net Asset::{_net_gain}  "
            f"S2 Net Assert ::{s2_calculated_net_gain}")

    def verify_views_tag_based(self, tag):
        view = self.parse_response().views.net_assets_summary()[0]
        acc_uuids = view["account_uuids"]
        account_summary = self.parse_response().views.account_summary()
        references_accounts = self.parse_response().references.accounts
        Assert.log_assert(
            len(acc_uuids) == len(account_summary) == len(references_accounts),
            "account uuids not matching with reference")
        for uuid, summary, account in zip(acc_uuids, account_summary,
                                          references_accounts):
            Assert.log_assert(
                summary["account_uuid"] == account["accountUuid"] == uuid,
                "account_uuid is not matching")
            Assert.log_assert(
                summary["account_name"] == account["accountShortName"],
                "account_name and accountShortName is not matching.")
            if self.is_account_type(account, tag):
                continue
            mgs_data = handle_value_formatting(account.get(tag, 0))
            if self.verify_blank_value(mgs_data):
                continue
            self.verify_views_values_account_summary_based_tag(summary,
                                                               account, tag)

    def verify_views_values_account_summary_based_tag(self, summary, account,
                                                      tag):
        """
        Verify views account_summary values with S2 value.
        :return:
        """
        mapping = ReferencesAccountsMapping(self._uid)
        if len(summary['account_additional_labels']) == 3:
            days_gain, total_gain, cash = summary['account_additional_labels']
        else:
            days_gain, total_gain = summary['account_additional_labels']
            cash = 0

        s2_account, s2_calls = mapping.get_account(
            account["accountUuid"],
            request=self.prepared_request,
            proofs=True)
        s2_data = s2_account[f'{tag}']
        mgs_data = handle_value_formatting(account[f'{tag}'])
        mgs_account_id = account["accountId"]
        day_gain_tag = {"daysGain", "daysGainPercent"}
        total_gain_tag = {"totalGain", "totalGainPercent"}

        if tag in day_gain_tag:
            val = days_gain['account_additional_label_streamable_value']
            days_gain_initial_value = val["initial"]
            logging.info(
                f'verifying Tag:{tag}:: view value:: '
                f'{days_gain_initial_value} S2_data ::{s2_data} '
                f'::mgs value = {mgs_data}')
            Assert.log_assert(
                days_gain_initial_value == f"{account['daysGain']} ("
                                           f"{account['daysGainPercent']})")
            self.compare_floats(mgs_data, s2_data)
            logging.info(
                f"Completed verification of Tag::{tag} "f"in account_summarys "
                f"with accountid::{mgs_account_id}")
        if tag in total_gain_tag:
            val = total_gain['account_additional_label_streamable_value']
            total_gain_initial_value = val["initial"]
            logging.info(
                f'verifying Tag::{tag}:: '
                f'view value:: {total_gain_initial_value}:: '
                f'S2_data::{s2_data}')
            Assert.log_assert(
                total_gain_initial_value == f"{account['totalGain']} ("
                                            f"{account['totalGainPercent']})")
            self.compare_floats(mgs_data, s2_data)
            logging.info(
                f"Completed verification of Tag::{tag} "
                f"in account_summarys with accountid::{mgs_account_id}")

        if tag == "ledgerAccountValue" and cash:
            label = 'account_additional_label_streamable_value'
            cash_initial_value = cash[label]["initial"]
            logging.info(
                f'verifying Tag:{tag}:: '
                f'view value:: {cash_initial_value} '
                f'S2::{s2_data}')
            Assert.log_assert(
                cash_initial_value == account['ledgerAccountValue'])
            self.compare_floats(mgs_data, s2_data)
            logging.info(f"Completed verification of Tag::{tag} "
                         f"in account_summarys with accountid::"
                         f"{mgs_account_id}")

    def verify_blank_value(self, mgs_data):
        if mgs_data == 0.0:
            return True

    def is_account_type(self, account, tag):
        bank_acc = account['acctType'] == 'Bank'
        esp_acc = account['acctType'] == 'ESP'
        is_total_gain = tag == 'totalGain'
        is_total_gain_pct = tag == 'totalGainPercent'
        if bank_acc or esp_acc and is_total_gain or is_total_gain_pct:
            return True

    def get_account_value(self, account):
        account_summary = self.parse_response().views.account_summary()
        for summary in account_summary:
            if summary['account_uuid'] == account['accountUuid']:
                account_value = summary['account_detail_value']
                return account_value

    def get_s2_account_value(self, account):
        account_uuid = account['accountUuid']
        s2_account_values_helper = ReferencesAccountsMapping(self._uid)
        request = self.prepared_request
        account_from_s2 = s2_account_values_helper.get_account(account_uuid,
                                                               request=request,
                                                               proofs=True,
                                                               factory=False)
        _p1, _p2, _p3 = 'GetAllBalances', 'MGS-Balance', 'AVAIL_BALANCE'
        s2_account_value = account_from_s2[1][_p1][_p2][_p3]
        return s2_account_value

    def is_linked_bank_account_type(self, account):
        if account['acctType'] == 'Bank':
            return True
