from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from app.db.database import get_db
from app.models.user import User
from app.schemas.auth import (
    UserCreate, Token, RefreshTokenRequest, ForgotPasswordRequest, 
    ResetPasswordRequest, VerifyEmailRequest, AccessToken, UserOut
)
from app.core.security import (
    hash_password, verify_password, validate_password, generate_reset_token
)
from app.core.jwt import create_access_token, create_refresh_token, verify_token, decode_token
from app.core.email import EmailService
from app.core.rate_limit import rate_limit, rate_limit_by_email
from app.core.deps import get_current_user

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", response_model=UserOut)
async def register(
    data: UserCreate,
    request: Request,
    db: Session = Depends(get_db),
):
    """Register a new user with email and password."""
    
    # Rate limiting
    if not await rate_limit(request, max_requests=5, window_seconds=300):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many registration attempts. Please try again later."
        )
    
    # Check if email already exists
    existing = db.query(User).filter(User.email == data.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Validate password strength
    is_valid, error = validate_password(data.password)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error
        )
    
    # Generate email verification token
    verification_token = generate_reset_token()
    
    # Create user
    user = User(
        email=data.email,
        password_hash=hash_password(data.password),
        email_verification_token=verification_token,
        is_active=True,
    )
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Send verification email
    EmailService.send_verification_email(user.email, verification_token)
    
    return user

@router.post("/login", response_model=Token)
async def login(
    data: UserCreate,
    request: Request,
    db: Session = Depends(get_db),
):
    """Login and receive access and refresh tokens."""
    
    # Rate limiting
    if not await rate_limit(request, max_requests=5, window_seconds=300):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many login attempts. Please try again later."
        )
    
    # Find user
    user = db.query(User).filter(User.email == data.email).first()
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )
    
    # Create tokens
    access_token = create_access_token(subject=user.email)
    refresh_token = create_refresh_token(subject=user.email)
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

@router.post("/refresh", response_model=AccessToken)
async def refresh_access_token(
    data: RefreshTokenRequest,
    db: Session = Depends(get_db),
):
    """Get a new access token using a refresh token."""
    try:
        payload = verify_token(data.refresh_token, token_type="refresh")
        email = payload.get("sub")
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    
    # Verify user still exists
    user = db.query(User).filter(User.email == email).first()
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive"
        )
    
    # Create new access token
    access_token = create_access_token(subject=email)
    
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }

@router.post("/forgot-password")
async def forgot_password(
    data: ForgotPasswordRequest,
    db: Session = Depends(get_db),
):
    """Request password reset email."""
    
    # Rate limiting (max 3 attempts per email in 10 minutes)
    if not await rate_limit_by_email(data.email, max_requests=3, window_seconds=600):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many password reset attempts. Please try again later."
        )
    
    user = db.query(User).filter(User.email == data.email).first()
    
    # Always return success to prevent email enumeration
    if not user:
        return {"message": "If email exists, reset link will be sent"}
    
    # Generate reset token
    reset_token = generate_reset_token()
    expires = datetime.utcnow() + timedelta(hours=24)
    
    user.password_reset_token = reset_token
    user.password_reset_token_expires = expires
    
    db.commit()
    
    # Send reset email
    EmailService.send_password_reset_email(user.email, reset_token)
    
    return {"message": "If email exists, reset link will be sent"}

@router.post("/reset-password")
async def reset_password(
    data: ResetPasswordRequest,
    db: Session = Depends(get_db),
):
    """Reset password using reset token."""
    
    # Find user by reset token
    user = db.query(User).filter(
        User.password_reset_token == data.token
    ).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid reset token"
        )
    
    # Check if token expired
    if user.password_reset_token_expires < datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Reset token expired"
        )
    
    # Validate new password
    is_valid, error = validate_password(data.new_password)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error
        )
    
    # Update password
    user.password_hash = hash_password(data.new_password)
    user.password_reset_token = None
    user.password_reset_token_expires = None
    
    db.commit()
    
    return {"message": "Password reset successfully"}

@router.post("/verify-email")
async def verify_email(
    data: VerifyEmailRequest,
    db: Session = Depends(get_db),
):
    """Verify email address."""
    
    user = db.query(User).filter(
        User.email_verification_token == data.token
    ).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid verification token"
        )
    
    # Mark email as verified
    user.is_email_verified = True
    user.email_verification_token = None
    
    db.commit()
    db.refresh(user)
    
    return {"message": "Email verified successfully", "user": user}

@router.get("/me", response_model=UserOut)
async def get_current_user_info(
    current_user: User = Depends(get_current_user),
):
    """Get current user info."""
    return current_user