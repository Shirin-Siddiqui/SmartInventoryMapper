import React, { useState } from "react";
import axios from "axios";

function Preprocess() {
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(false);
  const [timeTaken, setTimeTaken] = useState(null);

  const handlePreprocess = async () => {
    setLoading(true);
    setMessage("");
    setTimeTaken(null);
    const startTime = new Date();

    try {
      const response = await axios.post("http://127.0.0.1:5000/preprocess");

      const endTime = new Date();
      const processingTime = ((endTime - startTime) / 1000).toFixed(2);
      setTimeTaken(processingTime);

      setMessage(response.data.message || "Preprocessing completed.");
    } catch (error) {
      setMessage("Error during preprocessing: " + error.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={styles.container}>
      <h1 style={styles.title}>Preprocess & Embed Data</h1>
      <p style={styles.subtitle}>
        Your data has been uploaded. Would you like to proceed with data
        preprocessing and embedding?
      </p>

      <button
        style={
          loading
            ? { ...styles.button, ...styles.buttonDisabled }
            : styles.button
        }
        onClick={handlePreprocess}
        disabled={loading}
      >
        {loading ? "Processing..." : "Start Preprocessing"}
      </button>

      {message && <p style={styles.message}>{message}</p>}
      {timeTaken && <p style={styles.time}>Time Taken: {timeTaken} seconds</p>}
    </div>
  );
}

const styles = {
  container: {
    background: "#f9f9f9",
    borderRadius: "10px",
    boxShadow: "0 4px 8px rgba(0, 0, 0, 0.1)",
    padding: "30px 20px",
    width: "80%",
    maxWidth: "500px",
    textAlign: "center",
    margin: "40px auto",
    fontFamily: "'Arial', sans-serif",
  },
  title: {
    fontSize: "24px",
    fontWeight: "bold",
    color: "#333",
    marginBottom: "15px",
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
    color: "green",
    fontWeight: "bold",
  },
  time: {
    marginTop: "10px",
    fontSize: "14px",
    color: "#555",
    fontStyle: "italic",
  },
};

export default Preprocess;
