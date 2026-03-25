from pydantic import BaseModel, EmailStr, field_validator

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    
    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, v):
        from app.core.security import validate_password
        is_valid, error = validate_password(v)
        if not is_valid:
            raise ValueError(error)
        return v

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class AccessToken(BaseModel):
    access_token: str
    token_type: str = "bearer"

class RefreshTokenRequest(BaseModel):
    refresh_token: str

class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str
    
    @field_validator("new_password")
    @classmethod
    def validate_password_strength(cls, v):
        from app.core.security import validate_password
        is_valid, error = validate_password(v)
        if not is_valid:
            raise ValueError(error)
        return v

class VerifyEmailRequest(BaseModel):
    token: str

class UserOut(BaseModel):
    id: int
    email: str
    is_email_verified: bool
    
    class Config:
        from_attributes = True