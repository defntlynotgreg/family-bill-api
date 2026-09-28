from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config.firebase import db
from routers import bills

app = FastAPI(title="Family Bill Tracker API")

# Allow your future React frontend to communicate with this backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://family-bill-ui.vercel.app"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(bills.router)

@app.get("/")
def read_root():
    return {"message": "Server is running successfully"}