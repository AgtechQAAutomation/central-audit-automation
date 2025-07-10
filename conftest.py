import pytest
from playwright.sync_api import Playwright, APIRequestContext, Page
from core.utils.logger import get_logger 
import os
from core.pages.login.login_page import LoginPage
from dotenv import load_dotenv

load_dotenv() # Loads variables from .env into environment variables

LOGGER = get_logger(__name__)

# --- Configuration from Environment Variables ---
BASE_URL = os.getenv("BASE_URL") 
API_BASE_URL = os.getenv("API_BASE_URL")
GRPC_SERVER_ADDRESS = os.getenv("GRPC_SERVER_ADDRESS")
DEFAULT_TIMEOUT = int(os.getenv("DEFAULT_TIMEOUT", "10000"))
HEADLESS_MODE = os.getenv("HEADLESS_MODE", "true").lower() == 'true'
DEFAULT_BROWSER = os.getenv("DEFAULT_BROWSER", "chromium")
TRACE_MODE = os.getenv("TRACE_MODE", "on-first-retry")

@pytest.fixture(scope="session")
def browser_context_args(browser_context_args, pytestconfig):
    args = {**browser_context_args} 

    if pytestconfig.getoption("video") != "off":
        args["record_video_dir"] = "videos/"
        args["record_video_size"] = {"width": 1280, "height": 720}
    else:
        args.pop("record_video_dir", None)
        args.pop("record_video_size", None)

    args.update({
        "base_url": BASE_URL, 
        "ignore_https_errors": True,
        "locale": "en-US",
        "viewport": {"width": 1280, "height": 720},
    })

    return {k: v for k, v in args.items() if v is not None}

@pytest.fixture(scope="function", autouse=True)
def set_page_default_timeout(page: Page):
    LOGGER.info(f"Setting default page timeout to: {DEFAULT_TIMEOUT}ms")
    page.set_default_timeout(DEFAULT_TIMEOUT)
    yield


@pytest.fixture(scope="session")
def api_request_context(playwright: Playwright):
    if not API_BASE_URL:
        LOGGER.warning("API_BASE_URL not set in .env, skipping APIRequestContext setup.")
        yield None
        return
        
    request_context = playwright.request.new_context(base_url=API_BASE_URL)
    LOGGER.info(f"APIRequestContext created for base_url: {API_BASE_URL}")
    yield request_context
    request_context.dispose()
    LOGGER.info("APIRequestContext disposed.")

@pytest.fixture(scope="session")
def simple_login_data():
    import json
    # Construct path relative to conftest.py's location
    current_dir = os.path.dirname(os.path.abspath(__file__))
    data_file = os.path.join(current_dir, "data", "json" , "simple_login_data.json") 
    LOGGER.info(f"Loading simple_login_data from: {data_file}")
    try:
        with open(data_file, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        LOGGER.error(f"Data file not found: {data_file}")
        pytest.fail(f"Data file not found: {data_file}")
        return None 

@pytest.fixture(scope="session")
def app_env_config():
    config = {
        "BASE_URL": BASE_URL,
        "API_BASE_URL": API_BASE_URL,
        "GRPC_SERVER_ADDRESS": GRPC_SERVER_ADDRESS,
        "DEFAULT_TIMEOUT": DEFAULT_TIMEOUT,
        "HEADLESS_MODE_CONFIG": os.getenv("HEADLESS_MODE", "true").lower() == 'true',
        "DEFAULT_BROWSER_CONFIG": os.getenv("DEFAULT_BROWSER", "chromium"),
        "TRACE_MODE_CONFIG": os.getenv("TRACE_MODE", "on-first-retry")
    }
    LOGGER.info(f"App environment config loaded: {config}")
    return config

@pytest.fixture(scope="function")
def logged_in_page(page: Page):
    LOGGER.info("Logging in for test validation screen...")

    # Load login credentials from environment
    org = os.getenv("VALIDATOR_ORG")
    email = os.getenv("VALIDATOR_EMAIL")
    password = os.getenv("VALIDATOR_PASSWORD")

    if not all([org, email, password]):
        pytest.fail("Missing VALIDATOR_ORG, VALIDATOR_EMAIL, or VALIDATOR_PASSWORD in .env")

    login_page = LoginPage(page)
    login_page.goto()
    login_page.login(org, email, password)

    # ✅ Wait until /home
    page.wait_for_url("**/home", timeout=10000)

    # ✅ Click on Audit button to go to /audit/profile
    LOGGER.info("Clicking Audit button to navigate to /audit/profile")
    page.click("a[data-testid='secure-link-AUDIT_PROFILE']")

    # ✅ Wait for audit profile screen
    page.wait_for_url("**/audit/profile", timeout=10000)
    LOGGER.info("Successfully landed on audit profile screen.")

    return page