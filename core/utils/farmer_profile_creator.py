import requests
import logging
import uuid
from typing import Tuple
from core.utils.api.api_clients.graphql_client import GraphQLClient
from config.settings import settings

logger = logging.getLogger(__name__)

class FarmerSetupHelper:
    def __init__(self):
        self.ft_gql_client = None

    def _get_firebase_token(self, email: str, password: str) -> str:
        url = settings.FIREBASE_SIGNIN_URL
        if not url:
           logger.error("FIREBASE_SIGNIN_URL is not set in environment or settings.")
           raise ValueError("FIREBASE_SIGNIN_URL is required.")

        payload = {
            "email": email,
            "password": password,
            "returnSecureToken": True
        }
        headers = {'Content-Type': 'application/json'}

        logger.info(f"Firebase signin attempt for FT email: {email} at URL: {url.split('?')[0]}")
        try:
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()
            id_token = data.get("idToken")
            if not id_token:
                logger.error(f"Firebase idToken missing for FT {email}. Response: {data}")
                raise ValueError("Firebase idToken not found in response.")
            logger.info(f"Obtained Firebase idToken for FT {email}.")
            return id_token
        except requests.exceptions.HTTPError as http_err:
            logger.error(
                f"HTTP error during Firebase signin for FT {email}: {http_err} - Response: {response.text}"
            )
            raise
        except Exception as e:
            logger.error(f"Unexpected error during Firebase signin for FT {email}: {e}")
            raise

    def _app_login_with_firebase_token(self, firebase_token: str, email: str, organization_name: str) -> str:
        """
        Use the Firebase idToken to log in to the app’s GraphQL and retrieve an app-specific access token.
        """
        temp_gql = GraphQLClient(endpoint=settings.GRAPHQL_ENDPOINT)
        mutation = """
            mutation AuthService_AuthService_Login($access_token: String!, $email: String!, $organization_name: String!) {
                AuthService_AuthService_Login(
                    input: {
                        access_token: $access_token
                        email: $email
                        organization_name: $organization_name
                    }
                ) {
                    access_token
                    refresh_token
                    token_type
                }
            }
        """
        variables = {
            "access_token": firebase_token,
            "email": email,
            "organization_name": organization_name
        }

        logger.info(f"GraphQL login attempt for FT {email}, org: {organization_name}")
        try:
            resp = temp_gql.execute(mutation, variables)
            login_data = resp.get("AuthService_AuthService_Login")
            if not login_data or not login_data.get("access_token"):
                logger.error(
                    f"Missing app access_token in GraphQL login response for FT {email}. Response: {resp}"
                )
                raise ValueError("App access_token not found in GraphQL login response.")
            app_token = login_data["access_token"]
            logger.info(f"Obtained app access_token for FT {email}.")
            return app_token
        except Exception as e:
            logger.error(f"Error during GraphQL login for FT {email}: {e}")
            raise

    def _generate_unique_farmer_ids(self) -> Tuple[str, str]:
        """
        Returns a tuple of (farmerId, farmerUniqueId), both guaranteed to be unique.
        You can tweak the prefix or format if your system expects something different.
        """
        unique_suffix = uuid.uuid4().hex
        farmer_id = f"org_farmer_{unique_suffix}"
        farmer_unique_id = f"farmer_{unique_suffix}"
        return farmer_id, farmer_unique_id

    def _register_farmer(self, app_token: str, farmer_payload: dict) -> dict:
        """
        Executes the registerFarmer mutation using the provided app token and input payload.
        Before sending, inject fresh farmerId and farmerUniqueId if they’re missing.
        """
        # Ensure our GraphQL client has the correct Authorization header
        if not self.ft_gql_client or self.ft_gql_client.transport.headers.get("Authorization") != f"Bearer {app_token}":
            self.ft_gql_client = GraphQLClient(
                endpoint=settings.GRAPHQL_ENDPOINT,
                auth_token=app_token
            )

        # Drill down to the nested "createOrganizationFarmer" dict
        payload_root = farmer_payload.get("createOrganizationFarmer", {})
        if not payload_root:
            raise ValueError("Expected key 'createOrganizationFarmer' in farmer_payload.")

        # Generate unique IDs if not already present
        if not payload_root.get("farmerId") or not payload_root.get("farmerUniqueId"):
            new_farmer_id, new_unique_id = self._generate_unique_farmer_ids()
            payload_root["farmerId"] = new_farmer_id
            payload_root["farmerUniqueId"] = new_unique_id
            logger.debug(f"Injected unique IDs: farmerId={new_farmer_id}, farmerUniqueId={new_unique_id}")

        mutation = """
            mutation RegisterFarmer($input: RegisterFarmerRequestInput!) {
                registerFarmer(input: $input) {
                    organizationFarmer {
                        farmerId
                        farmerName
                        mobileNumber
                    }
                }
            }
        """
        variables = {"input": {"createOrganizationFarmer": payload_root}}

        logger.info("Calling registerFarmer mutation for new farmer.")
        try:
            resp = self.ft_gql_client.execute(mutation, variables)
            farmer_data = resp.get("registerFarmer", {}).get("organizationFarmer")
            if not farmer_data:
                logger.error(f"No 'organizationFarmer' returned. Full response: {resp}")
                raise ValueError("registerFarmer did not return expected farmer payload.")
            logger.info(f"Farmer registered successfully: {farmer_data}")
            return farmer_data
        except Exception as e:
            logger.error(f"Error during registerFarmer mutation: {e}")
            raise

    def create_farmer_for_ft(self,
                             ft_email: str = None,
                             ft_password: str = None,
                             organization_name: str = None,
                             farmer_payload: dict = None) -> dict:
        """
        Orchestrates the flow:
         1. Firebase signin for FT (using ft_email, ft_password).
         2. App login to get app_token.
         3. registerFarmer mutation with farmer_payload (injecting unique IDs if needed).
        Returns the newly created farmer’s details.
        """
        # Allow defaults from settings if not passed explicitly
        ft_email = ft_email or settings.FT_EMAIL
        ft_password = ft_password or settings.FT_PASSWORD
        organization_name = organization_name or settings.ORGANIZATION_NAME

        if farmer_payload is None:
            raise ValueError("Missing farmer_payload for registerFarmer.")

        try:
            # 1) Get Firebase token for FT
            firebase_token = self._get_firebase_token(ft_email, ft_password)

            # 2) Use that to log in to GraphQL and get an app_token
            app_token = self._app_login_with_firebase_token(firebase_token,
                                                            ft_email,
                                                            organization_name)

            # 3) Call registerFarmer mutation, auto-injecting IDs if absent
            new_farmer = self._register_farmer(app_token, farmer_payload)
            return new_farmer

        except Exception as e:
            logger.critical(f"Failed to create farmer under FT {ft_email}: {e}")
            return None


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    helper = FarmerSetupHelper()

    # Example "template" payload: you can omit farmerId / farmerUniqueId here
    sample_farmer_template = {
        "createOrganizationFarmer": {
            "countryId": "1",
            "dateOfBirth": "2000-12-09T00:00:00+0000",
            "familyDetail": {
                "fatherName": "Optimus Prime I",
                "maritalStatusId": "1",
                "motherName": "Ravenclaw",
                "totalMembersInFamily": 1,
                "spouseName": None,
                "numberOfChildren": None
            },
            # omit "farmerId" and "farmerUniqueId" → helper will generate them
            "farmerName": "sadham",
            "farmerProfilePhotoId": "1",
            "genderId": "1",
            "houseNumber": "mollit aliquip qui officia",
            "kycDetails": [
                {
                    "kycFieldId": "1",
                    "kycFieldStringValue": "tempor in ullamco labore"
                }
            ],
            "latitude": "12334.23324N",
            "longitude": "2342.232342E",
            "mobileNumber": "6383440981",
            "offlineCreatedAt": "2025-05-30T05:53:18+0000",
            "offlineUpdatedAt": "2025-05-30T05:53:18+0000",
            "regionId": "23",
            "regionPartId": "446",
            "road": "Annan Nagar",
            "skillsAndResources": {
                "farmerResourceIds": ["1"],
                "farmerSkillIds": ["1"]
            }
        }
    }

    created_farmer = helper.create_farmer_for_ft(
        farmer_payload=sample_farmer_template
    )
    if created_farmer:
        logger.info(f"Created Farmer Details: {created_farmer}")
    else:
        logger.error("Failed to register farmer.")