
from fastapi import FastAPI
from app import auth, chat

app = FastAPI()
app.include_router(auth.router)
app.include_router(chat.router)
@app.get("/")
def root():
    return {"message": "Backend is working!"}
