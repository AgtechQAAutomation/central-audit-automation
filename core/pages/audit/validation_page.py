from core.base.base_page import BasePage
from playwright.sync_api import Page
from core.utils.logger import get_logger
import allure

LOGGER = get_logger(__name__)

class ValidationPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        self.page = page
        self.approve_button = self.get_locator("button:has-text('Approve')")
        self.reject_button = self.get_locator("button:has-text('Reject')")
        self.skip_button = self.get_locator("button:has-text('Skip')")
        self.confirm_button = self.get_locator("button:has-text('Confirm')")
        self.reason_dropdown = self.get_locator("div[role='combobox']")
        self.reason_option = lambda reason: self.get_locator(f"text={reason}")
        self.no_more_requests_text = self.get_locator("text=No more applications to review. You're all good.")
        self.next_loader = self.get_locator("div:has-text('Loading next request')")

    @allure.step("Go to validation/audit page")
    def goto(self):
        LOGGER.info("Navigating to audit validation page")
        self.page.goto("/audit")
        self.page.wait_for_load_state("networkidle")

    @allure.step("Search for farmer name: {farmer_name}")
    def search_farmer(self, farmer_name: str):
        LOGGER.info(f"Searching for farmer: {farmer_name}")
        search_box = self.get_locator("input[placeholder='Search farmer']")
        self.type_text("input[placeholder='Search farmer']", farmer_name)
        self.page.keyboard.press("Enter")
        self.page.wait_for_timeout(1000)

    @allure.step("Check if farmer '{farmer_name}' is visible")
    def is_farmer_visible(self, farmer_name: str) -> bool:
        LOGGER.info(f"Checking if farmer '{farmer_name}' is visible in UI")
        locator = self.get_locator(f"text={farmer_name}")
        return locator.is_visible()
    
    @allure.step("Get farmer row for '{farmer_name}'")
    def get_farmer_row(self, farmer_name: str):
       locator = self.get_locator(f"text={farmer_name}")
       locator.wait_for(timeout=5000)
       return locator

    @allure.step("Approve application and proceed to next")
    def approve_application(self):
        LOGGER.info("Approving current application")
        self.click_element("button:has-text('Approve')")
        self.wait_for_selector("button:has-text('Confirm')")
        self.click_element("button:has-text('Confirm')")
        self.wait_for_next_application()

    @allure.step("Reject application with reason: '{reason_text}'")
    def reject_application(self, reason_text: str):
        LOGGER.info(f"Rejecting application with reason: {reason_text}")
        self.click_element("button:has-text('Reject')")
        self.click_element("div[role='combobox']")
        self.click_element(f"text={reason_text}")
        self.click_element("button:has-text('Confirm')")
        self.wait_for_next_application()

    @allure.step("Skip current application")
    def skip_application(self):
        LOGGER.info("Skipping current application")
        self.click_element("button:has-text('Skip')")
        self.wait_for_next_application()

    @allure.step("Wait for next application to load")
    def wait_for_next_application(self):
        LOGGER.info("Waiting for next request to load")
        try:
            self.next_loader.wait_for(state="hidden", timeout=5000)
        except Exception:
            LOGGER.warning("Loader did not appear — assuming next request loaded instantly")

    @allure.step("Verify no more applications message is shown")
    def verify_no_more_requests_message(self):
        LOGGER.info("Verifying end-of-queue message is visible")
        self.expect_locator("text=No more applications to review. You're all good.").to_be_visible()