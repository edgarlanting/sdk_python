import os
import unittest

from tests import config
from bunq.sdk import context


class BunqSdkTestCase(unittest.TestCase):
    # Config values
    _API_KEY = config.Config.get_api_key()

    # Name of bunq config file
    _FILENAME_BUNQ_CONFIG = "/bunq-test.conf"

    # Device description used for python tests
    _DEVICE_DESCRIPTION = 'Python test device'

    @classmethod
    def _get_api_context(cls):
        """
        Calls IsSessionActive to check if the session token is still active
        and returns the context.ApiContext.

        Catches ApiException if the session is inactive.
        Catches BunqException if the conf file does not exist.

        :rtype: context.ApiContext
        """

        filename_bunq_config_full = (cls._get_directory_test_root() +
                                     cls._FILENAME_BUNQ_CONFIG)

        try:
            api_context = context.ApiContext.restore(filename_bunq_config_full)
        except FileNotFoundError:
            api_context = context.ApiContext(context.ApiEnvironmentType.SANDBOX, cls._API_KEY,
                                     cls._DEVICE_DESCRIPTION, [])
        else:
            api_context.ensure_session_active()

        api_context.save(filename_bunq_config_full)

        return api_context

    @staticmethod
    def _get_directory_test_root():
        return os.path.dirname(os.path.abspath(__file__))
