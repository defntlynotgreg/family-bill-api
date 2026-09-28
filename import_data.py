import csv
import requests

# This targets your live production server
API_URL = "https://family-bill-api.onrender.com/bills/add"

# Open the CSV file you just saved
with open('data.csv', mode='r') as file:
    csv_reader = csv.DictReader(file)

    for row in csv_reader:
        # Package the row data into the JSON format your API expects
        payload = {
            "month": row["Month"].strip(),
            "year": int(row["Year"]),
            "rent_and_water": float(row["Rent"]),
            "electricity": float(row["Electricity"]),
            "internet": float(row["Internet"])
        }

        print(f"Uploading {payload['month']} {payload['year']}...")

        # Send it to your API
        response = requests.post(API_URL, json=payload)

        if response.status_code == 200:
            print("✓ Success")
        else:
            print(f"✕ Failed: {response.text}")