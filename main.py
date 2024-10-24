from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel, EmailStr
from motor.motor_asyncio import AsyncIOMotorClient
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from bson.objectid import ObjectId
import os
import uuid

# FastAPI instance
app = FastAPI()

# MongoDB connection
client = AsyncIOMotorClient("mongodb://localhost:27017")
db = client["test_db"]
users_collection = db["users"]

# Secret key and algorithm for JWT
SECRET_KEY = "your_secret_key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# Pydantic models for user registration and login
class UserRegister(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    username: str
    password: str


# Utility function to hash password
def hash_password(password: str):
    return pwd_context.hash(password)


# Utility function to verify password
def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)


# JWT token creation
def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (
        expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


# Registration route
@app.post("/register")
async def register_user(user: UserRegister):
    # Check if user already exists
    existing_user = await users_collection.find_one({"username": user.username})
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists")

    # Hash the password and save the user
    hashed_password = hash_password(user.password)
    user_dict = {
        "username": user.username,
        "email": user.email,
        "hashed_password": hashed_password,
    }
    await users_collection.insert_one(user_dict)
    return {"message": "User registered successfully"}


# Login route
@app.post("/login")
async def login_user(user: UserLogin):
    # Find the user in the database
    db_user = await users_collection.find_one({"username": user.username})
    if not db_user:
        raise HTTPException(status_code=400, detail="Invalid username or password")

    # Verify the password
    if not verify_password(user.password, db_user["hashed_password"]):
        raise HTTPException(status_code=400, detail="Invalid username or password")

    # Create JWT token
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}


# Run the app with: uvicorn main:app --reload

user_history = {}


# Endpoint to scan food using AI
@app.post("/scan-food/")
async def scan_food(file: UploadFile = File(...)):
    # Save the uploaded file temporarily
    temp_filename = f"temp_{uuid.uuid4()}.jpg"
    with open(temp_filename, "wb") as f:
        f.write(await file.read())

    # Run analysis on the image using Llama AI
    result = 'Result'
    # Clean up temp file
    os.remove(temp_filename)

    return {"result": result}


# Endpoint to get user scan history
@app.get("/get-history/")
async def get_history(user_id: str):
    return {"history": user_history.get(user_id, [])}


# Endpoint to manually add a food report
class Report(BaseModel):
    user_id: str
    product_name: str
    issue: str
    details: str


@app.post("/add-report/")
async def add_report(report: Report):
    user_reports = user_history.get(report.user_id, [])
    user_reports.append(report.dict())
    user_history[report.user_id] = user_reports
    return {"message": "Report added successfully"}


# Endpoint to get notifications for unsafe food
@app.get("/get-notifications/")
async def get_notifications(user_id: str):
    # Placeholder: You would fetch notifications from a database or an alerting system
    return {
        "notifications": ["Milk from Brand X is adulterated", "Bread expires in 2 days"]
    }
