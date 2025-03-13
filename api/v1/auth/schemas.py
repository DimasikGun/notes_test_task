import re

from pydantic import BaseModel, Field, field_validator


class BaseUser(BaseModel):
    username: str = Field(min_length=2, max_length=150)


class UserSchema(BaseUser):
    password: str = Field()

    @field_validator("password")
    def validate_password(cls, v):
        if not re.fullmatch(r"^(?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?=.*\W).{8,64}$", v):
            raise ValueError(
                "Password must contain at least one number, "
                "lowercase and uppercase letters, "
                "a special character, and be between 8 and 64 characters long."
            )
        return v


class Token(BaseModel):
    access_token: str
    refresh_token: str | None = None
    token_type: str = "Bearer"
