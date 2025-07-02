from faker import Faker

fake = Faker() # Default locale: en_US

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

    # Add more specific generators as needed
    @staticmethod
    def generate_random_text(max_chars: int = 50) -> str:
        return fake.text(max_nb_chars=max_chars)