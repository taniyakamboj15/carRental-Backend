import re
import requests

def validate_phone(phone: str) -> bool:
    """
    Validates a phone number using a simple regex for international format.
    Example: +1234567890
    """
    if not phone:
        return False
    # Simple regex for international phone numbers (optional + and 1-15 digits)
    pattern = re.compile(r"^\+?[1-9]\d{1,14}$")
    return bool(pattern.match(phone))

def validate_city(location: str) -> bool:
    """
    Validates if a city/location exists using OpenStreetMap Nominatim API.
    Returns True if valid or if API fails (fail-open), False if strictly not found.
    """
    if not location:
        return False
    try:
        # Use Nominatim for basic city validation
        url = f"https://nominatim.openstreetmap.org/search?q={location}&format=json"
        headers = {'User-Agent': 'CarRentalApp/1.0'}
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code != 200:
             return True # Fail open if external service issue
        data = response.json()
        return len(data) > 0
    except Exception as e:
        print(f"Validation error: {e}")
        return True # Fail open if API is down
