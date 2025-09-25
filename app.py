from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
import json


app = Flask(__name__)
CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///library.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['DEBUG'] = True

db = SQLAlchemy(app)

class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (date, datetime)):
            return obj.isoformat()
        return super().default(obj)

app.json_encoder = CustomJSONEncoder

class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    borrow_records = db.relationship("BorrowRecord", back_populates="user")
    ratings = db.relationship("Rating", back_populates="user")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

class Genre(db.Model):
    __tablename__ = "genres"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    books = db.relationship("Book", back_populates="genre")

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
        }

class Book(db.Model):
    __tablename__ = "books"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    author = db.Column(db.String(100), nullable=False)
    published_year = db.Column(db.Date, nullable=True)
    description = db.Column(db.Text)
    genre_id = db.Column(db.Integer, db.ForeignKey("genres.id"))
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    genre = db.relationship("Genre", back_populates="books")
    borrow_records = db.relationship("BorrowRecord", back_populates="book")
    ratings = db.relationship("Rating", back_populates="book")

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "author": self.author,
            "published_year": self.published_year.isoformat() if self.published_year else None,
            "description": self.description,
            "genre": self.genre.name if self.genre else None,
            "genre_id": self.genre_id,
        }

class BorrowRecord(db.Model):
    __tablename__ = "borrow_records"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    book_id = db.Column(db.Integer, db.ForeignKey("books.id"))
    borrow_date = db.Column(db.DateTime, default=datetime.utcnow)
    due_date = db.Column(db.DateTime, nullable=False)
    return_date = db.Column(db.DateTime, nullable=True)

    user = db.relationship("User", back_populates="borrow_records")
    book = db.relationship("Book", back_populates="borrow_records")

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "book_id": self.book_id,
            "borrow_date": self.borrow_date.isoformat() if self.borrow_date else None,
            "due_date": self.due_date.isoformat() if self.due_date else None,
            "return_date": self.return_date.isoformat() if self.return_date else None,
        }

class Rating(db.Model):
    __tablename__ = "ratings"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    book_id = db.Column(db.Integer, db.ForeignKey("books.id"))
    rating = db.Column(db.Integer, nullable=False)
    review = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship("User", back_populates="ratings")
    book = db.relationship("Book", back_populates="ratings")

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "book_id": self.book_id,
            "rating": self.rating,
            "review": self.review,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


def create_sample_data():
    """Create sample data for testing"""
    if User.query.first() is not None:
        return
    
    fiction = Genre(name="Fiction")
    scifi = Genre(name="Science Fiction")
    mystery = Genre(name="Mystery")
    db.session.add_all([fiction, scifi, mystery])
    db.session.flush()  

 
    user1 = User(name="John Doe", email="john@example.com")
    user1.set_password("password123")
    
    user2 = User(name="Jane Smith", email="jane@example.com")
    user2.set_password("password123")
    
    db.session.add_all([user1, user2])
    db.session.flush()

    book1 = Book(
        title="The Great Gatsby",
        author="F. Scott Fitzgerald",
        published_year=date(1925, 4, 10),
        description="A classic novel about the American Dream",
        genre_id=fiction.id
    )
    
    book2 = Book(
        title="Dune",
        author="Frank Herbert", 
        published_year=date(1965, 8, 1),
        description="Epic science fiction novel",
        genre_id=scifi.id
    )
    
    book3 = Book(
        title="Murder on the Orient Express",
        author="Agatha Christie",
        published_year=date(1934, 1, 1),
        description="Famous mystery novel",
        genre_id=mystery.id
    )
    
    db.session.add_all([book1, book2, book3])
    db.session.commit()
    
with app.app_context():
    db.create_all()
    create_sample_data()


@app.route('/')
def home():
    """Home page with API information"""
    return jsonify({
        "message": "Library Management API is running!",
        "endpoints": {
            "home": "GET /",
            "users": "GET /users",
            "books": "GET /books",
            "genres": "GET /genres",
            "create_rating": "POST /ratings",
            "get_ratings": "GET /ratings",
            "get_rating": "GET /ratings/<id>",
            "create_borrow": "POST /borrow",
            "get_borrows": "GET /borrow"
        },
        "status": "success"
    })
@app.route('/users', methods=['GET'])
def get_users():
    """Get all users"""
    users = User.query.all()
    return jsonify([user.to_dict() for user in users])

@app.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    """Get specific user"""
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    return jsonify(user.to_dict())

@app.route('/books', methods=['GET'])
def get_books():
    """Get all books"""
    books = Book.query.all()
    return jsonify([book.to_dict() for book in books])

