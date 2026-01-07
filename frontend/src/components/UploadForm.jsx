import React, { useState } from 'react';
import { postJSON, postFile } from '../api';

export default function UploadForm({ onResult }) {
  const [mode, setMode] = useState('text'); // 'text' or 'file'
  const [question, setQuestion] = useState('');
  const [studentAnswer, setStudentAnswer] = useState('');
  const [file, setFile] = useState(null);
  const [difficulty, setDifficulty] = useState('medium');
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');

  async function handleSubmitText(e) {
    e.preventDefault();
    if (!question || !studentAnswer) {
      setMessage('Please enter both question and student answer.');
      return;
    }
    setMessage('');
    setLoading(true);
    try {
      const payload = {
        questions: [{
          question_id: 'Q1',
          question,
          student_answer: studentAnswer,
          correct_answer: '',
          max_score: 5
        }],
        difficulty
      };
      const resp = await postJSON('/grade', payload);
      setLoading(false);
      if (resp.ok) {
        onResult(resp.results);
      } else {
        setMessage(resp.error || 'Unexpected error');
      }
    } catch (err) {
      setLoading(false);
      setMessage(err.message || 'Network error');
    }
  }

  async function handleSubmitFile(e) {
    e.preventDefault();
    if (!file) {
      setMessage('Please select a file to upload.');
      return;
    }
    setMessage('');
    setLoading(true);
    try {
      const form = new FormData();
      form.append('file', file);
      form.append('difficulty', difficulty);
      const resp = await postFile('/grade-file', form);
      setLoading(false);
      if (resp.ok) {
        onResult(resp.results);
      } else {
        setMessage(resp.error || 'Unexpected error');
      }
    } catch (err) {
      setLoading(false);
      setMessage(err.message || 'Network error');
    }
  }

  return (
    <div>
      <div style={{display:'flex', gap:10, marginBottom:12}}>
        <label style={{display:'flex', alignItems:'center', gap:8}}>
          <input type="radio" checked={mode==='text'} onChange={()=>setMode('text')} /> Text
        </label>
        <label style={{display:'flex', alignItems:'center', gap:8}}>
          <input type="radio" checked={mode==='file'} onChange={()=>setMode('file')} /> File
        </label>
        <select value={difficulty} onChange={e=>setDifficulty(e.target.value)} style={{marginLeft:'auto'}}>
          <option value="easy">Easy</option>
          <option value="medium">Medium</option>
          <option value="hard">Hard</option>
        </select>
      </div>

      {mode === 'text' ? (
        <form onSubmit={handleSubmitText}>
          <div className="form-row">
            <label className="small">Question</label>
            <textarea value={question} onChange={e=>setQuestion(e.target.value)} />
          </div>
          <div className="form-row">
            <label className="small">Student Answer</label>
            <textarea value={studentAnswer} onChange={e=>setStudentAnswer(e.target.value)} />
          </div>
          <div style={{display:'flex', gap:10}}>
            <button disabled={loading} type="submit">{loading ? 'Grading...' : 'Grade Answer'}</button>
            <button type="button" onClick={()=>{ setQuestion(''); setStudentAnswer(''); }}>Reset</button>
          </div>
        </form>
      ) : (
        <form onSubmit={handleSubmitFile}>
          <div className="form-row">
            <input type="file" accept=".pdf,.docx,.json,.txt" onChange={(e)=>setFile(e.target.files[0])} />
          </div>
          <div style={{display:'flex', gap:10}}>
            <button disabled={loading} type="submit">{loading ? 'Grading file...' : 'Upload & Grade'}</button>
            <button type="button" onClick={()=>setFile(null)}>Clear</button>
          </div>
        </form>
      )}

      {message && <div style={{color:'crimson', marginTop:10}}>{message}</div>}
      <div style={{marginTop:12}} className="small">
        Tip: for Colab backend set VITE_API_URL to your ngrok URL (eg. https://abcd1234.ngrok.io)
      </div>
    </div>
  );
}
