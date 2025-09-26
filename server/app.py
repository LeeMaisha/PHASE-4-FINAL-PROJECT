# app.py
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///library.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Simple Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    
    def to_dict(self):
        return {'id': self.id, 'name': self.name, 'email': self.email}

class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    author = db.Column(db.String(100), nullable=False)
    is_available = db.Column(db.Boolean, default=True)
    
    def to_dict(self):
        return {
            'id': self.id, 
            'title': self.title, 
            'author': self.author, 
            'is_available': self.is_available
        }

class BorrowRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False)
    borrow_date = db.Column(db.DateTime, default=datetime.utcnow)
    return_date = db.Column(db.DateTime)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'book_id': self.book_id,
            'borrow_date': self.borrow_date.isoformat() if self.borrow_date else None,
            'return_date': self.return_date.isoformat() if self.return_date else None
        }

# Routes
@app.route('/')
def home():
    return jsonify({"message": "Library Management API", "endpoints": ["/books", "/users", "/borrow"]})

# Books
@app.route('/books', methods=['GET'])
def get_books():
    books = Book.query.all()
    return jsonify([book.to_dict() for book in books])

@app.route('/books', methods=['POST'])
def add_book():
    data = request.get_json()
    book = Book(title=data['title'], author=data['author'])
    db.session.add(book)
    db.session.commit()
    return jsonify(book.to_dict()), 201

@app.route('/books/<int:book_id>', methods=['GET'])
def get_book(book_id):
    book = Book.query.get_or_404(book_id)
    return jsonify(book.to_dict())

# Users
@app.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()
    return jsonify([user.to_dict() for user in users])

@app.route('/users', methods=['POST'])
def add_user():
    data = request.get_json()
    user = User(name=data['name'], email=data['email'])
    db.session.add(user)
    db.session.commit()
    return jsonify(user.to_dict()), 201

# Borrow
@app.route('/borrow', methods=['POST'])
def borrow_book():
    data = request.get_json()
    book = Book.query.get_or_404(data['book_id'])
    
    if not book.is_available:
        return jsonify({"error": "Book not available"}), 400
    
    # Create borrow record
    borrow = BorrowRecord(user_id=data['user_id'], book_id=data['book_id'])
    book.is_available = False
    
    db.session.add(borrow)
    db.session.commit()
    return jsonify(borrow.to_dict()), 201

@app.route('/return/<int:borrow_id>', methods=['PUT'])
def return_book(borrow_id):
    borrow = BorrowRecord.query.get_or_404(borrow_id)
    book = Book.query.get(borrow.book_id)
    
    borrow.return_date = datetime.utcnow()
    book.is_available = True
    
    db.session.commit()
    return jsonify(borrow.to_dict())

@app.route('/borrowed-books')
def borrowed_books():
    records = BorrowRecord.query.filter_by(return_date=None).all()
    return jsonify([record.to_dict() for record in records])

# Initialize database and add sample data
def setup_database():
    with app.app_context():
        db.create_all()
        
        # Add sample data if empty
        if not Book.query.first():
            books = [
                Book(title="Harry Potter", author="J.K. Rowling"),
                Book(title="1984", author="George Orwell"),
                Book(title="To Kill a Mockingbird", author="Harper Lee")
            ]
            db.session.add_all(books)
            
        if not User.query.first():
            users = [
                User(name="John Doe", email="john@example.com"),
                User(name="Jane Smith", email="jane@example.com")
            ]
            db.session.add_all(users)
            
        db.session.commit()
        print("Database setup complete!")

if __name__ == '__main__':
    setup_database()
    app.run(debug=True)