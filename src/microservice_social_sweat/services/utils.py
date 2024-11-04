from fastapi import HTTPException, Request


def verify_user_id_is_the_same_from_jwt(request: Request, user_id: str) -> None:
    if not user_id == request.state.user_id:
        raise HTTPException(
            status_code=401,
            detail="Received JWT Token is not from the user id received to peform this action!",
        )
