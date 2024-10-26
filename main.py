from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel, EmailStr
from motor.motor_asyncio import AsyncIOMotorClient
from bson.objectid import ObjectId
import os
import uuid

# FastAPI instance
app = FastAPI()

# MongoDB connection
client = AsyncIOMotorClient("mongodb://localhost:27017")
db = client["safebit"]
users_collection = db["users"]

# Password hashing context


# Pydantic models for user registration and login
class UserRegister(BaseModel):
    username: str
    email: EmailStr
    password: str


# Endpoint to scan food using AI
@app.post("/scan-food/")
async def scan_food(file: UploadFile = File(...)):
    # Save the uploaded file temporarily
    temp_filename = f"temp_{uuid.uuid4()}.jpg"
    with open(temp_filename, "wb") as f:
        f.write(await file.read())

    # Run analysis on the image using Llama AI

    result = "Result"
    # Clean up temp file
    os.remove(temp_filename)

    return {"result": result}


# Endpoint to manually add a food report
class Report(BaseModel):
    user_id: str
    product_name: str
    issue: str
    details: str


@app.post("/add-report/")
async def add_report(report: Report):
    return {"report": report}




