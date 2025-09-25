import React from "react";

function Searchbar({ placeholder="Search books...",values, onChange}) {
    return (
        <div>
            <input 
                type="text" 
                placeholder={placeholder} 
                value={values} 
                onChange={(e) => onChange(e.target.value)} 
            />
        </div>
    )
}
export default Searchbar;