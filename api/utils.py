def validation_error(loc: list[str], msg: str, input_value=None, reason=None) -> dict:
    """Returns detail for HttpException in OpenApi format"""
    error = {
        "type": "value_error",
        "loc": loc,
        "msg": msg,
    }
    if input_value:
        error["input"] = input_value
    if reason:
        error["ctx"] = {"reason": reason}
    return {"detail": [error]}
