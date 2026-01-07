import React, { useState } from "react";
import { Routes, Route, useNavigate } from "react-router-dom";
import Snowfall from "react-snowfall";
import ExamGrader from "./ExamGrader";
import StudentCompanion from "./StudentCompanion";
import "./index.css";

export default function App() {
  const navigate = useNavigate();

  return (
    <Routes>
      {/* LANDING PAGE */}
      <Route
  path="/"
  element={
    <>
      <Snowfall
        snowflakeCount={80}
        color="#cbd5e1"
        style={{
          position: "fixed",
          width: "100vw",
          height: "100vh",
          zIndex: 0,
        }}
      />

      <div className="landing" style={{ position: "relative", zIndex: 1 }}>
        <h1 className="title">
          Welcome to <span>Xaminai</span>
        </h1>

        <p className="subtitle">Grader + Study Assistant</p>

        <div className="button-container">
          <button
            className="btn examiner"
            onClick={() => navigate("/examiner")}
          >
            ← Examiners This Way
          </button>

          <button
            className="btn student"
            onClick={() => navigate("/student")}
          >
            Students This Way →
          </button>
        </div>

        {/* NEW DEMO BUTTON */}
        <div style={{ marginTop: "40px" }}>
          <button
            className="btn"
            style={{
              background: "linear-gradient(135deg, #a78bfa, #6366f1)",
              color: "#020617",
              minWidth: "300px",
            }}
            onClick={() =>
              window.open(
                "https://3d6192310b29.ngrok-free.app",
                "_blank"
              )
            }
          >
            Proceed to Demo →
          </button>
        </div>
      </div>
    </>
  }
/>


      {/* EXAM GRADER PAGE */}
      <Route path="/examiner" element={<ExamGrader />} />

      {/* STUDENT PAGE */}
      <Route path="/student" element={<StudentCompanion />} />
    </Routes>
  );
}
