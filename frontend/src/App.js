import React from "react";
import "./App.css"; // Import the CSS for styling
import FileUpload from "./components/FileUpload";

function App() {
  return (
    // Add the return statement to render the JSX
    <div style={styles.container}>
      {/* Title */}
      <h1 style={styles.title}>Smart Inventory Mapper</h1>

      {/* Render the FileUpload component */}
      <FileUpload />
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
  title: {
    fontSize: "48px", // Large title size
    fontWeight: "bold", // Make it bold
    color: "#333", // Dark color for the title
    marginBottom: "40px", // Add some space between title and content
    textAlign: "center", // Center the title
    fontFamily: "'Roboto', sans-serif", // Font choice
  },
};

export default App;
