from datetime import timedelta
from typing import Annotated
from fastapi import Depends, APIRouter, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from utils.utils import verify_password
from utils.utils import get_current_user, create_access_token
from schemas import Token, UserIn, ReturnMessage
from sqlmodel import select
from models import User
from utils.utils import get_current_user, get_user, get_password_hash, add_user, ACCESS_TOKEN_EXPIRE_HOURS, verify_password
from db import session_dependency

auth_router = APIRouter(prefix='/api/auth', tags=['auth'])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def authenticate_user(username: str, password: str, session: session_dependency) -> bool | User:
    """
    Authenticate a user by username and password.

    Args:
    username (str): The username of the user.
    password (str): The password of the user.

    Returns:
    bool | User: The authenticated user or False if authentication fails.
    """
    user = get_user(username, session=session)
    print(user)
    if not user:
        return False
    if not verify_password(password, user.password):
        return False
    return user

@auth_router.post("/register")
async def register_user(user: UserIn, session: session_dependency) -> ReturnMessage:
    """
    Register a new user.

    Args:
    user (UserIn): The user data for registration.

    Returns:
    ReturnMessage: A message indicating the success of the registration.
    """
    if get_user(user.username, session = session):
        raise HTTPException(status_code=400, detail="Username already registered")
    user.password = get_password_hash(user.password)
    if user.budget is None:
        user.budget = 0
    new_user = add_user(user, session=session)
    return ReturnMessage(success=True, message="User registered successfully", payload=new_user.model_dump())

@auth_router.post("/token")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: session_dependency
) -> Token:
    """
    Log in a user and provide an access token.

    Args:
    form_data (OAuth2PasswordRequestForm): The form data containing username and password.

    Returns:
    Token: The access token for the authenticated user.
    """
    user = authenticate_user(form_data.username, form_data.password, session=session)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")

@auth_router.get("/users/me", response_model=User)
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_user)],
):
    """
    Retrieve the current authenticated user.

    Args:
    current_user (User): The current authenticated user.

    Returns:
    User: The current user.
    """
    return current_user

@auth_router.get("/users/{user_id}", response_model=User)
async def read_user_by_id(user_id: int, session: session_dependency ,current_user: Annotated[User, Depends(get_current_user)]):
    """
    Retrieve a user by ID.

    Args:
    user_id (int): The ID of the user to retrieve.
    current_user (User): The current authenticated user.

    Returns:
    User: The user with the specified ID.
    """
    if current_user.id != user_id:
        raise HTTPException(status_code=400, detail="You are not authorized to view this user")
    return session.get(User, user_id)

@auth_router.delete("/users/{user_id}")
async def delete_user(user_id: int, session: session_dependency,current_user: Annotated[User, Depends(get_current_user)]):
    """
    Delete a user by ID.

    Args:
    user_id (int): The ID of the user to delete.
    current_user (User): The current authenticated user.

    Returns:
    ReturnMessage: A message indicating the success of the deletion.
    """
    if current_user.id != user_id:
        raise HTTPException(status_code=400, detail="You are not authorized to delete this user")
    session.delete(session.get(User, user_id))
    session.commit()
    return ReturnMessage(success=True, message="User deleted successfully", payload=None)


#temporary endpoints
#just to see all users for now

@auth_router.get("/users")
async def get_users(session: session_dependency):
    """
    Retrieve all users.

    Args:
    current_user (User): The current authenticated user.

    Returns:
    list[User]: A list of all users.
    """
    return session.exec(select(User)).all()
