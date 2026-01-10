import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

const BASE_URL = "http://localhost:8000";

export default function Dashboard() {
  const [history, setHistory] = useState([]);
  const [modeFilter, setModeFilter] = useState("");
  const navigate = useNavigate();

  const fetchHistory = async () => {
    const url = new URL(`${BASE_URL}/dashboard/history`);
    if (modeFilter) url.searchParams.append("mode", modeFilter);

    const res = await fetch(url);
    const data = await res.json();
    setHistory(data);
  };

  useEffect(() => {
    fetchHistory();
  }, [modeFilter]);

  const exportCSV = () => {
    const url = new URL(`${BASE_URL}/dashboard/export`);
    if (modeFilter) url.searchParams.append("mode", modeFilter);
    window.open(url, "_blank");
  };

  return (
    <div className="container">
      {/* HEADER */}
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          marginBottom: "16px",
        }}
      >
        <h1>📊 Grading Dashboard</h1>

        <button
          onClick={() => navigate("/examiner")}
          style={{
            padding: "8px 14px",
            borderRadius: "6px",
            border: "1px solid #475569",
            background: "#020617",
            color: "#e5e7eb",
            cursor: "pointer",
          }}
        >
          ← Back to Grading
        </button>
      </div>

      {/* FILTER CONTROLS */}
      <div style={{ display: "flex", gap: "12px", marginBottom: "16px" }}>
        <select
          value={modeFilter}
          onChange={(e) => setModeFilter(e.target.value)}
        >
          <option value="">All Modes</option>
          <option value="text">Text</option>
          <option value="file">File</option>
          <option value="image">Image</option>
          <option value="drive">Drive</option>
        </select>

        <button onClick={exportCSV}>📥 Export CSV</button>
      </div>

      {/* HISTORY TABLE */}
      <table className="summary-table">
        <thead>
          <tr>
            <th>Question</th>
            <th>Score</th>
            <th>Difficulty</th>
            <th>Mode</th>
            <th>Date</th>
          </tr>
        </thead>

        <tbody>
          {history.map((item) => (
            <tr key={item.id}>
              <td>{item.question}</td>
              <td>
                {item.score} / {item.max_score}
              </td>
              <td>{item.difficulty}</td>
              <td>{item.mode}</td>
              <td>{new Date(item.created_at).toLocaleString()}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
