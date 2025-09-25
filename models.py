from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date
from sqlalchemy.orm import relationship
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    email = db.Column(db.String, unique=True, nullable=False)
    password_hash = db.Column(db.String, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    borrow_records = relationship(
        "BorrowRecord", back_populates="user", cascade="all, delete-orphan"
    )
    ratings = db.relationship(
        "Rating", back_populates="user", cascade="all, delete-orphan"
    )

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,  # Fixed: was "first_name" but field is "name"
            "email": self.email,
            "created_at": self.created_at.isoformat() if self.created_at else None,  # Added ISO format
        }

class Book(db.Model):
    __tablename__ = "books"
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    author = db.Column(db.String, nullable=False)
    published_year = db.Column(db.Date, nullable=True)  # This is a Date object
    description = db.Column(db.Text)
    genre_id = db.Column(db.Integer, db.ForeignKey("genres.id"))
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    genre = db.relationship("Genre", back_populates="books")
    borrow_records = db.relationship(
        "BorrowRecord", back_populates="book", cascade="all, delete-orphan"
    )
    ratings = db.relationship(
        "Rating", back_populates="book", cascade="all, delete-orphan"
    )
    
    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "author": self.author,
            "published_year": self.published_year.isoformat() if self.published_year else None,  # Fixed: convert to ISO string
            "description": self.description,
            "genre": self.genre.name if self.genre else None,
            "last_updated": self.last_updated.isoformat() if self.last_updated else None,  # Added ISO format
        }

class Genre(db.Model):
    __tablename__ = "genres"
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True, nullable=False)

    books = db.relationship("Book", back_populates="genre", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
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
            "due_date": self.due_date.isoformat() if self.due_date else None,  # Added due_date
            "return_date": self.return_date.isoformat() if self.return_date else None,
        }

class Rating(db.Model):
    __tablename__ = "ratings"
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    book_id = db.Column(db.Integer, db.ForeignKey("books.id"))
    rating = db.Column(db.Integer, nullable=False)  # Fixed: field is "rating" not "score"
    review = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship("User", back_populates="ratings")
    book = db.relationship("Book", back_populates="ratings")

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "book_id": self.book_id,
            "rating": self.rating,  # Fixed: was "score" but field is "rating"
            "review": self.review,
            "created_at": self.created_at.isoformat() if self.created_at else None,  # Fixed: ISO format
        }