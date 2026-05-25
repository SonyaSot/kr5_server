from __future__ import annotations
from fastapi import APIRouter, Depends, HTTPException
from app.schemas import UserOut
from app.dependencies import get_current_user

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserOut)
def get_me(user: UserOut = Depends(get_current_user)) -> UserOut:
    return user


@router.get("/{user_id}", response_model=UserOut)
def get_user(user_id: int, user: UserOut = Depends(get_current_user)) -> UserOut:
    # In a real app you'd look up the user; here we just return current user's info
    # or 404 if they request someone else's profile (simplified)
    if user_id != user.id:
        raise HTTPException(status_code=404, detail="User not found")
    return user
