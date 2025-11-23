import React from 'react';
import { useNavigate } from 'react-router-dom'; // Import useNavigate
import './GradingResults.css';

const GradingResults = ({ results, onTryAgain }) => {
  const navigate = useNavigate(); // Add this hook

  // Use results from props or fallback to empty state
  const {
    overallScore = 0,
    totalDuration = 0,
    wordCount = 0,
    speechRate = 0,
    criteriaScores = []
  } = results || {};

  // Calculate total max score from criteria
  const totalMaxScore = criteriaScores.reduce((total, category) => {
    return total + category.metrics.reduce((catTotal, metric) => catTotal + metric.maxScore, 0);
  }, 0) || 100;

  // Generate remark based on score
  const getRemark = (score) => {
    if (score >= 90) return 'Excellent! Outstanding communication skills';
    if (score >= 80) return 'Very Good! Strong communication abilities';
    if (score >= 70) return 'Good! Solid performance with some areas for improvement';
    if (score >= 60) return 'Satisfactory. Keep working on your skills';
    return 'Needs improvement. Focus on key areas highlighted';
  };

  // Generate improvement tips based on scores
  const getImprovementTips = (scores) => {
    const tips = [];
    
    if (!scores || scores.length === 0) {
      return [
        'Include all key personal information (name, background, interests, goals)',
        'Maintain consistent speech pace',
        'Reduce filler words for better clarity',
        'Use more varied vocabulary'
      ];
    }

    // Check keyword presence score
    const keywordMetric = scores
      .flatMap(cat => cat.metrics)
      .find(metric => metric.name.includes('Keyword'));
    
    if (keywordMetric && keywordMetric.score < keywordMetric.maxScore * 0.7) {
      tips.push('Include more key personal information (name, background, interests, goals)');
    }

    // Check speech rate
    const speechMetric = scores
      .flatMap(cat => cat.metrics)
      .find(metric => metric.name.includes('Speech Rate'));
    
    if (speechMetric && speechMetric.score < speechMetric.maxScore * 0.7) {
      tips.push('Work on maintaining optimal speech pace (110-140 words per minute)');
    }

    // Check grammar
    const grammarMetric = scores
      .flatMap(cat => cat.metrics)
      .find(metric => metric.name.includes('Grammar'));
    
    if (grammarMetric && grammarMetric.score < grammarMetric.maxScore * 0.7) {
      tips.push('Review grammar rules and practice sentence construction');
    }

    // Check vocabulary
    const vocabMetric = scores
      .flatMap(cat => cat.metrics)
      .find(metric => metric.name.includes('Vocabulary'));
    
    if (vocabMetric && vocabMetric.score < vocabMetric.maxScore * 0.7) {
      tips.push('Use more varied vocabulary and avoid repetition');
    }

    // Check filler words
    const fillerMetric = scores
      .flatMap(cat => cat.metrics)
      .find(metric => metric.name.includes('Filler'));
    
    if (fillerMetric && fillerMetric.score < fillerMetric.maxScore * 0.7) {
      tips.push('Reduce filler words like "um", "uh", "like" for better clarity');
    }

    // Check sentiment
    const sentimentMetric = scores
      .flatMap(cat => cat.metrics)
      .find(metric => metric.name.includes('Sentiment'));
    
    if (sentimentMetric && sentimentMetric.score < sentimentMetric.maxScore * 0.7) {
      tips.push('Use more positive language and engaging tone');
    }

    // Check flow
    const flowMetric = scores
      .flatMap(cat => cat.metrics)
      .find(metric => metric.name.includes('Flow'));
    
    if (flowMetric && flowMetric.score < flowMetric.maxScore * 0.7) {
      tips.push('Improve introduction structure: Salutation → Name → Details → Closing');
    }

    // Default tips if none specific found
    if (tips.length === 0) {
      tips.push(
        'Practice speaking with varied pacing',
        'Record yourself and listen for improvement areas',
        'Expand your vocabulary with reading',
        'Focus on clear pronunciation'
      );
    }

    return tips.slice(0, 4); // Return max 4 tips
  };

  const handleDownloadReport = () => {
    // Create a simple text report
    const report = `
Communication Skills Assessment Report
======================================

Overall Score: ${overallScore}/${totalMaxScore}
Word Count: ${wordCount}
Duration: ${totalDuration} seconds
Speech Rate: ${speechRate} words per minute

Assessment Remarks:
${getRemark(overallScore)}

Detailed Breakdown:
${criteriaScores.map(category => `
${category.category}:
${category.metrics.map(metric => `  ${metric.name}: ${metric.score}/${metric.maxScore} - ${metric.feedback}`).join('\n')}
`).join('\n')}

Areas for Improvement:
${getImprovementTips(criteriaScores).map(tip => `• ${tip}`).join('\n')}

Generated on: ${new Date().toLocaleDateString()}
    `.trim();

    // Create and download file
    const blob = new Blob([report], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `communication-assessment-${new Date().getTime()}.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const handleTryAgain = () => {
    // Call parent callback if provided
    if (onTryAgain) {
      onTryAgain();
    }
    // Navigate back to intro page
    navigate('/');
  };

  // Show loading state if no results
  if (!results) {
    return (
      <div className="grading-results">
        <div className="loading-state">
          <div className="loading-spinner-large"></div>
          <h2>Loading Results...</h2>
          <p>Please wait while we process your assessment</p>
        </div>
      </div>
    );
  }

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
            <span className="detail-value">~{Math.round(speechRate)} wpm</span>
          </div>
        </div>
      </div>

      {/* Criteria Breakdown */}
      <div className="criteria-breakdown">
        <h2>Detailed Assessment</h2>
        
        {criteriaScores.length > 0 ? (
          criteriaScores.map((category, categoryIndex) => (
            <div key={categoryIndex} className="category-section">
              <h3 className="category-title">{category.category}</h3>
              
              {category.metrics.map((metric, metricIndex) => {
                const percentage = metric.maxScore > 0 ? (metric.score / metric.maxScore) * 100 : 0;
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
          ))
        ) : (
          <div className="no-results">
            <p>No assessment data available. Please try submitting again.</p>
          </div>
        )}
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
              {getImprovementTips(criteriaScores).map((tip, index) => (
                <li key={index}>{tip}</li>
              ))}
            </ul>
          </div>
        </div>
      </div>

      <div className="action-buttons">
        <button className="btn-primary" onClick={handleDownloadReport}>
          Download Report
        </button>
        <button className="btn-secondary" onClick={handleTryAgain}>
          Try Another Introduction
        </button>
      </div>
    </div>
  );
};

export default GradingResults;