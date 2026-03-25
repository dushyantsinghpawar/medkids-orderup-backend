from datetime import datetime, timedelta
from jose import jwt, JWTError
from app.core.config import JWT_SECRET_KEY, JWT_ALGORITHM, JWT_EXPIRE_MINUTES

def create_access_token(subject: str, expires_delta: timedelta = None) -> str:
    """Create a short-lived access token (15 minutes)."""
    if expires_delta is None:
        expires_delta = timedelta(minutes=15)
    
    expire = datetime.utcnow() + expires_delta
    payload = {"sub": subject, "exp": expire, "type": "access"}
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)

def create_refresh_token(subject: str) -> str:
    """Create a long-lived refresh token (7 days)."""
    expire = datetime.utcnow() + timedelta(days=7)
    payload = {"sub": subject, "exp": expire, "type": "refresh"}
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)

def verify_token(token: str, token_type: str = "access") -> dict:
    """
    Verify and decode a JWT token.
    
    Args:
        token: The JWT token to verify
        token_type: "access" or "refresh"
    
    Returns:
        Decoded payload if valid
    
    Raises:
        JWTError if token is invalid or expired
    """
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        
        # Verify token type matches
        if payload.get("type") != token_type:
            raise JWTError("Invalid token type")
        
        return payload
    except JWTError:
        raise

def decode_token(token: str) -> dict:
    """Decode a token without strict type checking (for password reset tokens)."""
    try:
        return jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
    except JWTError:
        return None