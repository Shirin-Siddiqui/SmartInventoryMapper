import React, { useState } from "react";
import "./App.css"; // Import the CSS for styling
import FileUpload from "./components/FileUpload";
import Preprocess from "./components/Preprocess";
import MapProducts from "./components/MapProducts";
import ViewMapped from "./components/ViewMapped";
import CheckAccuracy from "./components/CheckAccuracy";

function App() {
  const [activeView, setActiveView] = useState("fileUpload");

  const renderView = () => {
    switch (activeView) {
      case "preprocess":
        return <Preprocess />;
      case "mapProducts":
        return <MapProducts />;
      case "viewMapped":
        return <ViewMapped />;
      case "checkAccuracy":
        return <CheckAccuracy />;
      default:
        return <FileUpload />;
    }
  };

  return (
    <div style={styles.container}>
      {/* Title */}
      <h1 style={styles.title}>Smart Inventory Mapper</h1>

      {/* Navigation Bar */}
      <nav style={styles.navbar}>
        {[
          { name: "File Upload", view: "fileUpload" },
          { name: "Preprocess & Embed Data", view: "preprocess" },
          { name: "Map the Products", view: "mapProducts" },
          { name: "View the Mapped Products", view: "viewMapped" },
          { name: "Check Accuracy", view: "checkAccuracy" },
        ].map((item) => (
          <button
            key={item.view}
            style={{
              ...styles.navButton,
              ...(activeView === item.view && styles.navButtonActive),
            }}
            onClick={() => setActiveView(item.view)}
          >
            {item.name}
          </button>
        ))}
      </nav>

      {/* Render Selected View */}
      {renderView()}
    </div>
  );
}

const styles = {
  container: {
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
    justifyContent: "flex-start",
    minHeight: "100vh", // Use minHeight instead of height
    background: "linear-gradient(135deg, #FFA500, #FF6700)", // Keep the gradient background
    padding: "20px",
  },
  title: {
    fontSize: "48px",
    fontWeight: "bold",
    color: "#fff",
    marginBottom: "20px", // Reduce margin to make it closer to the navbar
    textAlign: "center",
    fontFamily: "'Roboto', sans-serif",
    textShadow: "2px 2px 4px rgba(0, 0, 0, 0.3)",
  },
  navbar: {
    display: "flex",
    gap: "15px",
    marginBottom: "20px",
    backgroundColor: "#333",
    padding: "10px 20px",
    borderRadius: "8px",
  },
  navButton: {
    padding: "10px 20px",
    backgroundColor: "#555",
    color: "#fff",
    border: "none",
    borderRadius: "5px",
    cursor: "pointer",
    fontSize: "16px",
    fontWeight: "bold",
    transition: "background-color 0.3s ease, transform 0.2s ease",
  },
  navButtonActive: {
    backgroundColor: "#FFA500",
    transform: "scale(1.1)",
  },
};

export default App;
