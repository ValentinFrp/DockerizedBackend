from datetime import datetime
from typing import List, Optional

import uvicorn
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, EmailStr, Field

app = FastAPI(
    title="User Management API",
    description="API de gestion d'utilisateurs pour démonstration CI/CD",
    version="1.0.0",
)


class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    full_name: Optional[str] = None


class UserCreate(UserBase):
    password: str = Field(..., min_length=8)


class User(UserBase):
    id: int
    is_active: bool = True
    created_at: datetime

    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "username": "johndoe",
                "email": "john@example.com",
                "full_name": "John Doe",
                "is_active": True,
                "created_at": "2024-01-01T12:00:00",
            }
        }


class HealthCheck(BaseModel):
    status: str
    version: str
    timestamp: datetime


users_db: List[User] = []
user_id_counter = 1


@app.get("/", response_model=dict)
async def root():
    return {
        "message": "Welcome to User Management API",
        "docs": "/docs",
        "health": "/health",
    }


@app.get("/health", response_model=HealthCheck)
async def health_check():
    return HealthCheck(
        status="healthy",
        version="1.0.0",
        timestamp=datetime.now(),
    )


@app.post("/users", response_model=User, status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreate):
    global user_id_counter

    if any(u.username == user.username for u in users_db):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Username '{user.username}' already exists",
        )

    if any(u.email == user.email for u in users_db):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Email '{user.email}' already exists",
        )

    new_user = User(
        id=user_id_counter,
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        is_active=True,
        created_at=datetime.now(),
    )

    users_db.append(new_user)
    user_id_counter += 1

    return new_user


@app.get("/users", response_model=List[User])
async def list_users(skip: int = 0, limit: int = 100):
    return users_db[skip : skip + limit]


@app.get("/users/{user_id}", response_model=User)
async def get_user(user_id: int):
    user = next((u for u in users_db if u.id == user_id), None)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} not found",
        )

    return user


@app.put("/users/{user_id}", response_model=User)
async def update_user(user_id: int, user_update: UserBase):
    user = next((u for u in users_db if u.id == user_id), None)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} not found",
        )

    if any(u.username == user_update.username and u.id != user_id for u in users_db):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Username '{user_update.username}' already exists",
        )

    if any(u.email == user_update.email and u.id != user_id for u in users_db):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Email '{user_update.email}' already exists",
        )

    user.username = user_update.username
    user.email = user_update.email
    user.full_name = user_update.full_name

    return user


@app.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: int):
    global users_db

    user = next((u for u in users_db if u.id == user_id), None)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} not found",
        )

    users_db = [u for u in users_db if u.id != user_id]


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
