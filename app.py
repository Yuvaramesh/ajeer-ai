from flask import Flask, render_template, request, session, redirect, url_for, jsonify
from flask_login import LoginManager
from config import config
from models import Database, UserModel, ConversationModel, FAQModel
from utils.helpers import AuthHelper, CountryHelper, CurrencyConverter, ValidationHelper
from agents.rag_agents import RAGAgentSystem
import os
from functools import wraps

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(config[os.getenv('FLASK_ENV', 'development')])

# Initialize database
db_connection = Database(app.config['MONGODB_URI'])
db_connection.init_collections()
db = db_connection.db

# Initialize RAG system
rag_system = RAGAgentSystem(
    qdrant_url=app.config['QDRANT_URL'],
    api_key=app.config.get('QDRANT_API_KEY'),
    google_api_key=app.config['GOOGLE_API_KEY']
)

# Session management
login_manager = LoginManager()
login_manager.init_app(app)


def login_required(f):
    """Decorator to require login"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


# ===== Authentication Routes =====

@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration"""
    if request.method == 'POST':
        data = request.get_json() if request.is_json else request.form
        username = data.get('username', '').strip()
        email = data.get('email', '').strip()
        password = data.get('password', '')
        password_confirm = data.get('password_confirm', '')
        
        # Validation
        if not username or not email or not password:
            return jsonify({'success': False, 'error': 'All fields are required'}), 400
        
        username_valid, username_msg = ValidationHelper.validate_username(username)
        if not username_valid:
            return jsonify({'success': False, 'error': username_msg}), 400
        
        if not ValidationHelper.validate_email(email):
            return jsonify({'success': False, 'error': 'Invalid email format'}), 400
        
        password_valid, password_msg = ValidationHelper.validate_password(password)
        if not password_valid:
            return jsonify({'success': False, 'error': password_msg}), 400
        
        if password != password_confirm:
            return jsonify({'success': False, 'error': 'Passwords do not match'}), 400
        
        # Check if user exists
        if UserModel.find_by_email(db, email):
            return jsonify({'success': False, 'error': 'Email already registered'}), 400
        
        if UserModel.find_by_username(db, username):
            return jsonify({'success': False, 'error': 'Username already taken'}), 400
        
        # Get user's country based on IP
        client_ip = request.remote_addr
        country_code, country_name = CountryHelper.get_country_from_ip(client_ip)
        currency = CountryHelper.get_currency_for_country(country_code)
        
        # Hash password and create user
        password_hash = AuthHelper.hash_password(password)
        user_id = UserModel.create_user(
            db, username, email, password_hash,
            country=country_code, preferred_currency=currency
        )
        
        return jsonify({
            'success': True,
            'message': 'Registration successful. Please login.',
            'redirect': url_for('login')
        }), 201
    
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if request.method == 'POST':
        data = request.get_json() if request.is_json else request.form
        email = data.get('email', '').strip()
        password = data.get('password', '')
        
        if not email or not password:
            return jsonify({'success': False, 'error': 'Email and password are required'}), 400
        
        user = UserModel.find_by_email(db, email)
        if not user or not AuthHelper.verify_password(password, user['password_hash']):
            return jsonify({'success': False, 'error': 'Invalid email or password'}), 401
        
        # Set session
        session['user_id'] = str(user['_id'])
        session['username'] = user['username']
        session['country'] = user.get('country', 'US')
        session['preferred_currency'] = user.get('preferred_currency', 'USD')
        session.permanent = True
        
        return jsonify({
            'success': True,
            'message': 'Login successful',
            'redirect': url_for('dashboard')
        }), 200
    
    return render_template('login.html')


@app.route('/logout')
def logout():
    """User logout"""
    session.clear()
    return redirect(url_for('login'))


# ===== Dashboard Routes =====

@app.route('/')
@app.route('/dashboard')
@login_required
def dashboard():
    """Main dashboard"""
    user = UserModel.find_by_id(db, session['user_id'])
    
    return render_template(
        'dashboard.html',
        username=session.get('username'),
        country=session.get('country'),
        currency=session.get('preferred_currency')
    )


