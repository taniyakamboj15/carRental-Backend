from fastapi import Header, HTTPException
import redis
from app.core.config import settings
import json



redis_client = redis.Redis(host='localhost', port=6379, db=1) # using db 1 for keys, 0 is for celery

def check_idempotency(idempotency_key: str = Header(None, alias="Idempotency-Key")):
    
    if not idempotency_key:
        return None 
        
    # Check Redis
    cached_response = redis_client.get(f"idempotency:{idempotency_key}")
    if cached_response:
        raise HTTPException(
            status_code=409, # Conflict
            detail="This request has already been processed (Idempotent replay)."
        )
    
    return idempotency_key

def save_idempotency_key(key: str, data: dict, expiry: int = 86400):
    """
    Save the key after successful processing.
    """
    if key:
        redis_client.setex(
            f"idempotency:{key}",
            expiry,
            json.dumps(data)
        )
