import React, { useState } from "react";

function SearchBox({ onSearch }) {
  const [query, setQuery] = useState("");

  const handleChange = (e) => {
    setQuery(e.target.value);
    onSearch(e.target.value);
  };

  return (
    <div className="search-box">
      <input
        type="text"
        placeholder="🔍 Search books..."
        value={query}
        onChange={handleChange}
      />
    </div>
  );
}

export default SearchBox;
