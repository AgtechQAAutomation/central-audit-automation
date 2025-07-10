import re
import allure
from playwright.sync_api import Page, Locator, expect as playwright_expect
from core.base.base_page import BasePage
from core.utils.logger import get_logger

LOGGER = get_logger(__name__)

class LoginPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        self.organization_name_input = 'input[placeholder="Enter your organization name"]'
        self.work_email_input = 'input[placeholder="ex. email@domain.com"]'
        self.continue_button = 'button:has-text("Continue")'
        self.sign_in_header = 'text="Sign In to your account"'
        self.password_input = 'input[placeholder="Password"]'
        self.error_message_selector = 'p.bodySm:has-text("Failed to get authentication method. Please try again later.")'
        self.login_url = 'http://148.113.1.233/login'
        self.login_url_path = "/login"

    @allure.step("Navigate to the Login Page")
    def goto(self):
        LOGGER.info(f"Navigating to login page: {self.login_url}")
        self.page.goto(self.login_url)
        self.wait_for_element_visible(self.organization_name_input, timeout=10_000)

    @allure.step("Enter Organization: '{organization}', Email: '{email}', and click Continue")
    def enter_company_and_user_name(self, organization: str, email: str):
        self.fill_element(self.organization_name_input, organization)
        self.fill_element(self.work_email_input, email)
        self.click_element(self.continue_button)
        LOGGER.info(f"Entered Org: '{organization}', Email: '{email}' and clicked Continue.")
        try:
            self.page.wait_for_selector(
                f"{self.password_input}, {self.error_message_selector}",
                state="visible",
                timeout=7000
            )
            LOGGER.info("Password input or error message became visible after first step.")
        except Exception as e:
            LOGGER.warning(f"Neither password input nor error message appeared after first continue: {e}")
            allure.attach(self.page.content(), name="Page HTML on unexpected state", attachment_type=allure.attachment_type.HTML)

    @allure.step("Enter password and click Continue")
    def enter_password(self, password: str):
        self.wait_for_element_visible(self.password_input, timeout=10_000)
        self.fill_element(self.password_input, password)
        self.click_element(self.continue_button)
        LOGGER.info("Entered password and clicked Continue.")

    @allure.step("Perform full login with Org: '{organization}', Email: '{email}'")
    def login(self, organization: str, email: str, password: str):
        self.goto()
        self.enter_company_and_user_name(organization, email)
        try:
            self.wait_for_element_visible(self.password_input, timeout=7000)
            self.enter_password(password)
        except Exception as e:
            LOGGER.warning("Password input not visible, cannot proceed with entering password during full login flow.")
            allure.attach(self.page.content(), name="Page HTML - Password Input Not Visible", attachment_type=allure.attachment_type.HTML)
            raise

    @allure.step("Get 'Sign In' header text")
    def get_sign_in_header_text(self) -> str | None:
        return self.get_text(self.sign_in_header)

    @allure.step("Get error message element locator")
    def get_error_message_element(self) -> Locator:
        LOGGER.info("Providing locator for error message element.")
        return self.page.locator('p.bodySm:has-text("Please enter valid credentials")')