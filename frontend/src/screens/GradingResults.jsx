import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import './GradingResults.css';

const GradingResults = ({ results, onTryAgain }) => {
  const location = useLocation();
  const resultsFromState = location.state?.results || results;
  const navigate = useNavigate();
  const [expandedMetrics, setExpandedMetrics] = useState({});

  const {
    overallScore = 0,
    totalDuration = 0,
    wordCount = 0,
    speechRate = 0,
    criteriaScores = []
  } = resultsFromState || {};

  const totalMaxScore = criteriaScores.reduce((total, category) => {
    return total + category.metrics.reduce((catTotal, metric) => catTotal + metric.maxScore, 0);
  }, 0) || 100;

  const getRemark = (score) => {
    const percentage = (score / totalMaxScore) * 100;
    if (percentage >= 90) return 'Excellent! Outstanding communication skills';
    if (percentage >= 80) return 'Very Good! Strong communication abilities';
    if (percentage >= 70) return 'Good! Solid performance with some areas for improvement';
    if (percentage >= 60) return 'Satisfactory. Keep working on your skills';
    return 'Needs improvement. Focus on key areas highlighted';
  };

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

    scores.forEach(category => {
      category.metrics.forEach(metric => {
        const percentage = metric.maxScore > 0 ? (metric.score / metric.maxScore) * 100 : 0;
        if (percentage < 70 && metric.details && metric.details.suggestion) {
          tips.push(metric.details.suggestion);
        }
      });
    });

    if (tips.length === 0) {
      tips.push(
        'Practice speaking with varied pacing',
        'Record yourself and listen for improvement areas',
        'Expand your vocabulary with reading',
        'Focus on clear pronunciation'
      );
    }

    return tips.slice(0, 5);
  };

  const toggleMetricDetails = (categoryIndex, metricIndex) => {
    const key = `${categoryIndex}-${metricIndex}`;
    setExpandedMetrics(prev => ({
      ...prev,
      [key]: !prev[key]
    }));
  };

  const renderDetailedFeedback = (details, metricName) => {
    if (!details) return null;

    return (
      <div className="detailed-feedback">
        {/* Salutation Details */}
        {metricName.includes('Salutation') && details.found && (
          <div className="feedback-section">
            <p><strong>Found:</strong> "{details.found}"</p>
            <p><strong>Level:</strong> {details.level}</p>
            <p className="suggestion">{details.suggestion}</p>
          </div>
        )}

        {/* Keyword Details */}
        {metricName.includes('Keyword') && details.matched_categories && (
          <div className="feedback-section">
            <p><strong>Coverage:</strong> {details.coverage}</p>
            
            {details.matched_categories.length > 0 && (
              <div className="matched-keywords">
                <h5>Found Information:</h5>
                <ul>
                  {details.matched_categories.map((match, idx) => (
                    <li key={idx}>
                      ✓ <strong>{match.category.replace('_', ' ')}</strong> 
                      <span className="similarity-badge">
                        Similarity: {(match.similarity * 100).toFixed(0)}%
                      </span>
                      <span className="points-badge">+{match.points} pts</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}
            
            {details.missing_categories && details.missing_categories.length > 0 && (
              <div className="missing-keywords">
                <h5>Missing Information:</h5>
                <ul>
                  {details.missing_categories.map((missing, idx) => (
                    <li key={idx}>
                      ✗ <strong>{missing.category.replace('_', ' ')}</strong>
                      <span className="suggestion-text">{missing.suggestion}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        )}

        {/* Flow Details */}
        {metricName.includes('Flow') && details.found_sections && (
          <div className="feedback-section">
            <p><strong>Status:</strong> {details.is_correct ? '✓ Correct flow' : '✗ Flow issues detected'}</p>
            {details.found_sections.length > 0 && (
              <p><strong>Found sections:</strong> {details.found_sections.join(', ')}</p>
            )}
            {details.missing_sections && details.missing_sections.length > 0 && (
              <p><strong>Missing sections:</strong> {details.missing_sections.join(', ')}</p>
            )}
            {details.issue && <p className="suggestion">{details.issue}</p>}
          </div>
        )}

        {/* Speech Rate Details */}
        {metricName.includes('Speech Rate') && details.rate && (
          <div className="feedback-section">
            <p><strong>Your rate:</strong> {details.rate} words/minute</p>
            <p><strong>Optimal range:</strong> {details.optimal_range}</p>
            <p><strong>Rating:</strong> {details.rating}</p>
            <p className="suggestion">{details.suggestion}</p>
          </div>
        )}

        {/* Grammar Details */}
        {metricName.includes('Grammar') && details.error_count !== undefined && (
          <div className="feedback-section">
            <p><strong>Errors found:</strong> {details.error_count}</p>
            <p><strong>Error rate:</strong> {details.error_rate}%</p>
            <p><strong>Rating:</strong> {details.rating}</p>
            
            {details.sample_errors && details.sample_errors.length > 0 && (
              <div className="grammar-errors">
                <h5>Sample Issues:</h5>
                <ul>
                  {details.sample_errors.map((error, idx) => (
                    <li key={idx}>
                      <strong>{error.message}</strong>
                      {error.suggestions && error.suggestions.length > 0 && (
                        <span className="error-suggestions">
                          {' '}→ Try: {error.suggestions.join(', ')}
                        </span>
                      )}
                    </li>
                  ))}
                </ul>
              </div>
            )}
            <p className="suggestion">{details.suggestion}</p>
          </div>
        )}

        {/* Vocabulary Richness Details */}
        {metricName.includes('Vocabulary') && details.mtld_score !== undefined && (
          <div className="feedback-section">
            <p><strong>MTLD Score:</strong> {details.mtld_score}</p>
            <p><strong>Rating:</strong> {details.rating}</p>
            <p className="suggestion">{details.suggestion}</p>
          </div>
        )}

        {/* Filler Words Details */}
        {metricName.includes('Filler') && details.filler_count !== undefined && (
          <div className="feedback-section">
            <p><strong>Filler words found:</strong> {details.filler_count}</p>
            <p><strong>Filler rate:</strong> {details.filler_rate}%</p>
            <p><strong>Rating:</strong> {details.rating}</p>
            
            {details.found_fillers && details.found_fillers.length > 0 && (
              <div className="found-fillers">
                <p><strong>Detected fillers:</strong> {details.found_fillers.join(', ')}</p>
              </div>
            )}
            <p className="suggestion">{details.suggestion}</p>
          </div>
        )}

        {/* Sentiment Details */}
        {metricName.includes('Sentiment') && details.positivity_score !== undefined && (
          <div className="feedback-section">
            <p><strong>Positivity score:</strong> {(details.positivity_score * 100).toFixed(1)}%</p>
            <p><strong>Rating:</strong> {details.rating}</p>
            
            {details.positive_words && details.positive_words.length > 0 && (
              <div className="positive-words">
                <p><strong>Positive words found:</strong> {details.positive_words.join(', ')}</p>
              </div>
            )}
            <p className="suggestion">{details.suggestion}</p>
          </div>
        )}
      </div>
    );
  };

  const handleDownloadReport = () => {
    const report = `
Communication Skills Assessment Report
======================================

Overall Score: ${overallScore}/${totalMaxScore} (${((overallScore/totalMaxScore)*100).toFixed(1)}%)
Word Count: ${wordCount}
Duration: ${totalDuration} seconds
Speech Rate: ${speechRate} words per minute

Assessment Remarks:
${getRemark(overallScore)}

Detailed Breakdown:
${criteriaScores.map(category => `
${category.category}:
${category.metrics.map(metric => {
  let metricReport = `  ${metric.name}: ${metric.score}/${metric.maxScore} - ${metric.feedback}`;
  
  if (metric.details) {
    const details = metric.details;
    
    if (details.suggestion) {
      metricReport += `\n    Suggestion: ${details.suggestion}`;
    }
    
    if (details.matched_categories) {
      metricReport += `\n    Matched: ${details.matched_categories.map(m => m.category).join(', ')}`;
    }
    
    if (details.found_fillers && details.found_fillers.length > 0) {
      metricReport += `\n    Filler words: ${details.found_fillers.join(', ')}`;
    }
  }
  
  return metricReport;
}).join('\n')}
`).join('\n')}

Areas for Improvement:
${getImprovementTips(criteriaScores).map(tip => `• ${tip}`).join('\n')}

Generated on: ${new Date().toLocaleDateString()}
    `.trim();

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
    if (onTryAgain) {
      onTryAgain();
    }
    navigate('/');
  };

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
          <div className="score-percentage">{((overallScore/totalMaxScore)*100).toFixed(1)}%</div>
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
                const isExpanded = expandedMetrics[`${categoryIndex}-${metricIndex}`];
                
                return (
                  <div key={metricIndex} className="metric-card">
                    <div 
                      className="metric-header clickable"
                      onClick={() => toggleMetricDetails(categoryIndex, metricIndex)}
                    >
                      <div className="metric-name">
                        <span>{metric.name}</span>
                        <span className="metric-weight">Weight: {metric.maxScore}%</span>
                      </div>
                      <div className="metric-score-wrapper">
                        <div className="metric-score">
                          {metric.score}/{metric.maxScore}
                        </div>
                        <span className="expand-icon">{isExpanded ? '▼' : '▶'}</span>
                      </div>
                    </div>
                    
                    <div className="progress-bar">
                      <div 
                        className={`progress-fill ${percentage >= 80 ? 'excellent' : percentage >= 60 ? 'good' : 'needs-improvement'}`}
                        style={{ width: `${percentage}%` }}
                      ></div>
                    </div>
                    
                    <div className="metric-feedback">
                      {metric.feedback}
                    </div>

                    {isExpanded && metric.details && (
                      <div className="metric-details-expanded">
                        {renderDetailedFeedback(metric.details, metric.name)}
                      </div>
                    )}
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
            <h4>Key Areas for Improvement:</h4>
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
          Download Detailed Report
        </button>
        <button className="btn-secondary" onClick={handleTryAgain}>
          Try Another Introduction
        </button>
      </div>
    </div>
  );
};

export default GradingResults;