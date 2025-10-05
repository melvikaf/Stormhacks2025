import React from "react";
import "./BackButton.css"; 

export default function BackButton() {
  const handleBack = () => window.history.back();

  return (
    <div className="back-button-container">
      <button className="back-button" onClick={handleBack}>
        ↼
      </button>
    </div>
  );
}
