import pytest
from playwright.sync_api import Page
from core.utils.logger import get_logger 

LOGGER = get_logger(__name__)

@pytest.mark.ui # Apply UI marker to all tests inheriting from this base
class BaseTest:
    """
    Base class for all UI tests.
    It sets up common fixtures as instance attributes.
    """

    @pytest.fixture(autouse=True)
    def _setup_common_fixtures(self, page: Page, simple_login_data, app_env_config):
        """
        This autouse fixture runs for every test method in inheriting classes.
        It makes common fixtures available as instance attributes (self.xxx).
        """
        LOGGER.debug(f"BaseTest setup for test method in class: {self.__class__.__name__}")
        self.page = page
        self.simple_login_data = simple_login_data
        self.app_env_config = app_env_config
        yield
        LOGGER.debug(f"BaseTest teardown for test method in class: {self.__class__.__name__}")

