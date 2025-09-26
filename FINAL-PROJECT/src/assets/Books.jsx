import { Link } from "react-router-dom";

const books = [
    { id: 1, title: "Think Better"},
    { id: 2, title: "The Great Gatsby"},
    { id: 3, title: "Beauty and the Beast"},
    { id: 4, title: "The Catcher in the Rye"}
];

function Books() {
    return (
        <div>
            <h2>Book List</h2>
            <ul>
                {books.map(book => (
                    <li key={book.id}>
                        <Link to={`/books/${book.id}`}>{book.title}</Link>
                    </li>
                ))}
            </ul>
        </div>
    );
}

export default Books;