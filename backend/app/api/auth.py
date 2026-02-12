from datetime import timedelta
import json
import sys
import traceback

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.auth import (
    Token,
    UserCreate,
    UserLogin,
    UserResponse,
    authenticate_user,
    create_access_token,
    get_current_user,
    get_password_hash,
    get_user_by_email,
)
from app.core.config import settings
from app.core.database import get_db
from app.models.user import User

router = APIRouter(prefix="/auth", tags=["auth"])

# #region agent log
def _debug_log(hypothesis_id: str, location: str, message: str, data: dict = None):
    """Write debug log to stdout for docker logs visibility."""
    import time
    log_entry = {
        "hypothesisId": hypothesis_id,
        "location": location,
        "message": message,
        "data": data or {},
        "timestamp": int(time.time() * 1000),
    }
    print(f"[DEBUG_REG] {json.dumps(log_entry)}", file=sys.stderr, flush=True)
# #endregion


@router.post("/register", response_model=UserResponse)
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    # #region agent log
    _debug_log("A", "auth.py:register:entry", "Register called", {"email": user_data.email, "name": user_data.name})
    # #endregion

    try:
        existing_user = get_user_by_email(db, user_data.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )

        # #region agent log
        _debug_log("B", "auth.py:register:before_hash", "About to hash password")
        # #endregion
        hashed_password = get_password_hash(user_data.password)
        # #region agent log
        _debug_log("B", "auth.py:register:after_hash", "Password hashed successfully")
        # #endregion

        db_user = User(
            email=user_data.email,
            hashed_password=hashed_password,
            name=user_data.name
        )
        # #region agent log
        _debug_log("A", "auth.py:register:before_add", "About to db.add")
        # #endregion
        db.add(db_user)

        # #region agent log
        _debug_log("A,E", "auth.py:register:before_commit", "About to db.commit")
        # #endregion
        db.commit()

        # #region agent log
        _debug_log("C", "auth.py:register:before_refresh", "About to db.refresh")
        # #endregion
        db.refresh(db_user)

        # #region agent log
        _debug_log("C,D", "auth.py:register:after_refresh", "Refresh done, about to return", {
            "user_id": db_user.id,
            "email": db_user.email,
            "name": db_user.name,
            "is_active": db_user.is_active,
            "created_at": str(db_user.created_at) if db_user.created_at else None,
        })
        # #endregion

        # #region agent log
        _debug_log("D", "auth.py:register:returning", "Returning db_user to FastAPI for serialization")
        # #endregion
        return db_user

    except HTTPException:
        raise
    except Exception as e:
        # #region agent log
        _debug_log("ALL", "auth.py:register:unhandled_error", "Unhandled exception in register", {
            "error": str(e),
            "error_type": type(e).__name__,
            "traceback": traceback.format_exc(),
        })
        # #endregion
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {type(e).__name__}: {str(e)}"
        )


@router.post("/login", response_model=Token)
async def login(user_data: UserLogin, db: Session = Depends(get_db)):
    user = authenticate_user(db, user_data.email, user_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user


@router.put("/me", response_model=UserResponse)
async def update_me(
    name: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    current_user.name = name
    db.commit()
    db.refresh(current_user)
    return current_user
