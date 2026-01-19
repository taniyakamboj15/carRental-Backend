from slowapi import Limiter
from slowapi.util import get_remote_address

# Initialize Limiter
# key_func=get_remote_address means we limit by IP Address
limiter = Limiter(key_func=get_remote_address)
