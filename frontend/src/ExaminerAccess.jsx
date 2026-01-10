import { useState } from "react";
import { useNavigate } from "react-router-dom";

export default function ExaminerAccess() {
  const navigate = useNavigate();
  const [accessCode, setAccessCode] = useState("");
  const [error, setError] = useState("");

  const handleSubmit = (e) => {
    e.preventDefault();
    setError("");

    // 🔒 Demo-only access code
    if (accessCode === "1234") {
      navigate("/examiner");
    } else {
      setError("Invalid access code. Faculty-only access.");
    }
  };

  return (
    <div className="container">
      <h1>Examiner Verification</h1>
      <p style={{ marginBottom: "20px" }}>
        This section is restricted to verified faculty & examiners.
      </p>

      <form onSubmit={handleSubmit} className="security-form">
        <input
          type="password"
          placeholder="Enter Examiner Access Code"
          value={accessCode}
          onChange={(e) => setAccessCode(e.target.value)}
          required
        />

        {error && <p style={{ color: "#f87171" }}>{error}</p>}

        <button className="btn examiner" type="submit">
          Verify & Proceed →
        </button>
      </form>
    </div>
  );
}
