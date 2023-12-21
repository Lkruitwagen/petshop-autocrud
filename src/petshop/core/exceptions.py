from fastapi import HTTPException, status

class NotFoundError(Exception):
    pass


def handler(e: Exception):
    if isinstance(e, NotFoundError):
        return HTTPException(
            status_code=404,
            detail=f"Resource not found.",
        )
    else:
        return HTTPException(
            status_code=500,
            detail=str(e)
        )