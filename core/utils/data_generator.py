from faker import Faker
from datetime import datetime

fake = Faker()  # Default locale: en_US


class DataGenerator:
    @staticmethod
    def generate_random_email(domain: str = None) -> str:
        return fake.email(domain=domain)

    @staticmethod
    def generate_random_name() -> str:
        return fake.name()

    @staticmethod
    def generate_random_password(length: int = 12) -> str:
        return fake.password(length=length, special_chars=True, digits=True, upper_case=True, lower_case=True)

    @staticmethod
    def generate_company_name() -> str:
        return fake.company()

    @staticmethod
    def generate_random_text(max_chars: int = 50) -> str:
        return fake.text(max_nb_chars=max_chars)
    
    @staticmethod
    def generate_random_phone_number() -> str:
        return fake.msisdn()[:10]  # Ensures a 10-digit mobile number


def generate_random_farmer_payload():
    return {
        "createOrganizationFarmer": {
            "countryId": "1",
            "dateOfBirth": "2000-01-01T00:00:00+0000",
            "familyDetail": {
                "fatherName": fake.first_name_male(),
                "maritalStatusId": "1",
                "motherName": fake.first_name_female(),
                "totalMembersInFamily": fake.random_int(min=2, max=6),
                "spouseName": fake.first_name_female(),
                "numberOfChildren": fake.random_int(min=0, max=4)
            },
            "farmerName": fake.name(),
            "farmerProfilePhotoId": "1",
            "genderId": "1",
            "houseNumber": fake.building_number(),
            "kycDetails": [
                {
                    "kycFieldId": "1",
                    "kycFieldStringValue": fake.ssn()
                }
            ],
            "latitude": "12.9716N",
            "longitude": "77.5946E",
            "mobileNumber": fake.msisdn()[:10],
            "offlineCreatedAt": datetime.utcnow().isoformat() + "+0000",
            "offlineUpdatedAt": datetime.utcnow().isoformat() + "+0000",
            "regionId": "23",
            "regionPartId": "446",
            "road": fake.street_name(),
            "skillsAndResources": {
                "farmerResourceIds": ["1"],
                "farmerSkillIds": ["1"]
            }
        }
    }