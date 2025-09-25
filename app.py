from flask import Flask, request, jsonify
from flask_migrate import Migrate
from flask_restful import Resource, Api
from models import db, User, Book, BorrowRecord, Genre, Rating

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///app.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)
migrate = Migrate(app, db)
api = Api(app)



class BooksResource(Resource):
    def get(self):
        books = Book.query.all()
        return [b.to_dict() for b in books], 200

class BookResource(Resource):
    def get(self, id):
        book = Book.query.get(id)
        if not book:
            return {"error": "Book not found"}, 404
        return book.to_dict(), 200

    def patch(self, id):
        book = Book.query.get(id)
        if not book:
            return {"error": "Book not found"}, 404

        data = request.get_json()
        if "title" in data:
            book.title = data["title"]
        if "author" in data:
            book.author = data["author"]
        db.session.commit()
        return book.to_dict(), 200

class BorrowResource(Resource):
    def post(self):
        data = request.get_json()
        borrow = BorrowRecord(
            user_id=data["user_id"],
            book_id=data["book_id"],
            due_date=data.get("due_date")
        )
        db.session.add(borrow)
        db.session.commit()
        return borrow.to_dict(), 201

class RatingResource(Resource):
    def post(self):
        data = request.get_json()
        rating = Rating(
            user_id=data["user_id"],
            book_id=data["book_id"],
            rating=data["rating"],
            review=data.get("review")
        )
        db.session.add(rating)
        db.session.commit()
        return rating.to_dict(), 201

api.add_resource(BooksResource, "/books")
api.add_resource(BookResource, "/books/<int:id>")
api.add_resource(BorrowResource, "/borrow")
api.add_resource(RatingResource, "/ratings")

if __name__ == "__main__":
    app.run(debug=True)