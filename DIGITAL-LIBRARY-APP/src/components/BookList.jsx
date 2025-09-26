import React from "react";

function BookList({ books, onDelete }) {
  return (
    <div className="book-list">
      {books.length === 0 ? (
        <p>No books available.</p>
      ) : (
        books.map((book) => (
          <div key={book.id} className="book-card">
            <h3>{book.title}</h3>
            <p><strong>Author:</strong> {book.author}</p>
            <p><strong>Genre:</strong> {book.genre}</p>
            <button onClick={() => onDelete(book.id)} className="delete-btn">
              Delete
            </button>
          </div>
        ))
      )}
    </div>
  );
}

export default BookList;