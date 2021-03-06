from bunq.sdk import client
from bunq.sdk.json import converter
from bunq.sdk.model.generated import endpoint
from bunq.sdk.model.generated import object_
from tests.bunq_test import BunqSdkTestCase
from tests.config import Config


class TestPaginationScenario(BunqSdkTestCase):
    """
    Tests:
        Pagination
    """

    @classmethod
    def setUpClass(cls):
        cls._USER_ID = Config.get_user_id()
        cls._MONETARY_ACCOUNT_ID = Config.get_monetary_account_id_1()
        cls._COUNTER_PARTY_ALIAS_OTHER = \
            Config.get_pointer_counter_party_other()
        cls._API_CONTEXT = cls._get_api_context()
        cls._PAYMENT_LISTING_PAGE_SIZE = 2
        cls._PAYMENT_REQUIRED_COUNT_MINIMUM = cls._PAYMENT_LISTING_PAGE_SIZE * 2
        cls._NUMBER_ZERO = 0
        cls._PAYMENT_AMOUNT_EUR = '0.01'
        cls._PAYMENT_CURRENCY = 'EUR'
        cls._PAYMENT_DESCRIPTION = 'Python test Payment'

    def test_api_scenario_payment_listing_with_pagination(self):
        self._ensure_enough_payments()
        payments_expected = self._payments_required()
        pagination = client.Pagination()
        pagination.count = self._PAYMENT_LISTING_PAGE_SIZE

        response_latest = self._list_payments(pagination.url_params_count_only)
        pagination_latest = response_latest.pagination
        response_previous = self._list_payments(
            pagination_latest.url_params_previous_page
        )
        pagination_previous = response_previous.pagination
        response_previous_next = self._list_payments(
            pagination_previous.url_params_next_page
        )
        payments_previous = response_previous.value
        payments_previous_next = response_previous_next.value
        payments_actual = payments_previous_next + payments_previous
        payments_expected_serialized = converter.serialize(payments_expected)
        payments_actual_serialized = converter.serialize(payments_actual)

        self.assertEqual(payments_expected_serialized,
                         payments_actual_serialized)

    def _ensure_enough_payments(self):
        """
        :rtype: None
        """

        for _ in range(self._payment_missing_count):
            self._create_payment()

    @property
    def _payment_missing_count(self):
        """
        :rtype: int
        """

        return self._PAYMENT_REQUIRED_COUNT_MINIMUM - \
            len(self._payments_required())

    def _payments_required(self):
        """
        :rtype: list[endpoint.Payment]
        """

        pagination = client.Pagination()
        pagination.count = self._PAYMENT_REQUIRED_COUNT_MINIMUM

        return self._list_payments(pagination.url_params_count_only).value

    def _list_payments(self, params):
        """
        :type params: dict[str, str]

        :rtype BunqResponse[list[Payment]]
        """

        return endpoint.Payment.list(self._API_CONTEXT, self._USER_ID,
                                     self._MONETARY_ACCOUNT_ID, params)

    def _create_payment(self):
        """
        :rtype: None
        """

        request_map = {
            endpoint.Payment.FIELD_AMOUNT:
                object_.Amount(self._PAYMENT_AMOUNT_EUR,
                               self._PAYMENT_CURRENCY),
            endpoint.Payment.FIELD_DESCRIPTION: self._PAYMENT_DESCRIPTION,
            endpoint.Payment.FIELD_COUNTERPARTY_ALIAS:
                self._COUNTER_PARTY_ALIAS_OTHER,
        }

        endpoint.Payment.create(self._API_CONTEXT, request_map,
                                self._USER_ID, self._MONETARY_ACCOUNT_ID)
