from playwright.sync_api import Page, Locator
from core.utils.logger import get_logger 

LOGGER = get_logger(__name__)

class BasePage:
    def __init__(self, page: Page):
        self.page = page

    def navigate(self, url: str):
        LOGGER.info(f"Navigating to: {url}")
        self.page.goto(url)

    def get_title(self) -> str:
        LOGGER.info("Getting page title")
        return self.page.title()

    def wait_for_selector(self, selector: str, timeout: int = None, state: str = "visible"):
        LOGGER.info(f"Waiting for selector '{selector}' to be {state}")
        options = {"state": state}
        if timeout:
            options["timeout"] = timeout
        self.page.wait_for_selector(selector, **options)

    def click_element(self, selector: str, timeout: int = None, **kwargs):
        LOGGER.info(f"Clicking element: {selector}")
        locator = self.page.locator(selector)
        locator.click(timeout=timeout, **kwargs)

    def fill_element(self, selector: str, value: str, timeout: int = None, **kwargs):
        # Avoid logging full sensitive values if 'value' could be a password
        log_value = value[:20] + '...' if len(value) > 20 else value
        if "password" in selector.lower() or "pass" in selector.lower(): # Basic check
            log_value = "****" 
        LOGGER.info(f"Filling element '{selector}' with value: '{log_value}'")
        locator = self.page.locator(selector)
        # Using fill instead of type for inputs is generally recommended by Playwright
        locator.fill(value, timeout=timeout, **kwargs)


    def type_element(self, selector: str, value: str, delay: int = None, timeout: int = None, **kwargs):
        log_value = value[:20] + '...' if len(value) > 20 else value
        if "password" in selector.lower() or "pass" in selector.lower():
            log_value = "****"
        LOGGER.info(f"Typing into element '{selector}' value: '{log_value}'")
        locator = self.page.locator(selector)
        type_options = {}
        if delay is not None:
            type_options["delay"] = delay
        if timeout is not None:
            type_options["timeout"] = timeout
        locator.type(value, **type_options, **kwargs)

    def get_text(self, selector: str, timeout: int = None) -> str | None:
        LOGGER.info(f"Getting text from element: {selector}")
        locator = self.page.locator(selector)
        return locator.text_content(timeout=timeout)

    def is_visible(self, selector: str, timeout: int = None) -> bool:
        LOGGER.info(f"Checking visibility of element: {selector}")
        locator = self.page.locator(selector)
        try:
            return locator.is_visible(timeout=timeout if timeout is not None else 1000) # Default short timeout for checks
        except Exception:
            return False # If timeout occurs during visibility check

    def get_locator(self, selector: str) -> Locator:
        return self.page.locator(selector)

    def expect_locator(self, selector: str): # For direct use with Playwright's expect
        from playwright.sync_api import expect as playwright_expect
        return playwright_expect(self.page.locator(selector))
