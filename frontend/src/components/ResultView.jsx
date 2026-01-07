import React from 'react';

export default function ResultView({ results }) {
  if (!results || results.length === 0) return null;

  // results is expected to be array of question results
  return (
    <div style={{marginTop:18}}>
      <h3>Results</h3>
      <div style={{marginTop:10}}>
        {results.map((q, idx) => (
          <div key={idx} className="result-card">
            <div style={{display:'flex', justifyContent:'space-between', alignItems:'center'}}>
              <div><strong>Q{idx+1}</strong> <span className="kv">({q.max_score} marks)</span></div>
              <div><strong>{q.model_score ?? q.final_score ?? '0'}</strong></div>
            </div>
            <div style={{marginTop:8}}>
              <div><strong>Question:</strong> {q.question}</div>
              <div className="small"><strong>Answer:</strong> {q.student_answer}</div>
              {q.correct_answer ? <div className="small"><strong>Model answer:</strong> {q.correct_answer}</div> : null}
              <div style={{marginTop:8}}><strong>Feedback:</strong> {q.feedback || 'No feedback'}</div>
              {q.improvement_steps && q.improvement_steps.length>0 && (
                <div style={{marginTop:6}}>
                  <strong>Improve:</strong>
                  <ul>
                    {q.improvement_steps.map((s,i)=>(<li key={i} className="small">{s}</li>))}
                  </ul>
                </div>
              )}
              {q.keywords && q.keywords.length>0 && <div className="small" style={{marginTop:6}}>Keywords: {q.keywords.join(', ')}</div>}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
