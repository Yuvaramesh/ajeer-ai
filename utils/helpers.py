import requests
import hashlib
import secrets
from functools import wraps
from flask import session, redirect, url_for
from datetime import datetime

class AuthHelper:
    """Authentication helper functions"""
    
    @staticmethod
    def hash_password(password):
        """Hash password using SHA256"""
        salt = secrets.token_hex(32)
        password_hash = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt.encode('utf-8'),
            100000
        )
        return f"{salt}${password_hash.hex()}"
    
    @staticmethod
    def verify_password(password, password_hash):
        """Verify password against hash"""
        try:
            salt, stored_hash = password_hash.split('$')
            password_verify = hashlib.pbkdf2_hmac(
                'sha256',
                password.encode('utf-8'),
                salt.encode('utf-8'),
                100000
            )
            return password_verify.hex() == stored_hash
        except:
            return False
    
    @staticmethod
    def login_required(f):
        """Decorator to require login"""
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                return redirect(url_for('auth.login'))
            return f(*args, **kwargs)
        return decorated_function


class CountryHelper:
    """Country detection helper functions"""
    
    # Mapping of country codes to currencies
    COUNTRY_CURRENCY_MAP = {
        'US': 'USD', 'CA': 'CAD', 'GB': 'GBP', 'AU': 'AUD',
        'JP': 'JPY', 'IN': 'INR', 'AE': 'AED', 'SA': 'SAR',
        'FR': 'EUR', 'DE': 'EUR', 'IT': 'EUR', 'ES': 'EUR',
        'BR': 'BRL', 'MX': 'MXN', 'ZA': 'ZAR', 'SG': 'SGD',
        'HK': 'HKD', 'CN': 'CNY', 'KR': 'KRW', 'TH': 'THB',
        'MY': 'MYR', 'PH': 'PHP', 'ID': 'IDR', 'VN': 'VND',
        'PK': 'PKR', 'BD': 'BDT', 'LK': 'LKR', 'EG': 'EGP',
        'NG': 'NGN', 'KE': 'KES', 'IL': 'ILS', 'TR': 'TRY',
        'RU': 'RUB', 'UA': 'UAH', 'PL': 'PLN', 'CZ': 'CZK'
    }
    
    @staticmethod
    def get_country_from_ip(ip_address):
        """Get country code from IP address using ipapi.co"""
        try:
            response = requests.get(f'https://ipapi.co/{ip_address}/json/', timeout=5)
            if response.status_code == 200:
                data = response.json()
                return data.get('country_code', 'US'), data.get('country_name', 'United States')
            return 'US', 'United States'
        except:
            return 'US', 'United States'
    
    @staticmethod
    def get_currency_for_country(country_code):
        """Get currency code for country"""
        return CountryHelper.COUNTRY_CURRENCY_MAP.get(country_code, 'USD')


class CurrencyConverter:
    """Currency conversion helper functions"""
    
    @staticmethod
    def convert_currency(amount, from_currency, to_currency):
        """Convert currency using Google Sheets API or exchangerate-api"""
        if from_currency == to_currency:
            return amount, from_currency, to_currency
        
        try:
            # Using exchangerate-api (free tier available)
            response = requests.get(
                f'https://api.exchangerate-api.com/v4/latest/{from_currency}',
                timeout=5
            )
            if response.status_code == 200:
                data = response.json()
                if to_currency in data.get('rates', {}):
                    rate = data['rates'][to_currency]
                    converted_amount = amount * rate
                    return round(converted_amount, 2), from_currency, to_currency
            return amount, from_currency, to_currency
        except Exception as e:
            print(f"[v0] Currency conversion error: {e}")
            return amount, from_currency, to_currency
    
    @staticmethod
    def get_exchange_rate(from_currency, to_currency):
        """Get exchange rate between two currencies"""
        try:
            response = requests.get(
                f'https://api.exchangerate-api.com/v4/latest/{from_currency}',
                timeout=5
            )
            if response.status_code == 200:
                data = response.json()
                return data.get('rates', {}).get(to_currency, 1.0)
            return 1.0
        except:
            return 1.0


class ValidationHelper:
    """Input validation helper functions"""
    
    @staticmethod
    def validate_email(email):
        """Validate email format"""
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    @staticmethod
    def validate_password(password):
        """Validate password strength"""
        if len(password) < 8:
            return False, "Password must be at least 8 characters long"
        if not any(c.isupper() for c in password):
            return False, "Password must contain at least one uppercase letter"
        if not any(c.isdigit() for c in password):
            return False, "Password must contain at least one digit"
        return True, "Password is valid"
    
    @staticmethod
    def validate_username(username):
        """Validate username format"""
        if len(username) < 3:
            return False, "Username must be at least 3 characters long"
        if len(username) > 20:
            return False, "Username must be at most 20 characters long"
        import re
        if not re.match(r'^[a-zA-Z0-9_-]+$', username):
            return False, "Username can only contain letters, numbers, underscores, and hyphens"
        return True, "Username is valid"
