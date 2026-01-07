import { useState } from "react";
import { getCompanionFeedback } from "./api";
import { getCompanionFromImage } from "./api";
import { getCompanionFromDrive } from "./api";

export default function StudentCompanion() {
  const [mode, setMode] = useState("text"); // text | file

  const [question, setQuestion] = useState("");
  const [studentAnswer, setStudentAnswer] = useState("");
  const [correctAnswer, setCorrectAnswer] = useState("");

  const [file, setFile] = useState(null);

  const [driveLink, setDriveLink] = useState("");


  const [fileName, setFileName] = useState("");
  const [uploadedFile, setUploadedFile] = useState(null);

  const [loading, setLoading] = useState(false);
  const [data, setData] = useState(null);
  const [error, setError] = useState("");


  function extractDriveFileId(link) {
    const match = link.match(/[-\w]{25,}/);
    return match ? match[0] : link;
  }
  

  const handleDriveGuidance = async () => {
    if (!driveLink.trim()) return;
  
    try {
      setLoading(true);
      setError("");
      setData(null);
  
      const fileId = extractDriveFileId(driveLink);
      const res = await getCompanionFromDrive(fileId);
  
      setData({
        feedback: res.feedback || "No feedback generated",
        keywords: res.keywords || [],
        improvement_steps: res.improvement_steps || [],
      });
    } catch (e) {
      console.error(e);
      setError("Failed to analyze Drive file.");
    } finally {
      setLoading(false);
    }
  };
    
  const handleImageGuidance = async () => {
    if (!file) return;
  
    try {
      setLoading(true);
      setData(null);
  
      const res = await getCompanionFromImage(file);
  
      setData({
        feedback: res.feedback || "No feedback generated",
        keywords: res.keywords || [],
        improvement_steps: res.improvement_steps || [],
      });
    } catch (e) {
      setError("Failed to analyze image.");
    } finally {
      setLoading(false);
    }
  };
  
  /* ---------- File Handling ---------- */
  const handleFileUpload = (file) => {
    if (!file) return;
  
    setUploadedFile(file);   // ✅ STORE FILE
    setFileName(file.name);
    setError("");
    setData(null);
  };
  

  /* ---------- Text Mode API Call ---------- */
  const handleGetGuidance = async () => {
    if (!question.trim() || !studentAnswer.trim()) {
      setError("Please enter both question and answer.");
      return;
    }

    setLoading(true);
    setError("");
    setData(null);

    try {
      const res = await getCompanionFeedback({
        question,
        student_answer: studentAnswer,
        correct_answer: correctAnswer || null,
      });

      setData({
        feedback: res?.feedback || "No feedback generated",
        keywords: Array.isArray(res?.keywords) ? res.keywords : [],
        improvement_steps: Array.isArray(res?.improvement_steps)
          ? res.improvement_steps
          : [],
      });
    } catch (err) {
      setError("Failed to fetch guidance. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container">
      <h1>🤝 Student Companion</h1>

      {/* MODE TABS */}
      <div className="tabs">
        <button
          className={mode === "text" ? "active" : ""}
          onClick={() => setMode("text")}
        >
          ✍️ Text Input
        </button>
        <button
          className={mode === "file" ? "active" : ""}
          onClick={() => setMode("file")}
        >
          📂 Upload File
        </button>
        <button
          className={mode === "image" ? "active" : ""}
          onClick={() => setMode("image")}
        >
          🖼️ Upload Image
        </button>

        <button
        className={mode === "drive" ? "active" : ""}
        onClick={() => setMode("drive")}
      >
        ☁️ Google Drive
      </button>

      </div>

      {/* ================= TEXT MODE ================= */}
      {mode === "text" && (
        <>
          <textarea
            placeholder="Question"
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
          />

          <textarea
            placeholder="Your Answer"
            value={studentAnswer}
            onChange={(e) => setStudentAnswer(e.target.value)}
          />

          <textarea
            placeholder="Correct Answer (optional)"
            value={correctAnswer}
            onChange={(e) => setCorrectAnswer(e.target.value)}
          />

          <button onClick={handleGetGuidance} disabled={loading}>
            {loading ? "Thinking..." : "Get Guidance"}
          </button>
        </>
      )}

      {/* ================= FILE MODE ================= */}
      {mode === "file" && (
        <>
          <div className="upload-box">
            <input
              type="file"
              accept=".txt,.pdf,.docx,.json"
              onChange={(e) => handleFileUpload(e.target.files[0])}
            />

            <p>
              {fileName
                ? `📄 Selected: ${fileName}`
                : "Click or drag a .txt, .pdf, .docx, or .json file here"}
            </p>

            <p style={{ opacity: 0.7, fontSize: "0.9rem", marginTop: 10 }}>
              Upload your answer file for AI-guided feedback.
            </p>
          </div>

          {/* SUBMIT FILE BUTTON */}
          <button
  disabled={!uploadedFile || loading}
  onClick={async () => {
    setLoading(true);
    setError("");

    try {
      const formData = new FormData();
      formData.append("file", uploadedFile);

      const res = await fetch("http://127.0.0.1:8000/companion/file", {
        method: "POST",
        body: formData,
      });

      if (!res.ok) throw new Error("Upload failed");

      const data = await res.json();
      setData(data);
    } catch (err) {
      setError("File submission failed.");
    } finally {
      setLoading(false);
    }
  }}
>
  {loading ? "Processing..." : "Submit File"}
</button>

        </>
      )}

{mode === "image" && (
  <>
    <div className="upload-box">
      <input
        type="file"
        accept="image/png,image/jpeg,image/jpg"
        onChange={(e) => setFile(e.target.files[0])}
      />

      <p>{file ? `🖼️ ${file.name}` : "Upload handwritten answer image"}</p>
    </div>

    <button
      onClick={handleImageGuidance}
      disabled={!file || loading}
    >
      {loading ? "Thinking..." : "Get Guidance from Image"}
    </button>
  </>
)}

{mode === "drive" && (
  <div className="upload-box">
    <input
      type="text"
      placeholder="Paste Google Drive file link or ID"
      value={driveLink}
      onChange={(e) => setDriveLink(e.target.value)}
    />

    <button
      type="button"
      onClick={handleDriveGuidance}
      disabled={loading || !driveLink.trim()}
    >
      {loading ? "Thinking..." : "Get Guidance from Drive"}
    </button>

    <p style={{ opacity: 0.7, marginTop: 8 }}>
      Supported: PDF, DOCX, TXT, JSON
    </p>
  </div>
)}


      {/* ================= RESULTS ================= */}
      {data && (
        <div className="results">
          <h2>📢 Feedback</h2>
          <p>{data.feedback}</p>

          <h3>🔑 Keywords</h3>
          {data.keywords.length ? (
            <p>{data.keywords.join(", ")}</p>
          ) : (
            <p>No keywords identified</p>
          )}

          <h3>🚀 Improvement Steps</h3>
          {data.improvement_steps.length ? (
            <ul>
              {data.improvement_steps.map((s, i) => (
                <li key={i}>{s}</li>
              ))}
            </ul>
          ) : (
            <p>No improvement steps suggested</p>
          )}
        </div>
      )}
    </div>
  );
}
