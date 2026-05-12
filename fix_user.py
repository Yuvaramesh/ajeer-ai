"""
fix_corrupted_names.py — One-time migration to fix users whose `name`
field was accidentally saved as a currency name (e.g. "UAE Dirham").

Run once: python fix_corrupted_names.py
"""

from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()
MONGO_URI = os.environ.get("MONGO_URI", "mongodb://localhost:27017/ajeer_db")

CURRENCY_NAMES = {
    "US Dollar",
    "Indian Rupee",
    "British Pound",
    "Euro",
    "Japanese Yen",
    "Chinese Yuan",
    "Canadian Dollar",
    "Australian Dollar",
    "Brazilian Real",
    "Mexican Peso",
    "South African Rand",
    "Nigerian Naira",
    "Saudi Riyal",
    "UAE Dirham",
    "Singapore Dollar",
    "South Korean Won",
    "Russian Ruble",
    "Swiss Franc",
    "Pakistani Rupee",
    "Bangladeshi Taka",
    "Indonesian Rupiah",
    "Malaysian Ringgit",
    "Philippine Peso",
    "Thai Baht",
    "Turkish Lira",
    "Egyptian Pound",
    "Argentine Peso",
}

client = MongoClient(MONGO_URI)
db = client["ajeer_db"]

corrupted = list(db.users.find({"name": {"$in": list(CURRENCY_NAMES)}}))

if not corrupted:
    print("✅ No corrupted records found.")
else:
    print(f"Found {len(corrupted)} corrupted user(s):")
    for u in corrupted:
        print(
            f"  - {u['email']}  name='{u['name']}'  currency_name='{u.get('currency_name')}'"
        )

    confirm = input("\nFix these by setting name to email prefix? (yes/no): ")
    if confirm.strip().lower() == "yes":
        for u in corrupted:
            # Use the part before @ as a placeholder name
            placeholder = u["email"].split("@")[0].replace(".", " ").title()
            db.users.update_one({"_id": u["_id"]}, {"$set": {"name": placeholder}})
            print(f"  ✓ Fixed {u['email']} → name set to '{placeholder}'")
        print(
            "\n✅ Done. Ask affected users to update their display name in profile settings."
        )
    else:
        print("Aborted.")

client.close()
