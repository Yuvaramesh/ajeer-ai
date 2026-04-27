from pymongo import MongoClient
from datetime import datetime
from bson.objectid import ObjectId
import os

class Database:
    """MongoDB database connection handler"""
    
    def __init__(self, uri):
        self.client = MongoClient(uri)
        self.db = self.client.get_default_database()
    
    def close(self):
        self.client.close()
    
    def init_collections(self):
        """Initialize MongoDB collections with indexes"""
        # Users collection
        if 'users' not in self.db.list_collection_names():
            self.db.create_collection('users')
            self.db.users.create_index('email', unique=True)
            self.db.users.create_index('username', unique=True)
        
        # Conversations collection
        if 'conversations' not in self.db.list_collection_names():
            self.db.create_collection('conversations')
            self.db.conversations.create_index('user_id')
            self.db.conversations.create_index('created_at')
        
        # FAQs collection (metadata, embeddings stored in Qdrant)
        if 'faqs' not in self.db.list_collection_names():
            self.db.create_collection('faqs')
            self.db.faqs.create_index('qdrant_id', unique=True)


class UserModel:
    """User model for MongoDB"""
    
    @staticmethod
    def create_user(db, username, email, password_hash, country=None, preferred_currency=None):
        """Create a new user"""
        user_doc = {
            'username': username,
            'email': email,
            'password_hash': password_hash,
            'country': country,
            'preferred_currency': preferred_currency,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }
        result = db.users.insert_one(user_doc)
        return result.inserted_id
    
    @staticmethod
    def find_by_email(db, email):
        """Find user by email"""
        return db.users.find_one({'email': email})
    
    @staticmethod
    def find_by_username(db, username):
        """Find user by username"""
        return db.users.find_one({'username': username})
    
    @staticmethod
    def find_by_id(db, user_id):
        """Find user by ID"""
        if isinstance(user_id, str):
            user_id = ObjectId(user_id)
        return db.users.find_one({'_id': user_id})
    
    @staticmethod
    def update_user(db, user_id, update_data):
        """Update user data"""
        if isinstance(user_id, str):
            user_id = ObjectId(user_id)
        update_data['updated_at'] = datetime.utcnow()
        result = db.users.update_one(
            {'_id': user_id},
            {'$set': update_data}
        )
        return result.modified_count > 0


class ConversationModel:
    """Conversation model for MongoDB"""
    
    @staticmethod
    def create_conversation(db, user_id, agent_type, query, response):
        """Create a new conversation record"""
        if isinstance(user_id, str):
            user_id = ObjectId(user_id)
        
        conversation_doc = {
            'user_id': user_id,
            'agent_type': agent_type,
            'query': query,
            'response': response,
            'created_at': datetime.utcnow()
        }
        result = db.conversations.insert_one(conversation_doc)
        return result.inserted_id
    
    @staticmethod
    def get_user_conversations(db, user_id, limit=50):
        """Get user's conversation history"""
        if isinstance(user_id, str):
            user_id = ObjectId(user_id)
        
        conversations = list(db.conversations.find(
            {'user_id': user_id}
        ).sort('created_at', -1).limit(limit))
        return conversations
    
    @staticmethod
    def get_conversation(db, conversation_id):
        """Get a specific conversation"""
        if isinstance(conversation_id, str):
            conversation_id = ObjectId(conversation_id)
        return db.conversations.find_one({'_id': conversation_id})


class FAQModel:
    """FAQ model for MongoDB (metadata storage)"""
    
    @staticmethod
    def create_faq_record(db, qdrant_id, question, answer, category):
        """Create FAQ metadata record in MongoDB"""
        faq_doc = {
            'qdrant_id': qdrant_id,
            'question': question,
            'answer': answer,
            'category': category,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }
        result = db.faqs.insert_one(faq_doc)
        return result.inserted_id
    
    @staticmethod
    def get_all_faqs(db):
        """Get all FAQ metadata records"""
        return list(db.faqs.find({}))
    
    @staticmethod
    def get_faq_by_qdrant_id(db, qdrant_id):
        """Get FAQ metadata by Qdrant ID"""
        return db.faqs.find_one({'qdrant_id': qdrant_id})
