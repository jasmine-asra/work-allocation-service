import './SearchBar.css';

const SearchBar = ({ searchQuery, setSearchQuery, placeholder }) => {
    return (
        <div className="search-bar">
            <input
                type="text"
                placeholder={placeholder}
                className="search-input"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
            />
        </div>
    );
};

export default SearchBar;