@app.route('/books/<int:book_id>', methods=['GET'])
def get_book(book_id):
    """Get specific book"""
    book = Book.query.get(book_id)
    if not book:
        return jsonify({"error": "Book not found"}), 404
    return jsonify(book.to_dict())

@app.route('/genres', methods=['GET'])
def get_genres():
    """Get all genres"""
    genres = Genre.query.all()
    return jsonify([genre.to_dict() for genre in genres])

@app.route('/ratings', methods=['GET'])
def get_all_ratings():
    """Get all ratings"""
    ratings = Rating.query.all()
    return jsonify([rating.to_dict() for rating in ratings])

@app.route('/ratings/<int:rating_id>', methods=['GET'])
def get_rating(rating_id):
    """Get specific rating"""
    rating = Rating.query.get(rating_id)
    if not rating:
        return jsonify({"error": "Rating not found"}), 404
    return jsonify(rating.to_dict())

@app.route('/ratings', methods=['POST'])
def create_rating():
    """Create a new rating"""
    try:
        data = request.get_json()
        
        print("Received data:", data)
        
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
            
        # Check required fields
        required_fields = ['user_id', 'book_id', 'rating']
        missing_fields = [field for field in required_fields if field not in data]
        
        if missing_fields:
            return jsonify({"error": f"Missing required fields: {', '.join(missing_fields)}"}), 400
        

        user = User.query.get(data['user_id'])
        if not user:
            return jsonify({"error": "User not found"}), 404

        book = Book.query.get(data['book_id'])
        if not book:
            return jsonify({"error": "Book not found"}), 404
        
        if not 1 <= data['rating'] <= 5:
            return jsonify({"error": "Rating must be between 1 and 5"}), 400
        
        existing_rating = Rating.query.filter_by(
            user_id=data['user_id'], 
            book_id=data['book_id']
        ).first()
        
        if existing_rating:
            return jsonify({"error": "User has already rated this book"}), 400
    
        rating = Rating(
            user_id=data['user_id'],
            book_id=data['book_id'],
            rating=data['rating'],
            review=data.get('review', ''),
            created_at=datetime.utcnow()
        )
        
        db.session.add(rating)
        db.session.commit()
        
        print("Rating created successfully!")
        return jsonify({
            "message": "Rating created successfully!",
            "rating": rating.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        print( "Error:", str(e))
        return jsonify({"error": f"Server error: {str(e)}"}), 500

@app.route('/borrow', methods=['GET'])
def get_borrow_records():
    """Get all borrow records"""
    borrows = BorrowRecord.query.all()
    return jsonify([borrow.to_dict() for borrow in borrows])

@app.route('/borrow', methods=['POST'])
def create_borrow_record():
    """Create a new borrow record"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
            
        required_fields = ['user_id', 'book_id', 'due_date']
        missing_fields = [field for field in required_fields if field not in data]
        
        if missing_fields:
            return jsonify({"error": f"Missing required fields: {', '.join(missing_fields)}"}), 400
        
        user = User.query.get(data['user_id'])
        book = Book.query.get(data['book_id'])
        
        if not user:
            return jsonify({"error": "User not found"}), 404
        if not book:
            return jsonify({"error": "Book not found"}), 404
        
      
        borrow = BorrowRecord(
            user_id=data['user_id'],
            book_id=data['book_id'],
            due_date=datetime.fromisoformat(data['due_date']),  
            borrow_date=datetime.utcnow()
        )
        
        db.session.add(borrow)
        db.session.commit()
        
        return jsonify({
            "message": "Borrow record created successfully!",
            "borrow": borrow.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Server error: {str(e)}"}), 500
@app.route('/books', methods=['GET', 'POST'])
def handle_books():
    if request.method == 'GET':
        books = Book.query.all()
        return jsonify([book.to_dict() for book in books])
    
    elif request.method == 'POST':
        try:
            data = request.get_json()
            print("Received book data:", data)  
            
            if not data:
                return jsonify({"error": "No JSON data provided"}), 400
            
            if not data.get('title') or not data.get('author'):
                return jsonify({"error": "Title and author are required"}), 400
            
            # Create new book
            book = Book(
                title=data['title'],
                author=data['author'],
                published_year=data.get('published_year'),
                genres_id=data.get('genres_id'),
                description=data.get('description', '')
            )
            
            db.session.add(book)
            db.session.commit()
            
            return jsonify({
                "message": "Book created successfully!",
                "book": book.to_dict()
            }), 201
            
        except Exception as e:
            db.session.rollback()
            print("Error creating book:", str(e))
            return jsonify({"error": f"Server error: {str(e)}"}), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500

if __name__ == '__main__':
    print("   GET  /users - Get all users")

    app.run(debug=True, host='0.0.0.0', port=5000)