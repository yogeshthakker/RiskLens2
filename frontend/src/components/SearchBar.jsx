import { useState } from "react";

export default function SearchBar({ onSearch, loading }) {
  const [value, setValue] = useState("");

  return (
    <div style={styles.wrapper}>
      <input
        style={styles.input}
        placeholder="Enter account ID — e.g. ACC3003"
        value={value}
        onChange={e => setValue(e.target.value)}
        onKeyDown={e => e.key === "Enter" && onSearch(value)}
      />
      <button
        style={styles.button}
        onClick={() => onSearch(value)}
        disabled={loading || !value}
      >
        {loading ? "Investigating..." : "Investigate"}
      </button>
    </div>
  );
}

const styles = {
  wrapper: {
    display       : "flex",
    gap           : "12px",
    marginBottom  : "32px",
  },
  input: {
    flex          : 1,
    padding       : "12px 16px",
    borderRadius  : "8px",
    border        : "1px solid #e2e8f0",
    fontSize      : "15px",
    outline       : "none",
    background    : "#f8fafc",
  },
  button: {
    padding       : "12px 28px",
    borderRadius  : "8px",
    border        : "none",
    background    : "#1e40af",
    color         : "#fff",
    fontSize      : "15px",
    cursor        : "pointer",
    fontWeight    : "600",
  }
};