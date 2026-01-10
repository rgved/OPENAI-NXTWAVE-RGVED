import { useState } from "react";
import { gradeAnswer, gradeFromFile, gradeFromDrive, gradeFromImage } from "./api";
import { jsPDF } from "jspdf";




export default function ExamGrader() {
  const [mode, setMode] = useState("text"); // text | file

  const [question, setQuestion] = useState("");
  const [studentAnswer, setStudentAnswer] = useState("");
  const [correctAnswer, setCorrectAnswer] = useState("");

  const [file, setFile] = useState(null);
  const [difficulty, setDifficulty] = useState("medium");
  const [maxScore, setMaxScore] = useState(5);

  const [driveLink, setDriveLink] = useState("");


  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const QUESTION_KEYWORDS = [
    "explain",
    "why",
    "what",
    "where",
    "when",
    "define",
    "justify",
    "how",
    "compare",
    "contrast",
    "describe",
    "discuss",
    "list",
    "state",
    "illustrate",
    "differentiate",
    "analyze",
    "evaluate"
  ];
  function detectQuestionAnswer(text) {
    if (!text) {
      return { question: "—", answer: "—" };
    }
  
    const lines = text
      .split("\n")
      .map(line => line.trim())
      .filter(Boolean);
  
    let questionLine = "";
    let answerLines = [];
    let foundQuestion = false;
  
    for (const line of lines) {
      const lower = line.toLowerCase();
  
      const isQuestion = QUESTION_KEYWORDS.some(keyword =>
        lower.startsWith(keyword) || lower.includes(` ${keyword} `)
      );
  
      if (isQuestion && !foundQuestion) {
        questionLine = line;
        foundQuestion = true;
      } else if (foundQuestion) {
        answerLines.push(line);
      }
    }
  
    return {
      question: questionLine || "Question could not be detected automatically.",
      answer: answerLines.join(" ") || "Answer could not be detected automatically."
    };
  }
    

  // ---------------------------------------
  const downloadResultPDF = () => {
    if (!result) return;
  
    const doc = new jsPDF();
  
    doc.setFontSize(16);
    doc.text("Exam Grading Result", 20, 20);
  
    doc.setFontSize(11);
    doc.text(`Difficulty: ${difficulty}`, 20, 35);
    doc.text(`Max Score: ${maxScore}`, 20, 42);
  
    doc.line(20, 48, 190, 48);
  
    doc.setFontSize(12);
    doc.text("Marks Summary", 20, 58);
  
    doc.setFontSize(11);
    doc.text("Sr No: 1", 20, 70);
    doc.text(`Question: ${result.question || "Submitted question"}`, 20, 78, { maxWidth: 170 });
    doc.text(`Answer: ${result.answer || file?.name || "Submitted answer"}`, 20, 95, { maxWidth: 170 });
    doc.text(`Marks Awarded: ${result.score} / ${maxScore}`, 20, 112);
  
    doc.line(20, 120, 190, 120);
  
    doc.setFontSize(12);
    doc.text("Feedback", 20, 132);
  
    doc.setFontSize(11);
    doc.text(result.feedback, 20, 140, { maxWidth: 170 });
  
    doc.save("exam_result.pdf");
  };
  
  // ---------------------------------------

  function extractDriveFileId(link) {
    // Works for full links and raw file IDs
    const match = link.match(/[-\w]{25,}/);
    return match ? match[0] : link;
  }
  const handleImageGrade = async () => {
    if (!file) {
      setError("Please upload an image");
      return;
    }
  
    try {
      setLoading(true);
      setError("");
      setResult(null);
  
      const res = await gradeFromImage(
        file,
        maxScore,
        difficulty
      );
  
      setResult(res);
    } catch (e) {
      console.error(e);
      setError("Image grading failed.");
    } finally {
      setLoading(false);
    }
  };
  
  
  const handleDriveGrade = async () => {
    if (!driveLink.trim()) return;

    try {
      setLoading(true);
      setResult(null);

      const fileId = extractDriveFileId(driveLink);

      const res = await gradeFromDrive(
        fileId,
        maxScore,
        difficulty
      );

      setResult(res);
    } catch (e) {
      console.error(e);
      alert("Failed to grade Drive file");
    } finally {
      setLoading(false);
    }
  };


  const handleGrade = async () => {
    setLoading(true);
    setError("");
    setResult(null);

    try {
      let res;

      if (mode === "text") {
        if (!question || !studentAnswer) {
          setError("Question and answer required");
          setLoading(false);
          return;
        }

        res = await gradeAnswer({
          question,
          student_answer: studentAnswer,
          correct_answer: correctAnswer,
          max_score: maxScore,
          difficulty,
        });
      } else {
        if (!file) {
          setError("Please upload a file");
          setLoading(false);
          return;
        }

        res = await gradeFromFile(file, maxScore, difficulty);
      }

      setResult(res);
    } catch (err) {
      setError("Grading failed. Try again.");
    } finally {
      setLoading(false);
    }
  };

  const detectedQA =
  result
    ? {
        question: result.question || question || "—",
        answer: result.student_answer || studentAnswer || "—"
      }
    : {
        question: question || "—",
        answer: studentAnswer || "—"
      };


  
  

  return (
    <div className="container">
      <h1>Exam Grader</h1>

      {/* MODE TABS */}
      <div className="tabs">
        <button onClick={() => setMode("text")}>✍️ Text</button>
        <button onClick={() => setMode("file")}>📂 File</button>
        <button onClick={() => setMode("drive")}>☁️ Google Drive</button>
        <button onClick={() => setMode("image")}>🖼️ Image</button>


      </div>

      {/* CONTROLS */}
      <select value={difficulty} onChange={(e) => setDifficulty(e.target.value)}>
        <option value="easy">Easy</option>
        <option value="medium">Medium</option>
        <option value="hard">Hard</option>
      </select>

      <input
        type="number"
        min="1"
        max="20"
        value={maxScore}
        onChange={(e) => setMaxScore(e.target.value)}
      />

      {/* TEXT MODE */}
      {mode === "text" && (
        <>
          <textarea
            placeholder="Question"
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
          />
          <textarea
            placeholder="Student Answer"
            value={studentAnswer}
            onChange={(e) => setStudentAnswer(e.target.value)}
          />
          <textarea
            placeholder="Correct Answer (optional)"
            value={correctAnswer}
            onChange={(e) => setCorrectAnswer(e.target.value)}
          />
        </>
      )}


      {/* FILE MODE */}
      {mode === "file" && (
        <div className="upload-box">
          <input
            type="file"
            accept=".pdf,.docx,.txt,.json"
            onChange={(e) => setFile(e.target.files[0])}
          />
          <p>{file ? `📄 ${file.name}` : "Upload answer file"}</p>
        </div>
      )}

{mode === "drive" && (
  <div className="upload-box">
    <input
      type="text"
      placeholder="Paste Google Drive File ID or Share Link"
      value={driveLink}
      onChange={(e) => setDriveLink(e.target.value)}
    />

    <button
      onClick={handleDriveGrade}
      disabled={loading || !driveLink.trim()}
    >
      {loading ? "Grading..." : "Grade from Drive"}
    </button>
  </div>
)}

{mode === "image" && (
  <>
    <div className="upload-box">
      <input
        type="file"
        accept="image/png,image/jpeg,image/jpg"
        onChange={(e) => setFile(e.target.files[0])}
      />

      <p>{file ? `🖼️ ${file.name}` : "Upload image answer"}</p>
    </div>

    {/* 👇 BUTTON IS OUTSIDE UPLOAD BOX */}
    <button
      onClick={handleImageGrade}
      disabled={!file || loading}
    >
      {loading ? "Grading..." : "Grade Image"}
    </button>
  </>
)}





{mode !== "drive" && mode !== "image" && (
  <button onClick={handleGrade} disabled={loading}>
    {loading ? "Grading..." : "Grade"}
  </button>
)}





      {/* <button onClick={handleGrade} disabled={loading}>
        {loading ? "Grading..." : "Grade"}
      </button> */}

      {error && <p style={{ color: "#f87171" }}>{error}</p>}

      {result && (

        
  <>
{/* ================= SUMMARY TABLE ================= */}
<div className="results summary">
  <h2>📊 Marks Summary</h2>

  <table className="summary-table">
    <tbody>
      <tr>
        <td><b>Detected Question: </b></td>
        <td>{result.question || detectedQA.question}</td>


      </tr>

      <tr>
      <td><b>Detected Answer</b></td>
        <td>{detectedQA.answer}</td>
      </tr>

      <tr>
        <td><b>Score</b></td>
        <td>{result.score} / {maxScore}</td>
      </tr>

      <tr>
        <td><b>Difficulty</b></td>
        <td>{difficulty}</td>
      </tr>

      <tr>
        <td><b>Evaluation</b></td>
        <td>
          {result.score >= maxScore * 0.8
            ? "Excellent"
            : result.score >= maxScore * 0.5
            ? "Good"
            : "Needs Improvement"}
        </td>
      </tr>
    </tbody>
  </table>
</div>



    {/* ================= DETAILED DROPDOWN ================= */}
    <details className="results details">
      <summary>📄 View Detailed Feedback</summary>

      <p style={{ marginTop: 16, lineHeight: 1.6 }}>
        {result.feedback}
      </p>
    </details>

    <button
  onClick={downloadResultPDF}
  style={{
    marginTop: "16px",
    padding: "10px 16px",
    backgroundColor: "#2563eb",
    color: "#fff",
    border: "none",
    borderRadius: "6px",
    cursor: "pointer"
  }}
>
  📥 Download PDF
</button>
<button onClick={() => window.location.href = "/dashboard"}>
  📊 View Dashboard
</button>



  </>
)}

    </div>
  );
}
