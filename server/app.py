from flask import Flask, request, jsonify
from flask_migrate import Migrate
from flask_restful import Resource, Api
from models import db, User, Book, BorrowRecord, Genre, Rating
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from datetime import datetime

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///app.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)
migrate = Migrate(app, db)
api = Api(app)

@app.route('/')
def home():
    return jsonify({
        "message": "Book Borrowing API",
        "endpoints": {
            "books": "/books",
            "book_detail": "/books/<id>",
            "borrow": "/borrow",
            "ratings": "/ratings"
        }
    }), 200

class BooksResource(Resource):
    def get(self):
        try:
            books = Book.query.all()
            return [b.to_dict() for b in books], 200
        except SQLAlchemyError as e:
            return {"error": "Database error occurred"}, 500

class BookResource(Resource):
    def get(self, id):
        try:
            book = Book.query.get(id)
            if not book:
                return {"error": "Book not found"}, 404
            return book.to_dict(), 200
        except SQLAlchemyError as e:
            return {"error": "Database error occurred"}, 500

    def patch(self, id):
        try:
            book = Book.query.get(id)
            if not book:
                return {"error": "Book not found"}, 404

            data = request.get_json()
            if not data:
                return {"error": "No input data provided"}, 400

            allowed_fields = ["title", "author", "description", "isbn"]
            updates = {}
            
            for field in allowed_fields:
                if field in data:
                    setattr(book, field, data[field])
            
            db.session.commit()
            return book.to_dict(), 200
            
        except SQLAlchemyError as e:
            db.session.rollback()
            return {"error": "Database error occurred"}, 500

class BorrowResource(Resource):
    def post(self):
        try:
            data = request.get_json()
            if not data:
                return {"error": "No input data provided"}, 400
            
            # Validate required fields
            required_fields = ["user_id", "book_id"]
            for field in required_fields:
                if field not in data:
                    return {"error": f"Missing required field: {field}"}, 400
            
            # Check if book exists
            book = Book.query.get(data["book_id"])
            if not book:
                return {"error": "Book not found"}, 404
            
            # Check if user exists
            user = User.query.get(data["user_id"])
            if not user:
                return {"error": "User not found"}, 404
            
            # Check if book is already borrowed
            existing_borrow = BorrowRecord.query.filter_by(
                book_id=data["book_id"], 
                returned=False
            ).first()
            
            if existing_borrow:
                return {"error": "Book is already borrowed"}, 400
            
            borrow = BorrowRecord(
                user_id=data["user_id"],
                book_id=data["book_id"],
                due_date=data.get("due_date")
            )
            
            db.session.add(borrow)
            db.session.commit()
            return borrow.to_dict(), 201
            
        except IntegrityError:
            db.session.rollback()
            return {"error": "Integrity error occurred"}, 400
        except SQLAlchemyError as e:
            db.session.rollback()
            return {"error": "Database error occurred"}, 500

class RatingResource(Resource):
    def post(self):
        try:
            data = request.get_json()
            if not data:
                return {"error": "No input data provided"}, 400
            
            required_fields = ["user_id", "book_id", "rating"]
            for field in required_fields:
                if field not in data:
                    return {"error": f"Missing required field: {field}"}, 400
            
            # Validate rating range
            if not (1 <= data["rating"] <= 5):
                return {"error": "Rating must be between 1 and 5"}, 400
            
            # Check if book exists
            book = Book.query.get(data["book_id"])
            if not book:
                return {"error": "Book not found"}, 404
            
            # Check if user exists
            user = User.query.get(data["user_id"])
            if not user:
                return {"error": "User not found"}, 404
            
            rating = Rating(
                user_id=data["user_id"],
                book_id=data["book_id"],
                rating=data["rating"],
                review=data.get("review")
            )
            
            db.session.add(rating)
            db.session.commit()
            return rating.to_dict(), 201
            
        except IntegrityError:
            db.session.rollback()
            return {"error": "User has already rated this book"}, 400
        except SQLAlchemyError as e:
            db.session.rollback()
            return {"error": "Database error occurred"}, 500

# Add return book functionality
class ReturnResource(Resource):
    def patch(self, id):
        try:
            borrow_record = BorrowRecord.query.get(id)
            if not borrow_record:
                return {"error": "Borrow record not found"}, 404
            
            if borrow_record.returned:
                return {"error": "Book already returned"}, 400
            
            borrow_record.returned = True
            borrow_record.return_date = datetime.utcnow()
            
            db.session.commit()
            return borrow_record.to_dict(), 200
            
        except SQLAlchemyError as e:
            db.session.rollback()
            return {"error": "Database error occurred"}, 500

api.add_resource(BooksResource, "/books")
api.add_resource(BookResource, "/books/<int:id>")
api.add_resource(BorrowResource, "/borrow")
api.add_resource(RatingResource, "/ratings")
api.add_resource(ReturnResource, "/return/<int:id>")

if __name__ == "__main__":
    app.run(debug=True)