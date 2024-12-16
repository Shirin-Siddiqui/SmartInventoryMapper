import React, { useState } from "react";
import axios from "axios";

function MapProducts() {
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(false);
  const [timeTaken, setTimeTaken] = useState(null);

  const handleMapping = async () => {
    setLoading(true);
    setMessage("");
    setTimeTaken(null);

    const startTime = new Date();

    try {
      const response = await axios.post("http://127.0.0.1:5000/match");

      const endTime = new Date();
      const processingTime = ((endTime - startTime) / 1000).toFixed(2);

      setMessage(
        response.data.message || "Product mapping completed successfully."
      );
      setTimeTaken(processingTime);
    } catch (error) {
      setMessage("Error during product mapping: " + error.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={styles.content}>
      <h2 style={styles.header}>Map the Products</h2>
      <p style={styles.subtitle}>
        Your data was successfully embedded and preprocessed. Would you like to
        proceed with mapping the products?
      </p>

      <button
        style={
          loading
            ? { ...styles.button, ...styles.buttonDisabled }
            : styles.button
        }
        onClick={handleMapping}
        disabled={loading}
      >
        {loading ? "Mapping..." : "Start Mapping"}
      </button>

      {message && <p style={styles.message}>{message}</p>}
      {timeTaken && <p style={styles.time}>Time Taken: {timeTaken} seconds</p>}
    </div>
  );
}

const styles = {
  content: {
    backgroundColor: "#fff",
    borderRadius: "10px",
    boxShadow: "0 4px 8px rgba(0, 0, 0, 0.2)",
    padding: "30px",
    width: "90%",
    maxWidth: "600px",
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
  message: {
    marginTop: "20px",
    fontSize: "16px",
    color: "#28a745",
    fontWeight: "bold",
  },
  time: {
    marginTop: "10px",
    fontSize: "14px",
    color: "#555",
    fontStyle: "italic",
  },
};

export default MapProducts;
