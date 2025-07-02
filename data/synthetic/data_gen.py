from faker import Faker
import random
import string
from datetime import datetime, timedelta

try:
    fake = Faker('en_IN')
except Exception: 
    fake = Faker() 
    
class DataGenerator:

    @staticmethod
    def get_random_email():
        return fake.email()

    @staticmethod
    def generate_random_password(length=12, special_chars=True, digits=True, upper_case=True, lower_case=True):
        """
        Generates a random password using Faker.
        :param length: Length of the password.
        :param special_chars: Whether to include special characters.
        :param digits: Whether to include digits.
        :param upper_case: Whether to include uppercase letters.
        :param lower_case: Whether to include lowercase letters.
        :return: A randomly generated password string.
        """
        return fake.password(
            length=length,
            special_chars=special_chars,
            digits=digits,
            upper_case=upper_case,
            lower_case=lower_case
        )
    
    @staticmethod
    def get_farmer_name():
        return fake.name()

    @staticmethod
    def get_valid_phone_number():
        # Generates a 10-digit number, typically starting with 6, 7, 8, or 9 for Indian mobiles
        return f"{random.randint(6, 9)}{fake.numerify(text='#########' )}"

    @staticmethod
    def get_invalid_phone_number_short():
        return fake.numerify(text='#####') # 5 digits

    @staticmethod
    def get_invalid_phone_number_long():
        return fake.numerify(text='##############') # 14 digits
    
    @staticmethod
    def get_invalid_phone_number_chars():
        # Contains non-digit characters
        return fake.bothify(text='???#######', letters='ABCXYZ')


    @staticmethod
    def get_address_line():
        return fake.street_address()

    @staticmethod
    def get_pincode():
        # Indian pincodes are 6 digits
        return fake.numerify(text='######') 

    @staticmethod
    def get_valid_govt_id_aadhaar():
        # Aadhaar is 12 digits
        return fake.numerify(text='############')
    
    @staticmethod
    def get_valid_govt_id_pan():
        # PAN is 10 chars: 5 letters, 4 numbers, 1 letter
        return fake.bothify(text='?????####?', letters='ABCDEFGHIJKLMNOPQRSTUVWXYZ').upper()


    @staticmethod
    def get_invalid_govt_id_short(length=8):
        return fake.numerify(text='#' * length) 

    @staticmethod
    def get_invalid_govt_id_long(length=16):
        return fake.numerify(text='#' * length) 
    
    @staticmethod
    def get_invalid_govt_id_chars(length=12):
        # Mix of numbers and disallowed characters for a numeric ID
        return fake.bothify(text='?' * length, letters='!@#$')


    @staticmethod
    def get_parent_name():
        return fake.name()
        
    @staticmethod
    def get_random_string(length=10, include_numbers=False, include_special_chars=False):
        characters = string.ascii_letters
        if include_numbers:
            characters += string.digits
        if include_special_chars:
            characters += string.punctuation
        return ''.join(random.choice(characters) for i in range(length))

    @staticmethod
    def get_date_in_format(years_offset=0, date_format="%d/%m/%Y"):
        """
        Generates a date relative to today.
        years_offset: positive for future, negative for past.
        """
        target_date = datetime.now() + timedelta(days=365 * years_offset)
        # Add some randomness to days and months to avoid always picking the same day
        target_date += timedelta(days=random.randint(-180, 180))
        return target_date.strftime(date_format)

# Example Usage (can be removed or kept for testing this script)
if __name__ == '__main__':
    print(f"Farmer Name: {DataGenerator.get_farmer_name()}")
    print(f"Valid Phone: {DataGenerator.get_valid_phone_number()}")
    print(f"Invalid Phone (short): {DataGenerator.get_invalid_phone_number_short()}")
    print(f"Invalid Phone (chars): {DataGenerator.get_invalid_phone_number_chars()}")
    print(f"Address: {DataGenerator.get_address_line()}")
    print(f"Pincode: {DataGenerator.get_pincode()}")
    print(f"Valid Aadhaar: {DataGenerator.get_valid_govt_id_aadhaar()}")
    print(f"Valid PAN: {DataGenerator.get_valid_govt_id_pan()}")
    print(f"Invalid ID (short): {DataGenerator.get_invalid_govt_id_short()}")
    print(f"Invalid ID (chars): {DataGenerator.get_invalid_govt_id_chars(length=12)}")
    print(f"Father's Name: {DataGenerator.get_parent_name()}")
    print(f"Past Date (5 years ago): {DataGenerator.get_date_in_format(years_offset=-5)}")
    print(f"Future Date (2 years ahead): {DataGenerator.get_date_in_format(years_offset=2)}")
    print(f"Random String: {DataGenerator.get_random_string()}")
