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

@app.delete("/bills/delete")
async def delete_bill(request: Request):
    try:
        data = await request.json()
        month = data.get("month")
        year = data.get("year")
        
        # Find the specific bill in the database
        docs = db.collection("bills").where("month", "==", month).where("year", "==", year).stream()
        for doc in docs:
            db.collection("bills").document(doc.id).delete()
            
        return {"status": "Success", "message": "Bill deleted"}
    except Exception as e:
        return {"status": "Error", "message": str(e)}

@app.put("/bills/edit")
async def edit_bill(request: Request):
    try:
        data = await request.json()
        month = data.get("month")
        year = data.get("year")
        rent = float(data.get("rent_and_water"))
        elec = float(data.get("electricity"))
        internet = float(data.get("internet"))
        
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
        for doc in docs:
            db.collection("bills").document(doc.id).update({
                "payables": payables,
                "totalDue": total,
                "contributionPerHead": per_head
            })
            
        return {"status": "Success", "message": "Bill updated"}
    except Exception as e:
        return {"status": "Error", "message": str(e)}