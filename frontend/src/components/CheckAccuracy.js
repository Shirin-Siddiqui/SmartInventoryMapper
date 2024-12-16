import React, { useState } from "react";
import axios from "axios";

function CheckAccuracy() {
  const [file, setFile] = useState(null);
  const [accuracyScore, setAccuracyScore] = useState(null);
  const [results, setResults] = useState([]);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
    setError("");
    setAccuracyScore(null);
    setResults([]);
  };

  const handleUpload = async () => {
    if (!file) {
      setError("Please upload a CSV file.");
      return;
    }

    setLoading(true);
    setError("");
    setAccuracyScore(null);
    setResults([]);

    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await axios.post(
        "http://127.0.0.1:5000/check-accuracy",
        formData,
        {
          headers: {
            "Content-Type": "multipart/form-data",
          },
        }
      );

      setAccuracyScore(response.data.accuracy);
      setResults(response.data.results);
    } catch (err) {
      setError("Error checking accuracy: " + err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={styles.content}>
      <h2 style={styles.header}>Check Accuracy</h2>
      <p style={styles.subtitle}>
        Upload a CSV file to check accuracy against the mapped products.
      </p>

      {/* File Upload */}
      <input
        type="file"
        accept=".csv"
        onChange={handleFileChange}
        style={styles.input}
      />
      <button style={styles.button} onClick={handleUpload} disabled={loading}>
        {loading ? "Checking..." : "Upload & Check Accuracy"}
      </button>

      {error && <p style={styles.error}>{error}</p>}
      {accuracyScore !== null && (
        <div style={styles.result}>
          <h3 style={styles.score}>Accuracy Score: {accuracyScore}%</h3>
          <table style={styles.table}>
            <thead>
              <tr>
                <th style={styles.th}>External</th>
                <th style={styles.th}>Actual Internal</th>
                <th style={styles.th}>Predicted Internal</th>
                <th style={styles.th}>Match Status</th>
              </tr>
            </thead>
            <tbody>
              {results.map((result, index) => (
                <tr key={index}>
                  <td style={styles.td}>{result.external}</td>
                  <td style={styles.td}>{result.actual_internal}</td>
                  <td style={styles.td}>{result.predicted_internal}</td>
                  <td
                    style={{
                      ...styles.td,
                      color: result.status === "Correct" ? "green" : "red",
                      fontWeight: "bold",
                    }}
                  >
                    {result.status}
                  </td>
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
    width: "90%",
    maxWidth: "900px",
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
  input: {
    margin: "10px 0",
  },
  button: {
    padding: "10px 20px",
    fontSize: "16px",
    backgroundColor: "#007BFF",
    color: "white",
    border: "none",
    borderRadius: "5px",
    cursor: "pointer",
    transition: "background-color 0.3s ease",
    marginTop: "10px",
  },
  error: {
    marginTop: "15px",
    color: "red",
    fontWeight: "bold",
  },
  result: {
    marginTop: "20px",
    textAlign: "left",
  },
  score: {
    fontSize: "18px",
    color: "#28a745",
    marginBottom: "10px",
  },
  table: {
    width: "100%",
    borderCollapse: "collapse",
    marginTop: "10px",
  },
  th: {
    backgroundColor: "#007BFF",
    color: "white",
    padding: "10px",
    border: "1px solid #ddd",
  },
  td: {
    padding: "8px",
    border: "1px solid #ddd",
    textAlign: "left",
  },
};

export default CheckAccuracy;
