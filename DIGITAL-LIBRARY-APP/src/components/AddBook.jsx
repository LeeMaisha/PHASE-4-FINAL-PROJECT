import React, { useState } from "react";

function AddBook({ onAdd, existingBooks }) {
  const [book, setBook] = useState({ title: "", author: "", genre: "" });
  const [error, setError] = useState("");

  const handleChange = (e) => {
    setBook({ ...book, [e.target.name]: e.target.value });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    // const duplicate = [...existingBooks];

    // if (duplicate) {
    //   setError("This book by the same author already exists.");
    // }

    fetch("http://127.0.0.1:5000/books", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(book),
    })
      .then((res) => res.json())
      .then((data) => {
        onAdd(data.book);
        console.log(data);
        // setBook({ title: "", author: "", genre: "" }); 
        setError("");
      })
      .catch((err) => console.error("Error adding book:", err));
  };

  return (
    <form onSubmit={handleSubmit} className="add-book-form">
      <input
        type="text"
        name="title"
        placeholder="Book Title"
        value={book.title}
        onChange={handleChange}
        required
      />
      <input
        type="text"
        name="author"
        placeholder="Author"
        value={book.author}
        onChange={handleChange}
        required
      />
      <input
        type="text"
        name="genre"
        placeholder="Genre"
        value={book.genre}
        onChange={handleChange}
        required
      />

      {error && <p style={{ color: "red" }}>{error}</p>}

      <button type="submit">Add Book</button>
    </form>
  );
}

export default AddBook;
