from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date
from werkzeug.security import generate_password_hash, check_password_hash
import json

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///library.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (date, datetime)):
            return obj.isoformat()
        return super().default(obj)

app.json_encoder = CustomJSONEncoder

# Models
class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    email = db.Column(db.String, unique=True, nullable=False)
    password_hash = db.Column(db.String, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

class Book(db.Model):
    __tablename__ = "books"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    author = db.Column(db.String, nullable=False)
    published_year = db.Column(db.Date, nullable=True)
    description = db.Column(db.Text)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "author": self.author,
            "published_year": self.published_year.isoformat() if self.published_year else None,
            "description": self.description,
        }

class Rating(db.Model):
    __tablename__ = "ratings"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    book_id = db.Column(db.Integer, db.ForeignKey("books.id"))
    rating = db.Column(db.Integer, nullable=False)
    review = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "book_id": self.book_id,
            "rating": self.rating,
            "review": self.review,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

# Create tables
with app.app_context():
    db.create_all()

@app.route('/')
def home():
    return jsonify({"message": "Library API is working!", "status": "success"})

# DEBUG: List all routes
@app.route('/debug/routes')
def debug_routes():
    routes = []
    for rule in app.url_map.iter_rules():
        if rule.endpoint != 'static':
            routes.append({
                'endpoint': rule.endpoint,
                'methods': list(rule.methods),
                'path': str(rule)
            })
    return jsonify(routes)

# Create test data
@app.route('/api/test-data', methods=['POST'])
def create_test_data():
    try:
        # Create test user
        user = User(
            name="Test User",
            email="test@example.com"
        )
        user.set_password("password123")
        db.session.add(user)
        
        # Create test book
        book = Book(
            title="Sample Book",
            author="Sample Author", 
            published_year=date(2020, 1, 1),
            description="A great book for testing"
        )
        db.session.add(book)
        
        db.session.commit()
        
        return jsonify({
            'message': 'Test data created successfully',
            'user_id': user.id,
            'book_id': book.id
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# CREATE RATING - POST method
@app.route('/api/ratings', methods=['POST'])
def create_rating():
    print("CREATE RATING endpoint hit!")  # Debug print
    try:
        data = request.get_json()
        print("Received data:", data)
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
            
        required_fields = ['user_id', 'book_id', 'rating']
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            return jsonify({'error': f'Missing fields: {missing_fields}'}), 400

        if not 1 <= data['rating'] <= 5:
            return jsonify({'error': 'Rating must be between 1 and 5'}), 400

        rating = Rating(
            user_id=data['user_id'],
            book_id=data['book_id'], 
            rating=data['rating'],
            review=data.get('review', '')
        )
        
        db.session.add(rating)
        db.session.commit()
        
        return jsonify({
            'message': 'Rating created successfully',
            'rating': rating.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# GET ALL RATINGS - GET method  
@app.route('/api/ratings', methods=['GET'])
def get_ratings():
    ratings = Rating.query.all()
    return jsonify([rating.to_dict() for rating in ratings])

if __name__ == '__main__':
    print("=== Library API Starting ===")
    print("Available endpoints:")
    print("GET  / - Home page")
    print("GET  /debug/routes - List all routes")
    print("POST /api/test-data - Create test data")
    print("POST /api/ratings - Create a rating")
    print("GET  /api/ratings - Get all ratings")
    print("=============================")
    app.run(debug=True, port=5000)