from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import jwt, JWTError
from passlib.context import CryptContext
from datetime import datetime, timedelta
from .models import User, TokenData
from .database import db
import os

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")
pwd_context = CryptContext(schemes=["bcrypt"])
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")

def create_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(hours=1)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload.get("sub")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

@router.post("/register")
async def register(user: User):
    user_exists = await db.users.find_one({"username": user.username})
    if user_exists:
        raise HTTPException(status_code=400, detail="User exists")
    hashed_pw = pwd_context.hash(user.password)
    await db.users.insert_one({"username": user.username, "password": hashed_pw})
    return {"msg": "User created"}

@router.post("/login")
async def login(form: OAuth2PasswordRequestForm = Depends()):
    user = await db.users.find_one({"username": form.username})
    if not user or not pwd_context.verify(form.password, user["password"]):
        raise HTTPException(status_code=400, detail="Invalid credentials")
    token = create_token({"sub": form.username})
    return {"access_token": token, "token_type": "bearer"}
