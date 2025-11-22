import React from 'react';
import './GradingResults.css';

const GradingResults = () => {
  // Dummy variables - these will be populated from backend later
  const overallScore = 78; // This will come from backend
  const totalDuration = 45; // seconds - from backend
  const wordCount = 156; // from backend
  
  // Dummy criteria scores - will be populated from backend
  const criteriaScores = [
    { 
      category: 'Content & Structure',
      metrics: [
        { name: 'Salutation Level', score: 4, maxScore: 5, feedback: 'Good opening greeting' },
        { name: 'Keyword Presence', score: 25, maxScore: 30, feedback: 'Most key elements included (name, background, interests)' },
        { name: 'Flow & Structure', score: 4, maxScore: 5, feedback: 'Logical sequence maintained' }
      ]
    },
    {
      category: 'Speech Rate',
      metrics: [
        { name: 'Speech Rate (words/min)', score: 8, maxScore: 10, feedback: '208 words/minute - Optimal pace' }
      ]
    },
    {
      category: 'Language & Grammar',
      metrics: [
        { name: 'Grammar Accuracy', score: 9, maxScore: 10, feedback: '2 minor grammar errors detected' },
        { name: 'Vocabulary Richness', score: 7, maxScore: 10, feedback: 'Good variety of vocabulary used' }
      ]
    },
    {
      category: 'Clarity',
      metrics: [
        { name: 'Filler Word Rate', score: 12, maxScore: 15, feedback: 'Minimal use of filler words' }
      ]
    },
    {
      category: 'Engagement',
      metrics: [
        { name: 'Sentiment & Positivity', score: 13, maxScore: 15, feedback: 'Positive and engaging tone' }
      ]
    }
  ];

  // Calculate total max score
  const totalMaxScore = criteriaScores.reduce((total, category) => {
    return total + category.metrics.reduce((catTotal, metric) => catTotal + metric.maxScore, 0);
  }, 0);

  // Generate remark based on score
  const getRemark = (score) => {
    if (score >= 90) return 'Excellent! Outstanding communication skills';
    if (score >= 80) return 'Very Good! Strong communication abilities';
    if (score >= 70) return 'Good! Solid performance with some areas for improvement';
    if (score >= 60) return 'Satisfactory. Keep working on your skills';
    return 'Needs improvement. Focus on key areas highlighted';
  };

  return (
    <div className="grading-results">
      <div className="results-header">
        <h1>Communication Skills Assessment</h1>
        <p>Detailed breakdown of your self-introduction evaluation</p>
      </div>

      {/* Overall Score Card */}
      <div className="overall-score-card">
        <div className="score-circle">
          <div className="score-value">{overallScore}</div>
          <div className="score-label">Overall Score</div>
        </div>
        <div className="score-details">
          <div className="detail-item">
            <span className="detail-label">Word Count:</span>
            <span className="detail-value">{wordCount} words</span>
          </div>
          <div className="detail-item">
            <span className="detail-label">Duration:</span>
            <span className="detail-value">{totalDuration} seconds</span>
          </div>
          <div className="detail-item">
            <span className="detail-label">Speech Rate:</span>
            <span className="detail-value">~{Math.round((wordCount / totalDuration) * 60)} wpm</span>
          </div>
        </div>
      </div>

      {/* Criteria Breakdown */}
      <div className="criteria-breakdown">
        <h2>Detailed Assessment</h2>
        
        {criteriaScores.map((category, categoryIndex) => (
          <div key={categoryIndex} className="category-section">
            <h3 className="category-title">{category.category}</h3>
            
            {category.metrics.map((metric, metricIndex) => {
              const percentage = (metric.score / metric.maxScore) * 100;
              return (
                <div key={metricIndex} className="metric-card">
                  <div className="metric-header">
                    <div className="metric-name">
                      <span>{metric.name}</span>
                      <span className="metric-weight">Weight: {metric.maxScore}%</span>
                    </div>
                    <div className="metric-score">
                      {metric.score}/{metric.maxScore}
                    </div>
                  </div>
                  
                  <div className="progress-bar">
                    <div 
                      className="progress-fill"
                      style={{ width: `${percentage}%` }}
                    ></div>
                  </div>
                  
                  <div className="metric-feedback">
                    {metric.feedback}
                  </div>
                </div>
              );
            })}
          </div>
        ))}
      </div>

      {/* Final Summary */}
      <div className="final-summary">
        <div className="total-score">
          <div className="total-score-value">
            {overallScore}<span className="total-out-of">/{totalMaxScore}</span>
          </div>
          <div className="total-score-label">Final Score</div>
        </div>
        
        <div className="remarks-section">
          <h3>Remarks</h3>
          <p className="remarks-text">{getRemark(overallScore)}</p>
          <div className="improvement-tips">
            <h4>Areas for Improvement:</h4>
            <ul>
              <li>Include all key personal information (name, background, interests, goals)</li>
              <li>Maintain consistent speech pace</li>
              <li>Reduce filler words for better clarity</li>
              <li>Use more varied vocabulary</li>
            </ul>
          </div>
        </div>
      </div>

      <div className="action-buttons">
        <button className="btn-primary">Download Report</button>
        <button className="btn-secondary">Try Another Introduction</button>
      </div>
    </div>
  );
};

export default GradingResults;