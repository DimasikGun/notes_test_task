from fastapi import HTTPException, status

from api.utils import validation_error

invalid_token_exc = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail=validation_error(
        loc=["header", "Authorization"],
        msg="Invalid token",
        reason="Token is expired, malformed or you provided a token with invalid type",
    )["detail"],
)

unauthed_exc = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail=validation_error(
        loc=["body", "username", "password"],
        msg="Invalid username or password",
        reason="Username or password is incorrect",
    )["detail"],
)

username_taken_exc = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail=validation_error(
        loc=["body", "username"],
        msg="Username taken",
        reason="This username is already taken",
    )["detail"],
)


user_not_found_exc = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail=validation_error(
        loc=["header", "Authorization"],
        msg="User not found",
        reason="No user with the provided ID exists",
    )["detail"],
)