# ===== Currency Converter Routes =====

@app.route('/api/convert-currency', methods=['POST'])
@login_required
def convert_currency():
    """Convert currency based on user's country"""
    data = request.get_json()
    amount = data.get('amount', 0)
    from_currency = data.get('from_currency', session.get('preferred_currency', 'USD'))
    to_currency = data.get('to_currency', 'USD')
    
    try:
        converted_amount, from_curr, to_curr = CurrencyConverter.convert_currency(
            amount, from_currency, to_currency
        )
        
        return jsonify({
            'success': True,
            'original_amount': amount,
            'original_currency': from_curr,
            'converted_amount': converted_amount,
            'target_currency': to_curr
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/exchange-rate', methods=['GET'])
def get_exchange_rate():
    """Get exchange rate between two currencies"""
    from_currency = request.args.get('from', 'USD')
    to_currency = request.args.get('to', 'USD')
    
    try:
        rate = CurrencyConverter.get_exchange_rate(from_currency, to_currency)
        return jsonify({
            'success': True,
            'from': from_currency,
            'to': to_currency,
            'rate': rate
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# ===== RAG Chatbot Routes =====

@app.route('/api/chat', methods=['POST'])
@login_required
def chat():
    """Process user query through RAG chatbot"""
    data = request.get_json()
    user_query = data.get('query', '').strip()
    
    if not user_query:
        return jsonify({'success': False, 'error': 'Query cannot be empty'}), 400
    
    try:
        # Get conversation history
        conversations = ConversationModel.get_user_conversations(db, session['user_id'], limit=10)
        conversation_history = [
            {'role': 'user' if conv.get('agent_type') != 'assistant' else 'assistant', 'content': conv.get('query') or conv.get('response')}
            for conv in conversations
        ]
        
        # Process query through RAG system
        result = rag_system.process_query(
            user_query,
            session['user_id'],
            conversation_history
        )
        
        # Store conversation
        ConversationModel.create_conversation(
            db,
            session['user_id'],
            result['agent_type'],
            user_query,
            result['response']
        )
        
        return jsonify({
            'success': True,
            'response': result['response'],
            'agent_type': result['agent_type'],
            'faq_used': result['faq_used']
        }), 200
    except Exception as e:
        print(f"[v0] Chat error: {e}")
        return jsonify({'success': False, 'error': 'Failed to process query'}), 500


@app.route('/api/chatbot-page')
@login_required
def get_chatbot_page():
    """Redirect to chatbot page"""
    return render_template('chatbot.html', username=session.get('username'))


@app.route('/chatbot')
@login_required
def chatbot():
    """Chatbot page"""
    return render_template('chatbot.html', username=session.get('username'))


# ===== User Profile Routes =====

@app.route('/api/user-profile', methods=['GET'])
@login_required
def get_user_profile():
    """Get user profile"""
    user = UserModel.find_by_id(db, session['user_id'])
    if not user:
        return jsonify({'success': False, 'error': 'User not found'}), 404
    
    return jsonify({
        'success': True,
        'username': user.get('username'),
        'email': user.get('email'),
        'country': user.get('country'),
        'preferred_currency': user.get('preferred_currency'),
        'created_at': user.get('created_at').isoformat()
    }), 200


@app.route('/api/user-profile', methods=['PUT'])
@login_required
def update_user_profile():
    """Update user profile"""
    data = request.get_json()
    
    update_data = {}
    if 'preferred_currency' in data:
        update_data['preferred_currency'] = data['preferred_currency']
        session['preferred_currency'] = data['preferred_currency']
    
    if update_data:
        UserModel.update_user(db, session['user_id'], update_data)
    
    return jsonify({'success': True, 'message': 'Profile updated'}), 200


# ===== Error Handlers =====

@app.errorhandler(404)
def not_found(error):
    return jsonify({'success': False, 'error': 'Page not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({'success': False, 'error': 'Internal server error'}), 500


# ===== Application Context =====

@app.teardown_appcontext
def close_db(error):
    """Close database connection on app context teardown"""
    db_connection.close()


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
