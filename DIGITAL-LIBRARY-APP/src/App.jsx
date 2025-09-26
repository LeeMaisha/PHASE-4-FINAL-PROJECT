import React, { useEffect, useState } from "react";
import BookList from "./components/BookList";
import AddBook from "./components/AddBook";
import SearchBox from "./components/SearchBox";
import "./App.css";

function App() {
  const [books, setBooks] = useState([]);
  const [filteredBooks, setFilteredBooks] = useState([]);

  // Fetch books from Flask backend
  useEffect(() => {
    fetch(" http://192.168.100.8:5000/books") // Flask API endpoint
      .then((res) => res.json())
      .then((data) => {
        setBooks(data);
        setFilteredBooks(data);
      })
      .catch((err) => console.error("Error fetching books:", err));
  }, []);

  const handleSearch = (query) => {
    if (!query) {
      setFilteredBooks(books);
    } else {
      setFilteredBooks(
        books.filter((book) =>
          book.title.toLowerCase().includes(query.toLowerCase())
        )
      );
    }
  };

  const handleAddBook = (newBook) => {
    setBooks([...books, newBook]);
    setFilteredBooks([...books, newBook]);
  };

  const handleDeleteBook = (id) => {
    fetch("$http://192.168.100.8:5000/books", {
      method: "DELETE",
    })
      .then(() => {
        const updated = books.filter((book) => book.id !== id);
        setBooks(updated);
        setFilteredBooks(updated);
      })
      .catch((err) => console.error("Error deleting book:", err));
  };
  useEffect(() => {
    const fetchBooks = async () => {
        try {
            // Try localhost first
            const response = await fetch('http://localhost:5000/books');
            
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            const books = await response.json();
            setBooks(books);
        } catch (error) {
            console.error('Error fetching books:', error);
        }
    };

    fetchBooks();
}, []);

  return (
    <div className="container">
      <h1>Digital Library</h1>
      <SearchBox onSearch={handleSearch} />
      <AddBook onAdd={handleAddBook} existingBooks ={filteredBooks}/>
      <BookList books={filteredBooks} onDelete={handleDeleteBook} />
    </div>
  );
}


export default App;
