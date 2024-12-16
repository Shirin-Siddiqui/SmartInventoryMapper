import React, { useState } from "react";
import axios from "axios";

function FileUpload() {
  const [file1, setFile1] = useState(null);
  const [file2, setFile2] = useState(null);
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(false);

  // Handle file input changes
  const handleFileChange1 = (e) => {
    setFile1(e.target.files[0]);
  };

  const handleFileChange2 = (e) => {
    setFile2(e.target.files[0]);
  };

  // Handle form submission
  const handleUpload = async () => {
    if (!file1 || !file2) {
      setMessage("Please select both CSV files.");
      return;
    }

    const formData = new FormData();
    formData.append("file1", file1);
    formData.append("file2", file2);

    setLoading(true);
    try {
      const response = await axios.post(
        "http://127.0.0.1:5000/upload",
        formData,
        {
          headers: {
            "Content-Type": "multipart/form-data",
          },
        }
      );

      setMessage(response.data.message);
    } catch (error) {
      setMessage("Error uploading files.");
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={styles.container}>
      <h2 style={styles.header}>
        Upload the External and Internal Product List
      </h2>

      <div style={styles.fileInputContainer}>
        <div style={styles.inputWrapper}>
          <label htmlFor="internalFile" style={styles.label}>
            Internal Product List:
          </label>
          <input
            id="internalFile"
            type="file"
            accept=".csv"
            onChange={handleFileChange1}
            style={styles.fileInput}
          />
        </div>

        <div style={styles.inputWrapper}>
          <label htmlFor="externalFile" style={styles.label}>
            External Product List:
          </label>
          <input
            id="externalFile"
            type="file"
            accept=".csv"
            onChange={handleFileChange2}
            style={styles.fileInput}
          />
        </div>
      </div>

      <button
        onClick={handleUpload}
        style={styles.uploadButton}
        disabled={loading}
      >
        {loading ? "Processing ..." : "Upload Files"}
      </button>

      {message && <p style={styles.message}>{message}</p>}
    </div>
  );
}

const styles = {
  container: {
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
    justifyContent: "center",
    padding: "20px",
  },
  header: {
    fontSize: "24px",
    marginBottom: "20px",
    fontWeight: "bold",
    color: "#333",
  },
  fileInputContainer: {
    display: "flex",
    justifyContent: "center",
    alignItems: "center",
    gap: "40px",
    marginBottom: "20px",
  },
  inputWrapper: {
    padding: "20px",
    borderRadius: "10px",
    boxShadow: "0 4px 8px rgba(0, 0, 0, 0.1)",
    backgroundColor: "#fff",
    textAlign: "center",
    flex: "1",
    maxWidth: "250px",
  },
  label: {
    fontSize: "18px",
    marginBottom: "10px",
    fontWeight: "bold",
    color: "#555",
    display: "block",
  },
  fileInput: {
    padding: "10px",
    borderRadius: "5px",
    border: "1px solid #ccc",
    width: "100%",
    boxSizing: "border-box",
    outline: "none",
    transition: "border-color 0.3s ease",
  },
  uploadButton: {
    padding: "10px 20px",
    fontSize: "16px",
    backgroundColor: "#4CAF50",
    color: "white",
    border: "none",
    borderRadius: "5px",
    cursor: "pointer",
    transition: "background-color 0.3s ease",
  },
  message: {
    marginTop: "20px",
    fontSize: "16px",
    color: "green",
  },
};

export default FileUpload;
