"""
init_db.py — Initialize MongoDB collections and indexes for Ajeer
Run once: python init_db.py
"""

from pymongo import MongoClient, ASCENDING
from werkzeug.security import generate_password_hash
from datetime import datetime
import os

MONGO_URI = os.environ.get("MONGO_URI", "mongodb://localhost:27017/ajeer_db")

client = MongoClient(MONGO_URI)
db = client.get_database()


def init():
    print("Initializing Ajeer MongoDB...")

    # Indexes
    db.users.create_index([("email", ASCENDING)], unique=True)
    db.jobs.create_index([("status", ASCENDING), ("created_at", ASCENDING)])
    db.tasks.create_index([("status", ASCENDING)])
    db.chat_logs.create_index([("user_id", ASCENDING), ("timestamp", ASCENDING)])
    db.login_logs.create_index([("user_id", ASCENDING)])
    print("✓ Indexes created")

    # Seed admin user
    if not db.users.find_one({"email": "admin@ajeer.com"}):
        db.users.insert_one(
            {
                "name": "Ajeer Admin",
                "email": "admin@ajeer.com",
                "password": generate_password_hash("admin123"),
                "country": "UAE",
                "currency_code": "AED",
                "currency_symbol": "د.إ",
                "currency_name": "UAE Dirham",
                "role": "admin",
                "created_at": datetime.utcnow(),
            }
        )
        print("✓ Admin user seeded: admin@ajeer.com / admin123")

    # Seed sample jobs
    if db.jobs.count_documents({}) == 0:
        jobs = [
            {
                "title": "Construction Foreman",
                "category": "Construction",
                "location": "Dubai",
                "salary_usd": 1800,
                "status": "active",
                "created_at": datetime.utcnow(),
            },
            {
                "title": "Nurse (ICU)",
                "category": "Healthcare",
                "location": "Riyadh",
                "salary_usd": 2200,
                "status": "active",
                "created_at": datetime.utcnow(),
            },
            {
                "title": "Hotel Receptionist",
                "category": "Hospitality",
                "location": "Abu Dhabi",
                "salary_usd": 900,
                "status": "active",
                "created_at": datetime.utcnow(),
            },
            {
                "title": "Electrician",
                "category": "Trades",
                "location": "Doha",
                "salary_usd": 1500,
                "status": "active",
                "created_at": datetime.utcnow(),
            },
            {
                "title": "Driver (Heavy Vehicle)",
                "category": "Transportation",
                "location": "Kuwait City",
                "salary_usd": 1100,
                "status": "active",
                "created_at": datetime.utcnow(),
            },
        ]
        db.jobs.insert_many(jobs)
        print(f"✓ Seeded {len(jobs)} sample jobs")

    # Seed sample tasks
    if db.tasks.count_documents({}) == 0:
        tasks = [
            {
                "title": "Install scaffolding",
                "status": "completed",
                "created_at": datetime.utcnow(),
            },
            {
                "title": "Patient ward rounds",
                "status": "completed",
                "created_at": datetime.utcnow(),
            },
            {
                "title": "Hotel check-in management",
                "status": "active",
                "created_at": datetime.utcnow(),
            },
        ]
        db.tasks.insert_many(tasks)
        print(f"✓ Seeded {len(tasks)} sample tasks")

    print("\n✅ Database initialization complete!")
    print(f"   DB: {db.name}")
    print(f"   Collections: {db.list_collection_names()}")

    client.close()


if __name__ == "__main__":
    init()
