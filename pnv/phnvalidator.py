## Implement a python phone number validator using regular expressions
## The validator should enforce the UK and Ireland phone number formats
## can you also include mobile phone numbers in the validation?
import re   


def validate_phone_number(phone_number):
    uk_ireland_pattern = re.compile(r'^(?:\+44\s?7\d{3}|\(?07\d{3}\)?)\s?\d{3}\s?\d{3}$|^(?:\+353\s?8\d{2}|\(?08\d{2}\)?)\s?\d{3}\s?\d{4}$')
    return bool(uk_ireland_pattern.match(phone_number))

# Test cases, include mobile numbers also
test_numbers = [
    "+44 7123 456 789",  # UK mobile
    "07123 456 789",     # UK mobile
    "+353 87 123 4567",  # Ireland mobile
    "087 123 4567",      # Ireland mobile   
    "+44 20 1234 5678",  # UK landline
    "020 1234 5678",     # UK landline
    "+44 7700 900123",   # UK mobile
    "(07700) 900 123",   # UK mobile with parentheses
    "+353 85 123 4567",  # Ireland mobile
    "(085) 123 4567",    # Ireland mobile with parentheses
    "+44 121 496 0000",  # UK Birmingham landline
    "0121 496 0000",     # UK landline
    "invalid123",        # Invalid format
    "+1 234 567 8900",   # US number (should not validate)
]

for number in test_numbers:
    print(f"{number}: {validate_phone_number(number)}")

