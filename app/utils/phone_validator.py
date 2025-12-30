from phonenumbers import parse, is_valid_number, NumberParseException


def validate_phone_number(phone_number: str) -> bool:
    """Validate phone number in E.164 format"""
    try:
        parsed = parse(phone_number, None)
        return is_valid_number(parsed)
    except NumberParseException:
        return False

