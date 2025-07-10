import pytest
from core.pages.audit.validation_page import ValidationPage
from core.utils.farmer_profile_creator import FarmerSetupHelper
from core.utils.data_generator import DataGenerator

@pytest.mark.audit
def test_farmer_profile_created_and_visible_in_validation_screen(logged_in_page):
    page = logged_in_page
    validation_page = ValidationPage(page)

    # Step 1: Generate farmer payload
    farmer_name = DataGenerator.generate_random_name()
    farmer_payload = {
        "createOrganizationFarmer": {
            "countryId": "1",
            "dateOfBirth": "2000-12-09T00:00:00+0000",
            "familyDetail": {
                "fatherName": "Optimus Prime I",
                "maritalStatusId": "1",
                "motherName": "Ravenclaw",
                "totalMembersInFamily": 1
            },
            "farmerName": farmer_name,
            "farmerProfilePhotoId": "1",
            "genderId": "1",
            "houseNumber": "Plot 42",
            "kycDetails": [
                {
                    "kycFieldId": "1",
                    "kycFieldStringValue": "KYCTEST123"
                }
            ],
            "latitude": "12.9716",
            "longitude": "77.5946",
            "mobileNumber": DataGenerator.generate_random_phone_number(),
            "offlineCreatedAt": "2025-05-30T05:53:18+0000",
            "offlineUpdatedAt": "2025-05-30T05:53:18+0000",
            "regionId": "23",
            "regionPartId": "446",
            "road": "MG Road",
            "skillsAndResources": {
                "farmerResourceIds": ["1"],
                "farmerSkillIds": ["1"]
            }
        }
    }

    # Step 2: Create farmer profile via API
    helper = FarmerSetupHelper()
    created_farmer = helper.create_farmer_for_ft(farmer_payload=farmer_payload)

    # 🔹 Print the full response for debug
    print("✅ Farmer created:", created_farmer)

    assert created_farmer is not None, "❌ Failed to create farmer via API"
    created_name = created_farmer.get("farmerName")
    assert created_name, "❌ Created farmer does not have a name"

    # Step 3: Navigate to Audit → Validation
    validation_page.click_element("[data-testid='secure-link-AUDIT_PROFILE']")
    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(3000)  # short buffer

    # Step 4: Search and assert
    validation_page.search_farmer(created_name)
    assert validation_page.is_farmer_visible(created_name), \
        f"❌ Farmer '{created_name}' not visible in validation screen."