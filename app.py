from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_pymongo import PyMongo
from werkzeug.security import generate_password_hash, check_password_hash
import google.generativeai as genai
import requests
import os
from datetime import datetime
from functools import wraps
from bson import ObjectId

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "ajeer-secret-key-2024")

app.config["MONGO_URI"] = os.environ.get(
    "MONGO_URI", "mongodb://localhost:27017/ajeer_db"
)
mongo = PyMongo(app)

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "your-gemini-api-key")
genai.configure(api_key=GEMINI_API_KEY)
gemini_model = genai.GenerativeModel("gemini-2.5-flash-lite")

COUNTRY_CURRENCY_MAP = {
    "United States": {"code": "USD", "symbol": "$", "name": "US Dollar"},
    "India": {"code": "INR", "symbol": "₹", "name": "Indian Rupee"},
    "United Kingdom": {"code": "GBP", "symbol": "£", "name": "British Pound"},
    "European Union": {"code": "EUR", "symbol": "€", "name": "Euro"},
    "Germany": {"code": "EUR", "symbol": "€", "name": "Euro"},
    "France": {"code": "EUR", "symbol": "€", "name": "Euro"},
    "Japan": {"code": "JPY", "symbol": "¥", "name": "Japanese Yen"},
    "China": {"code": "CNY", "symbol": "¥", "name": "Chinese Yuan"},
    "Canada": {"code": "CAD", "symbol": "CA$", "name": "Canadian Dollar"},
    "Australia": {"code": "AUD", "symbol": "A$", "name": "Australian Dollar"},
    "Brazil": {"code": "BRL", "symbol": "R$", "name": "Brazilian Real"},
    "Mexico": {"code": "MXN", "symbol": "MX$", "name": "Mexican Peso"},
    "South Africa": {"code": "ZAR", "symbol": "R", "name": "South African Rand"},
    "Nigeria": {"code": "NGN", "symbol": "₦", "name": "Nigerian Naira"},
    "Saudi Arabia": {"code": "SAR", "symbol": "﷼", "name": "Saudi Riyal"},
    "UAE": {"code": "AED", "symbol": "د.إ", "name": "UAE Dirham"},
    "Singapore": {"code": "SGD", "symbol": "S$", "name": "Singapore Dollar"},
    "South Korea": {"code": "KRW", "symbol": "₩", "name": "South Korean Won"},
    "Russia": {"code": "RUB", "symbol": "₽", "name": "Russian Ruble"},
    "Switzerland": {"code": "CHF", "symbol": "CHF", "name": "Swiss Franc"},
    "Pakistan": {"code": "PKR", "symbol": "₨", "name": "Pakistani Rupee"},
    "Bangladesh": {"code": "BDT", "symbol": "৳", "name": "Bangladeshi Taka"},
    "Indonesia": {"code": "IDR", "symbol": "Rp", "name": "Indonesian Rupiah"},
    "Malaysia": {"code": "MYR", "symbol": "RM", "name": "Malaysian Ringgit"},
    "Philippines": {"code": "PHP", "symbol": "₱", "name": "Philippine Peso"},
    "Thailand": {"code": "THB", "symbol": "฿", "name": "Thai Baht"},
    "Turkey": {"code": "TRY", "symbol": "₺", "name": "Turkish Lira"},
    "Egypt": {"code": "EGP", "symbol": "E£", "name": "Egyptian Pound"},
    "Argentina": {"code": "ARS", "symbol": "$", "name": "Argentine Peso"},
    "Other": {"code": "USD", "symbol": "$", "name": "US Dollar"},
}

COUNTRIES = sorted(COUNTRY_CURRENCY_MAP.keys())


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login"))
        return f(*args, **kwargs)

    return decorated_function


def get_exchange_rate(from_currency, to_currency):
    try:
        url = f"https://api.exchangerate-api.com/v4/latest/{from_currency}"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            return data.get("rates", {}).get(to_currency, 1.0)
    except Exception as e:
        print(f"Exchange rate error: {e}")
    fallback = {
        "USD": {"INR": 83.5, "GBP": 0.79, "EUR": 0.92, "AED": 3.67, "SAR": 3.75},
        "INR": {"USD": 0.012, "AED": 0.044, "SAR": 0.045},
    }
    return fallback.get(from_currency, {}).get(to_currency, 1.0)


@app.route("/")
def index():
    if "user_id" in session:
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        country = request.form.get("country", "Other")

        user = mongo.db.users.find_one({"email": email})
        if user and check_password_hash(user["password"], password):
            session["user_id"] = str(user["_id"])
            session["name"] = user.get("name", "User")
            session["email"] = user["email"]
            session["country"] = country
            currency_info = COUNTRY_CURRENCY_MAP.get(
                country, COUNTRY_CURRENCY_MAP["Other"]
            )
            session["currency_code"] = currency_info["code"]
            session["currency_symbol"] = currency_info["symbol"]
            session["currency_name"] = currency_info["name"]

            mongo.db.users.update_one(
                {"_id": user["_id"]},
                {
                    "$set": {
                        "country": country,
                        **currency_info,
                        "last_login": datetime.utcnow(),
                    }
                },
            )
            mongo.db.login_logs.insert_one(
                {
                    "user_id": str(user["_id"]),
                    "email": email,
                    "country": country,
                    "timestamp": datetime.utcnow(),
                    "ip": request.remote_addr,
                }
            )
            return redirect(url_for("dashboard"))
        else:
            error = "Invalid email or password."

    return render_template("login.html", countries=COUNTRIES, error=error)


