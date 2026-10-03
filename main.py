from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config.firebase import db
from routers import bills

app = FastAPI(title="Family Bill Tracker API")

# Allow your React frontend (and Vercel previews) to communicate with this backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://family-bill-ui.vercel.app"], 
    allow_origin_regex=r"https://.*\.vercel\.app", # Safely allows temporary Vercel preview links
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(bills.router)

@app.get("/")
def read_root():
    return {"message": "Server is running successfully"}

@app.post("/bills/delete")
async def delete_bill(data: dict):
    try:
        month = data.get("month")
        year = data.get("year")
        
        # Find the specific bill in the database
        docs = db.collection("bills").where("month", "==", month).where("year", "==", year).stream()
        for doc in docs:
            db.collection("bills").document(doc.id).delete()
            
        return {"status": "Success", "message": "Bill deleted"}
    except Exception as e:
        return {"status": "Error", "message": str(e)}

@app.post("/bills/edit")
async def edit_bill(data: dict):
    try:
        month = data.get("month")
        year = data.get("year")
        
        # Safely fall back to 0.0 if the data is missing to prevent math crashes
        rent = float(data.get("rent_and_water") or 0.0)
        elec = float(data.get("electricity") or 0.0)
        internet = float(data.get("internet") or 0.0)
        
        # Recalculate the math
        total = round(rent + elec + internet, 2)
        per_head = round(total / 3, 2)
        
        payables = {
            "Lola Flor (Rent & Water)": rent,
            "Meralco (Electricity)": elec,
            "Converge (Internet)": internet
        }
        
        # Overwrite the existing document
        docs = db.collection("bills").where("month", "==", month).where("year", "==", year).stream()
        updated = False
        
        for doc in docs:
            db.collection("bills").document(doc.id).update({
                "payables": payables,
                "totalDue": total,
                "contributionPerHead": per_head
            })
            updated = True
            
        if not updated:
            return {"status": "Error", "message": "Bill not found in database."}
            
        return {"status": "Success", "message": "Bill updated"}
    except Exception as e:
        return {"status": "Error", "message": f"Server crash: {str(e)}"}