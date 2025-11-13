import os
from datetime import datetime
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional

from database import db, create_document, get_documents
from schemas import User, Vehicle, Booking, Otp, SupportMessage

app = FastAPI(title="Flames.Blue API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"name": "Flames.Blue API", "status": "ok"}

@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set",
        "database_name": "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set",
        "connection_status": "Not Connected",
        "collections": []
    }
    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["connection_status"] = "Connected"
            try:
                response["collections"] = db.list_collection_names()
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️ Connected but error: {str(e)[:80]}"
        else:
            response["database"] = "⚠️ Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:80]}"
    return response

# ---------------------- Auth (OTP) ----------------------
class SendOtpRequest(BaseModel):
    phone: str

class VerifyOtpRequest(BaseModel):
    phone: str
    code: str

@app.post("/auth/send-otp")
def send_otp(payload: SendOtpRequest):
    import random
    code = f"{random.randint(100000, 999999)}"
    create_document("otp", {"phone": payload.phone, "code": code, "created_at": datetime.utcnow()})
    # In real life we'd send SMS; for demo, return code
    return {"status": "sent", "code": code}

@app.post("/auth/verify-otp")
def verify_otp(payload: VerifyOtpRequest):
    records = db["otp"].find({"phone": payload.phone}).sort("created_at", -1).limit(1)
    rec = next(records, None)
    if not rec or rec.get("code") != payload.code:
        raise HTTPException(status_code=400, detail="Invalid OTP")
    # Upsert user
    existing = db["user"].find_one({"phone": payload.phone})
    if not existing:
        create_document("user", {"phone": payload.phone, "created_at": datetime.utcnow()})
    return {"status": "verified"}

# ---------------------- Vehicles ----------------------
@app.post("/vehicles")
def create_vehicle(vehicle: Vehicle):
    vid = create_document("vehicle", vehicle)
    return {"id": vid}

@app.get("/vehicles")
def list_vehicles():
    items = get_documents("vehicle")
    # Convert ObjectId to str
    for it in items:
        it["_id"] = str(it["_id"]) if "_id" in it else None
    return items

# ---------------------- Bookings ----------------------
@app.post("/bookings")
def create_booking(booking: Booking):
    bid = create_document("booking", booking)
    return {"id": bid}

@app.get("/bookings")

def list_bookings():
    items = get_documents("booking")
    for it in items:
        it["_id"] = str(it["_id"]) if "_id" in it else None
    return items

# ---------------------- Support Chat ----------------------
class ChatMessage(BaseModel):
    user_id: str
    message: str

@app.post("/support/chat")

def support_chat(msg: ChatMessage):
    # Save user message
    create_document("supportmessage", {"user_id": msg.user_id, "role": "user", "message": msg.message, "created_at": datetime.utcnow()})
    # Simple friendly bot reply
    reply = "Thanks! A support specialist will reach out shortly. Meanwhile, can I help you with bookings or vehicle listings?"
    create_document("supportmessage", {"user_id": msg.user_id, "role": "bot", "message": reply, "created_at": datetime.utcnow()})
    return {"reply": reply}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
