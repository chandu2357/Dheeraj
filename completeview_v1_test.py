import logging

import pytest
from dash_common.constants.pict_constants import PICTHeaderLabels as Header
from dash_core.core.common.decorators.decorators import log_assertion

from test_helpers.mgs_validation_helpers.accounts.completeview import \
    CompleteViewHelper
from test_helpers.mgs_validation_helpers.comments import Comments


class TestCompleteView(CompleteViewHelper):
    @pytest.mark.service
    @pytest.mark.completeView
    @pytest.mark.tags
    @pytest.mark.references_accounts
    @log_assertion()
    def test_complete_view(self, pict_case_args):
        """
        Script to test mgs completeView service
        :param pict_case_args: arguments from the pict file
        """
        self.mobile_authenticate(username=pict_case_args[Header.USERNAME],
                                 password=pict_case_args[Header.PASSWORD])
        self.complete_view_request()
        self.verify_views_references_objects_types()
        logging.info('\tChecking views objects tags.')
        self.verify_views_tags()
        logging.info('\tChecking references objects tags.')
        self.verify_references_accounts_tags()
        logging.info('Response tags check complete')
        Comments.log_comments()
