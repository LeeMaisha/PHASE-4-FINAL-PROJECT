from datetime import datetime, timedelta, date
from faker import Faker
from app import app, db  
from models import User, Book, Genre, Rating, BorrowRecord

fake = Faker()

with app.app_context():
    
    db.session.query(User).delete()
    db.session.query(Book).delete()
    db.session.query(Genre).delete()
    db.session.query(Rating).delete()
    db.session.query(BorrowRecord).delete()
    db.session.commit()

    genres = [
        Genre(name="Mystery"),
        Genre(name="Technology"),
        Genre(name="Philosophy"),
        Genre(name="Fantasy"),
        Genre(name="Science"),
        Genre(name="Self-Help"),
    ]
    db.session.add_all(genres)
    db.session.commit()

   
    users = [
        User(name="Jane Doe", email="aliceD@gmail.com", password_hash="hashed4567", created_at=datetime.now()),
        User(name="John Smith", email="johnS@gmail.com", password_hash="hashed1234", created_at=datetime.now()),
        User(name="Alice Johnson", email="aliceJ@gmail.com", password_hash="hashed7890", created_at=datetime.now()),
        User(name="Bob Brown", email="bobB@gmail.com", password_hash="hashed2345", created_at=datetime.now()),
        User(name="Charlie Davis", email="char@gmail.com", password_hash="hashed5678", created_at=datetime.now()),
    ]
    db.session.add_all(users)
    db.session.commit()

    
    book1 = Book(
        title="Think Big",
        author="Ben Carson",
        published_year=date(1982, 1, 1),  
        genre_id=3,
        description="A motivational book encouraging readers to set high goals and achieve their dreams.",
        last_updated=datetime.now()
    )

    book2 = Book(
        title="The Great Gatsby",
        author="F. Scott Fitzgerald",
        published_year=date(1925, 1, 1),  
        genre_id=4,
        description="A novel about the American dream and the decadence of the Jazz Age.",
        last_updated=datetime.now()
    )

    book3 = Book(
        title="Beauty and the Beast",
        author="Gabrielle-Suzanne Barbot de Villeneuve", 
        published_year=date(1740, 1, 1),  # Changed to date object
        genre_id=1,
        description="A fairy tale about beauty, love, and transformation.",
        last_updated=datetime.now()
    )

    book4 = Book(
        title="The Catcher in the Rye",
        author="J.D. Salinger",
        published_year=date(1951, 1, 1),  # Changed to date object
        genre_id=1,
        description="A story about teenage rebellion and alienation.",
        last_updated=datetime.now()
    )
    db.session.add_all([book1, book2, book3, book4])
    db.session.commit()

    
    rating1 = Rating(user_id=1, book_id=1, rating=5, review="Inspiring and motivational!", created_at=datetime.now())
    rating2 = Rating(user_id=2, book_id=2, rating=4, review="A classic read with deep themes.", created_at=datetime.now())
    rating3 = Rating(user_id=3, book_id=3, rating=3, review="A timeless fairy tale.", created_at=datetime.now())

    db.session.add_all([rating1, rating2, rating3])
    db.session.commit()

   
    borrow1 = BorrowRecord(
        user_id=1,
        book_id=2,
        borrow_date=datetime.now(),
        due_date=datetime.now() + timedelta(days=14), 
    )
    borrow2 = BorrowRecord(
        user_id=2,
        book_id=3,
        borrow_date=datetime.now() - timedelta(days=3),
        due_date=datetime.now() + timedelta(days=11),
    )
    db.session.add_all([borrow1, borrow2])
    db.session.commit()

