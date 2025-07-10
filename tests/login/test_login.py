import pytest
import allure 
import re
from playwright.sync_api import expect as playwright_expect
from core.pages.login.login_page import LoginPage 
from tests.base.base_test import BaseTest
from core.utils.logger import get_logger 

LOGGER = get_logger(__name__)

class Severity:
    BLOCKER = allure.severity_level.BLOCKER
    CRITICAL = allure.severity_level.CRITICAL
    NORMAL = allure.severity_level.NORMAL
    MINOR = allure.severity_level.MINOR
    TRIVIAL = allure.severity_level.TRIVIAL

@allure.epic("User Authentication")
@allure.feature("Login Feature")
@allure.suite("Web Login Functionality Tests") 
class TestSimpleLoginFunctionality(BaseTest):
    """
    Tests for simple login functionality on the web application.
    Inherits common setup from BaseTest.
    """

    @allure.story("Successful User Login")
    @allure.title("TC_WEB_LOGIN_001: Verify successful login with valid credentials")
    @allure.description("This test attempts to log in with valid credentials and checks for navigation to the home page.")
    @allure.severity(Severity.BLOCKER)
    @pytest.mark.login
    @pytest.mark.smoke # Example marker
    def test_should_allow_a_user_to_login_with_valid_credentials(self):
        login_page = LoginPage(self.page)
        valid_user = self.simple_login_data['validUser']
        organization = valid_user['organization']
        email = valid_user['email']
        password = valid_user['password']

        LOGGER.info(f"Starting test: TC_WEB_LOGIN_001 - Valid login for user {email}")

        # The login_page methods will have their own @allure.step decorators
        login_page.login(organization, email, password)

        with allure.step("Verify navigation to the home page after successful login"):
            try:
                playwright_expect(self.page).to_have_url(
                    re.compile(r".*/home/?$"),
                    timeout=self.app_env_config.get("DEFAULT_TIMEOUT", 10000)
                )
                LOGGER.info("Successfully navigated to the home page.")
            except Exception as e:
                LOGGER.error(f"AssertionError: Did not navigate to home page. URL: {self.page.url}. Error: {e}")
                # pytest-playwright and allure-pytest handle screenshot on failure
                raise

    @allure.story("Failed User Login - Invalid Credentials")
    @allure.title("TC_WEB_LOGIN_002: Verify error message for invalid credentials (e.g., wrong password or non-existent user)")
    @allure.description("This test attempts to log in with invalid credentials and verifies the display of an error message.")
    @allure.severity(Severity.CRITICAL)
    @pytest.mark.login
    def test_should_show_error_for_invalid_credentials(self):
        login_page = LoginPage(self.page)
        invalid_user = self.simple_login_data['invalidUser']
        organization = invalid_user['organization']
        email = invalid_user['email']
        password = invalid_user.get('password', None) 

        LOGGER.info(f"Starting test: TC_WEB_LOGIN_002 - Invalid login attempt for user {email}")

        with allure.step("Navigate to login page"): 
            login_page.goto()

        with allure.step(f"Enter company '{organization}', user '{email}' and attempt login"):
            login_page.enter_company_and_user_name(organization, email)
            
            if password:
               
                if login_page.is_visible(login_page.password_input, timeout=1000): # Check if password field appeared
                    login_page.enter_password(password) # This also clicks continue
                else:
                    LOGGER.info("Password input not visible after first step, error likely already displayed.")

        with allure.step("Verify error message is displayed"):
            try:
                error_message_element = login_page.get_error_message_element()
                playwright_expect(error_message_element).to_be_visible(
                timeout=self.app_env_config.get("ASSERTION_TIMEOUT", 5000)
                )
                actual_error_text = error_message_element.text_content()
                allure.attach(actual_error_text, name="Actual Error Message", attachment_type=allure.attachment_type.TEXT)

                # ✅ Correct expected message here
                expected_error_substring = "Please enter valid credentials"
                assert expected_error_substring in actual_error_text, \
                    f"Error message text mismatch. Expected to contain '{expected_error_substring}', got '{actual_error_text}'"

                LOGGER.info(f"Error message visible and content verified: '{actual_error_text}'")
            except Exception as e:
                LOGGER.error(f"AssertionError: Error message not visible or text mismatch. Error: {e}")
                raise

        with allure.step("Verify user remains on the login page"):
            try:
                # Check current URL contains /login or is the specific login page URL
                playwright_expect(self.page).to_have_url(
                    re.compile(r".*/login(\?.*)?$"),
                    timeout=self.app_env_config.get("DEFAULT_TIMEOUT", 5000)
                )
                LOGGER.info("User correctly remained on the login page.")
            except Exception as e:
                LOGGER.error(f"AssertionError: User did not remain on login page. URL: {self.page.url}. Error: {e}")
                raise
