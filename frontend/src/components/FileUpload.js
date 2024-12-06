import React, { useState } from "react";
import axios from "axios";

function FileUpload() {
  const [file1, setFile1] = useState(null);
  const [file2, setFile2] = useState(null);
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(false);
  const [downloadUrl, setDownloadUrl] = useState(""); // Store the download URL for the final file

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
            "Content-Type": "multipart/form-data", // Ensure this is set
          },
        }
      );

      setMessage(response.data.message);

      const filePath = response.data.results_file; // Get the correct file path
      const fileName = filePath.split("/").pop(); // Extract file name
      setDownloadUrl(`http://127.0.0.1:5000/download/${fileName}`); // Construct download URL

      // Trigger automatic download
      const link = document.createElement("a");
      link.href = `http://127.0.0.1:5000/download/${fileName}`;
      link.download = fileName;
      link.click(); // Simulate click to trigger download
    } catch (error) {
      setMessage("Error uploading files.");
      console.error(error); // Check for specific errors
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={styles.container}>
      <h2 style={styles.header}>
        Upload the External and Internal Product List
      </h2>

      {/* File input section displayed side by side */}
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
        {loading ? "Processing ..." : "Start Mapping"}
      </button>

      {message && <p style={styles.message}>{message}</p>}

      {/* Download Button */}
      {downloadUrl && (
        <div>
          <a href={downloadUrl} download>
            <button style={styles.downloadButton}>
              Download Final Product List
            </button>
          </a>
        </div>
      )}
    </div>
  );
}

const styles = {
  container: {
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
    justifyContent: "center",
    height: "100vh",
    backgroundColor: "#f0f0f0",
    padding: "20px",
  },
  header: {
    fontSize: "24px",
    marginBottom: "20px",
  },
  fileInputContainer: {
    display: "flex", // Flexbox to align items side by side
    justifyContent: "center", // Center items horizontally
    marginBottom: "20px",
  },
  inputWrapper: {
    margin: "0 20px", // Space between the two file input blocks
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
  },
  label: {
    fontSize: "18px",
    marginBottom: "10px",
    color: "#333",
  },
  fileInput: {
    padding: "10px",
    margin: "10px",
    borderRadius: "5px",
    border: "1px solid #ccc",
  },
  uploadButton: {
    padding: "10px 20px",
    fontSize: "16px",
    backgroundColor: "#4CAF50",
    color: "white",
    border: "none",
    borderRadius: "5px",
    cursor: "pointer",
    marginBottom: "20px",
  },
  message: {
    marginTop: "20px",
    fontSize: "16px",
    color: "green",
  },
  downloadButton: {
    padding: "10px 20px",
    fontSize: "16px",
    backgroundColor: "#2196F3", // Blue color for the download button
    color: "white",
    border: "none",
    borderRadius: "5px",
    cursor: "pointer",
    marginTop: "20px",
  },
};

export default FileUpload;
