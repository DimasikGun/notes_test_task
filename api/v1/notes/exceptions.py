from fastapi import HTTPException, status

from api.utils import validation_error

note_not_found_exc = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail=validation_error(
        loc=["query", "{note_id}"],
        msg="Note not found",
        reason="Note with provided id not found",
    )["detail"],
)

invalid_upd_found_exc = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail=validation_error(
        loc=["body", "title", "text"],
        msg="Invalid update input",
        reason="Update input is empty or same as original data",
    )["detail"],
)
