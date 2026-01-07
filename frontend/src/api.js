const BASE_URL = "http://127.0.0.1:8000";

/* =========================
   STUDENT COMPANION (TEXT)
   ========================= */
export async function getCompanionFeedback(payload) {
  const res = await fetch(`${BASE_URL}/companion`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });

  if (!res.ok) {
    throw new Error("Companion API request failed");
  }

  return await res.json();
}

/* =========================
   EXAM GRADER (TEXT MODE)
   ========================= */
export async function gradeAnswer(payload) {
  const res = await fetch(`${BASE_URL}/grade`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });

  if (!res.ok) {
    throw new Error("Grade API request failed");
  }

  return await res.json();
}

/* =========================
   EXAM GRADER (FILE MODE)
   ========================= */
export async function gradeFromFile(file, maxScore, difficulty) {
  const formData = new FormData();
  formData.append("file", file);

  const res = await fetch(
    `${BASE_URL}/grade/file?max_score=${maxScore}&difficulty=${difficulty}`,
    {
      method: "POST",
      body: formData,
    }
  );

  if (!res.ok) {
    throw new Error("File grading failed");
  }

  return await res.json();
}

export async function gradeFromDrive(fileId, maxScore, difficulty) {
  const res = await fetch(
    `http://127.0.0.1:8000/grade/drive?file_id=${fileId}&max_score=${maxScore}&difficulty=${difficulty}`,
    { method: "POST" }
  );

  if (!res.ok) throw new Error("Drive grading failed");
  return res.json();
}


export async function gradeFromImage(file, maxScore, difficulty) {
  const formData = new FormData();
  formData.append("file", file);

  const res = await fetch(
    `http://127.0.0.1:8000/grade/image?max_score=${maxScore}&difficulty=${difficulty}`,
    {
      method: "POST",
      body: formData,
    }
  );

  if (!res.ok) throw new Error("Image grading failed");
  return res.json();
}

export async function getCompanionFromImage(file) {
  const formData = new FormData();
  formData.append("file", file);

  const res = await fetch(
    "http://127.0.0.1:8000/companion/image",
    {
      method: "POST",
      body: formData,
    }
  );

  if (!res.ok) throw new Error("Image companion failed");
  return res.json();
}

export async function getCompanionFromDrive(fileId) {
  const res = await fetch(
    `http://127.0.0.1:8000/companion/drive?file_id=${fileId}`,
    {
      method: "POST",
    }
  );

  if (!res.ok) {
    throw new Error("Drive companion failed");
  }

  return res.json();
}
