import React, { useState } from "react";
import axios from "axios";

function ViewMapped() {
  const [mappedProducts, setMappedProducts] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const fetchMappedProducts = async () => {
    setLoading(true);
    setError("");

    try {
      const response = await axios.get("http://127.0.0.1:5000/view-mapped");
      if (Array.isArray(response.data) && response.data.length > 0) {
        setMappedProducts(response.data);
      } else {
        setError("No mapped products found.");
      }
    } catch (err) {
      setError("Error fetching mapped products: " + err.message);
    } finally {
      setLoading(false);
    }
  };

  const formatValue = (value) => {
    if (
      value === null ||
      value === undefined ||
      value === "" ||
      value !== value
    ) {
      return "N/A";
    }
    return value.toString();
  };

  // Define the specific column order
  const columnOrder = [
    "External",
    "Internal", // Rename to Predicted Internal
    "Method",
    "Semantic_Score",
    "Fallback_Internal",
    "Fallback_Semantic_Score",
  ];

  return (
    <div style={styles.content}>
      <h2 style={styles.header}>View the Mapped Products</h2>
      <p style={styles.subtitle}>
        Fetch the products and their mappings below. Data will be displayed in
        an organized table for easy review.
      </p>

      <button
        style={
          loading
            ? { ...styles.button, ...styles.buttonDisabled }
            : styles.button
        }
        onClick={fetchMappedProducts}
        disabled={loading}
      >
        {loading ? "Fetching..." : "Fetch Mapped Products"}
      </button>

      {loading && (
        <p style={styles.loadingMessage}>Loading mapped products...</p>
      )}
      {error && <p style={styles.error}>{error}</p>}
      {!loading && !error && mappedProducts.length > 0 && (
        <div style={styles.tableWrapper}>
          <table style={styles.table}>
            <thead>
              <tr>
                {columnOrder.map((key) => (
                  <th key={key} style={styles.th}>
                    {key === "Internal" ? "Predicted Internal" : key}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {mappedProducts.map((product, index) => (
                <tr key={index}>
                  {columnOrder.map((key) => (
                    <td key={key} style={styles.td}>
                      {formatValue(product[key])}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

const styles = {
  content: {
    backgroundColor: "#fff",
    borderRadius: "10px",
    boxShadow: "0 4px 8px rgba(0, 0, 0, 0.2)",
    padding: "30px",
    width: "95%",
    maxWidth: "1400px",
    textAlign: "center",
    margin: "20px auto",
    fontFamily: "'Arial', sans-serif",
  },
  header: {
    fontSize: "24px",
    fontWeight: "bold",
    marginBottom: "15px",
    color: "#333",
  },
  subtitle: {
    fontSize: "16px",
    color: "#555",
    marginBottom: "20px",
  },
  button: {
    padding: "10px 20px",
    fontSize: "16px",
    backgroundColor: "#007BFF",
    color: "white",
    border: "none",
    borderRadius: "5px",
    cursor: "pointer",
    transition: "background-color 0.3s ease, transform 0.2s ease",
  },
  buttonDisabled: {
    backgroundColor: "#0056b3",
    cursor: "not-allowed",
  },
  loadingMessage: {
    marginTop: "20px",
    fontSize: "16px",
    color: "#333",
  },
  tableWrapper: {
    width: "100%",
    marginTop: "20px",
    overflowX: "auto",
  },
  table: {
    width: "100%",
    borderCollapse: "collapse",
    border: "1px solid #ddd",
  },
  th: {
    backgroundColor: "#007BFF",
    color: "#fff",
    padding: "10px",
    border: "1px solid #ddd",
    textAlign: "left",
    fontWeight: "bold",
    textTransform: "capitalize",
  },
  td: {
    padding: "8px",
    border: "1px solid #ddd",
    textAlign: "left",
    color: "#333",
    backgroundColor: "#f9f9f9",
  },
  error: {
    color: "red",
    fontWeight: "bold",
    marginTop: "20px",
  },
};

export default ViewMapped;