@app.route("/register", methods=["GET", "POST"])
def register():
    error = None
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        country = request.form.get("country", "Other")

        if mongo.db.users.find_one({"email": email}):
            error = "Email already registered."
        elif len(password) < 6:
            error = "Password must be at least 6 characters."
        else:
            currency_info = COUNTRY_CURRENCY_MAP.get(
                country, COUNTRY_CURRENCY_MAP["Other"]
            )
            mongo.db.users.insert_one(
                {
                    "name": name,
                    "email": email,
                    "password": generate_password_hash(password),
                    "country": country,
                    "currency_code": currency_info["code"],
                    "currency_symbol": currency_info["symbol"],
                    "currency_name": currency_info["name"],
                    "created_at": datetime.utcnow(),
                    "role": "user",
                }
            )
            return redirect(url_for("login"))

    return render_template("register.html", countries=COUNTRIES, error=error)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/dashboard")
@login_required
def dashboard():
    user = mongo.db.users.find_one({"_id": ObjectId(session["user_id"])})
    country = session.get("country", "Other")
    currency_info = COUNTRY_CURRENCY_MAP.get(country, COUNTRY_CURRENCY_MAP["Other"])

    try:
        total_jobs = mongo.db.jobs.count_documents({})
        active_workers = mongo.db.users.count_documents({"role": "worker"})
        completed_tasks = mongo.db.tasks.count_documents({"status": "completed"})
    except Exception:
        total_jobs = active_workers = completed_tasks = 0

    stats = {
        "total_jobs": total_jobs,
        "active_workers": active_workers,
        "completed_tasks": completed_tasks,
        "revenue": 48750,
    }

    return render_template(
        "dashboard.html",
        user=user,
        stats=stats,
        currency=currency_info,
        country=country,
        countries=COUNTRIES,
        now_hour=datetime.now().hour,
    )


@app.route("/chatbot")
@login_required
def chatbot():
    currency_info = COUNTRY_CURRENCY_MAP.get(
        session.get("country", "Other"), COUNTRY_CURRENCY_MAP["Other"]
    )
    return render_template(
        "chatbot.html", currency=currency_info, user_name=session.get("name", "User")
    )


@app.route("/api/currency/convert", methods=["POST"])
@login_required
def convert_currency():
    data = request.get_json()
    amount = float(data.get("amount", 0))
    from_cur = data.get("from", "USD")
    to_cur = data.get("to", "INR")
    rate = get_exchange_rate(from_cur, to_cur)
    return jsonify(
        {
            "success": True,
            "amount": amount,
            "from": from_cur,
            "to": to_cur,
            "rate": rate,
            "converted": round(amount * rate, 2),
        }
    )


@app.route("/api/currency/rates", methods=["GET"])
@login_required
def get_rates():
    base = request.args.get("base", session.get("currency_code", "USD"))
    try:
        url = f"https://api.exchangerate-api.com/v4/latest/{base}"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            return jsonify(
                {"success": True, "rates": data.get("rates", {}), "base": base}
            )
    except Exception as e:
        print(f"Rates error: {e}")
    return jsonify({"success": False, "message": "Could not fetch rates"})


@app.route("/api/chat", methods=["POST"])
@login_required
def chat():
    data = request.get_json()
    message = data.get("message", "")
    history = data.get("history", [])

    try:
        country = session.get("country", "Unknown")
        currency = session.get("currency_code", "USD")
        system_ctx = (
            f"You are Ajeer AI Assistant, a smart workforce management platform assistant. "
            f"The user is from {country} using {currency} currency. "
            f"Help with jobs, workers, payments, workforce management. Be concise and professional."
        )

        chat_history = []
        for h in history[-8:]:
            role = "user" if h["role"] == "user" else "model"
            chat_history.append({"role": role, "parts": [h["content"]]})

        gemini_chat = gemini_model.start_chat(history=chat_history)
        response = gemini_chat.send_message(f"{system_ctx}\n\n{message}")
        reply = response.text

        mongo.db.chat_logs.insert_one(
            {
                "user_id": session["user_id"],
                "message": message,
                "reply": reply[:500],
                "timestamp": datetime.utcnow(),
            }
        )

        return jsonify({"success": True, "reply": reply})
    except Exception as e:
        return jsonify({"success": False, "reply": f"AI error: {str(e)}"})


if __name__ == "__main__":
    app.run(debug=True, port=5000)
