import React from "react";
import "./BackButton.css"; // optional, or put styles in main.css

export default function BackButton() {
  const handleBack = () => window.history.back(); // navigate to previous page

  return (
    <div className="back-button-container">
      <button className="back-button" onClick={handleBack}>
        ↼
      </button>
    </div>
  );
}
