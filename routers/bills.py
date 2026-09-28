from fastapi import APIRouter
from pydantic import BaseModel
from config.firebase import db

# Create a router specifically for bill-related endpoints
router = APIRouter(prefix="/bills", tags=["Bills"])

# Define the exact data structure we expect when adding a new month
class MonthlyBill(BaseModel):
    month: str
    year: int
    rent_and_water: float  # Lola Flor
    electricity: float     # Meralco
    internet: float        # Converge

@router.post("/add")
def add_new_bill(bill: MonthlyBill):
    # Calculate the totals based on your Excel sheet logic
    total_due = bill.rent_and_water + bill.electricity + bill.internet
    per_head = total_due / 3

    # Create a clean document ID (e.g., "2024-september")
    doc_id = f"{bill.year}-{bill.month.lower()}"
    doc_ref = db.collection("monthly_bills").document(doc_id)
    
    # Structure the data for Firestore
    bill_data = {
        "month": bill.month,
        "year": bill.year,
        "payables": {
            "Lola Flor (Rent & Water)": bill.rent_and_water,
            "Meralco (Electricity)": bill.electricity,
            "Converge (Internet)": bill.internet
        },
        "totalDue": round(total_due, 2),
        "contributionPerHead": round(per_head, 2),
        "paymentStatus": {
            "me": False,
            "sister": False,
            "cousin": False
        }
    }
    
    # Save to database
    doc_ref.set(bill_data)
    return {"status": "Success", "message": f"Bill for {bill.month} {bill.year} added.", "data": bill_data}

# Add this new data model right below your existing MonthlyBill class
class PaymentUpdate(BaseModel):
    month: str
    year: int
    person: str  # Must be "me", "sister", or "cousin"
    has_paid: bool

# ... (keep your existing @router.post("/add") code here) ...

@router.get("/all")
def get_all_bills():
    bills_list = []
    # Fetch all documents from the monthly_bills collection
    docs = db.collection("monthly_bills").stream()
    
    for doc in docs:
        bill_data = doc.to_dict()
        bill_data["id"] = doc.id # Keep the document ID attached
        bills_list.append(bill_data)
        
    return {"status": "Success", "data": bills_list}

@router.patch("/update-payment")
def update_payment(update: PaymentUpdate):
    # Recreate the document ID (e.g., "2024-september")
    doc_id = f"{update.year}-{update.month.lower()}"
    doc_ref = db.collection("monthly_bills").document(doc_id)
    
    # Update only the specific person's payment boolean
    doc_ref.update({
        f"paymentStatus.{update.person.lower()}": update.has_paid
    })
    
    return {
        "status": "Success", 
        "message": f"Payment status for {update.person} updated to {update.has_paid}."
    }