import allure # Import Allure
from playwright.sync_api import Page, Locator, expect as playwright_expect
from core.base.base_page import BasePage # Your BasePage
from core.utils.logger import get_logger # Adjust path if necessary

LOGGER = get_logger(__name__)

class LoginPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        self.organization_name_input = 'input[placeholder="Enter your organization name"]'
        self.work_email_input = 'input[placeholder="ex. email@domain.com"]'
        self.continue_button = '//button[text()="Continue"]'
        self.sign_in_header = 'text="Sign In to your account"'
        self.password_input = 'input[placeholder="Password"]'
        self.error_message_selector = 'p.bodySm:has-text("Failed to get authentication method. Please try again later.")'
        self.login_url = 'http://148.113.1.233/login' # Full URL from your code
        self.login_url_path = "/login" # Path for URL checks

    @allure.step("Navigate to the Login Page")
    def goto(self):
        # super().navigate(self.login_url) # Using the navigate method from BasePage
        LOGGER.info(f"Navigating to login page: {self.login_url}")
        self.page.goto(self.login_url)


    @allure.step("Enter Organization: '{organization}', Email: '{email}', and click Continue")
    def enter_company_and_user_name(self, organization: str, email: str):
        self.fill_element(self.organization_name_input, organization)
        self.fill_element(self.work_email_input, email)
        # self.page.wait_for_timeout(5000) # Consider if this explicit wait is always needed or can be replaced by Playwright's auto-waits
        self.click_element(self.continue_button)
        LOGGER.info(f"Entered Org: '{organization}', Email: '{email}' and clicked Continue.")
        try:
            # Wait for either password input or error message to decide next state
            self.page.wait_for_selector(f"{self.password_input}, {self.error_message_selector}", state="visible", timeout=5000)
            LOGGER.info("Password input or error message became visible after first step.")
        except Exception as e:
            LOGGER.warning(f"Neither password input nor error message appeared after first continue: {e}")
            # This might indicate an unexpected page state, an attachment will be useful here.
            allure.attach(self.page.content(), name="Page HTML on unexpected state", attachment_type=allure.attachment_type.HTML)


    @allure.step("Enter password and click Continue") # Password value not in step name
    def enter_password(self, password: str):
        self.fill_element(self.password_input, password)
        self.click_element(self.continue_button)
        LOGGER.info("Entered password and clicked Continue.")

    @allure.step("Perform full login with Org: '{organization}', Email: '{email}'")
    def login(self, organization: str, email: str, password: str):
        self.goto() # This already has a step
        self.enter_company_and_user_name(organization, email) # This already has a step
        
        # Check if password input is visible before trying to fill it
        # This is important because enter_company_and_user_name might result in an error state
        if self.is_visible(self.password_input, timeout=1000): # Short timeout to check presence
            self.enter_password(password) # This already has a step
        else:
            LOGGER.warning("Password input not visible, cannot proceed with entering password during full login flow. Error might have occurred.")
            # Optionally attach current page state if login cannot proceed
            allure.attach(self.page.content(), name="Page HTML - Password Input Not Visible", attachment_type=allure.attachment_type.HTML)
            # Depending on expected behavior, you might want to raise an error or let the test assertions handle it.


    @allure.step("Get 'Sign In' header text")
    def get_sign_in_header_text(self) -> str | None:
        return self.get_text(self.sign_in_header)

    @allure.step("Get error message element locator")
    def get_error_message_element(self) -> Locator:
        """Returns the Playwright Locator for the error message element."""
        LOGGER.info("Providing locator for error message element.")
        return self.page.locator(self.error_message_selector)