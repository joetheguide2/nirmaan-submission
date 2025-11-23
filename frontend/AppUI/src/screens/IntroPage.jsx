import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom'; // Import useNavigate
import './IntroductionForm.css';

const IntroductionForm = ({ onGradingComplete }) => {
  const [formData, setFormData] = useState({
    introduction: '',
    duration: ''
  });
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const navigate = useNavigate(); // Add this hook

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prevState => ({
      ...prevState,
      [name]: value
    }));
    // Clear error when user starts typing
    if (error) setError('');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    // Validation
    if (!formData.introduction.trim()) {
      setError('Please write your introduction');
      return;
    }
    
    if (!formData.duration || isNaN(formData.duration) || parseFloat(formData.duration) <= 0) {
      setError('Please enter a valid duration in seconds');
      return;
    }

    setIsLoading(true);
    setError('');

    try {
      const response = await fetch('/api/analyze-introduction', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          introduction: formData.introduction,
          duration: parseFloat(formData.duration)
        }),
      });

      const result = await response.json();

      if (result.success) {
        console.log('Grading completed:', result.data);
        
        // Pass results to parent component
        if (onGradingComplete) {
          onGradingComplete(result.data);
        }
        
        // Navigate to results page
        navigate('/results');
      } else {
        setError(result.message || 'Grading failed. Please try again.');
      }
    } catch (error) {
      console.error('Submission error:', error);
      setError('Network error. Please check your connection and try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const wordCount = formData.introduction.trim() ? formData.introduction.trim().split(/\s+/).length : 0;

  return (
    <div className="form-container">
      <div className="form-header">
        <h1>Student Self-Introduction</h1>
        <p>Please write your introduction and provide the duration for grading</p>
      </div>

      {error && (
        <div className="error-message">
          {error}
        </div>
      )}

      <form onSubmit={handleSubmit} className="introduction-form">
        <div className="form-group">
          <label htmlFor="introduction">Self Introduction</label>
          <textarea
            id="introduction"
            name="introduction"
            value={formData.introduction}
            onChange={handleChange}
            required
            placeholder="Write a brief introduction about yourself (your background, interests, goals, etc.)"
            rows="6"
            disabled={isLoading}
          />
          <div className="word-count">
            Words: {wordCount}
          </div>
        </div>

        <div className="form-group">
          <label htmlFor="duration">Duration (Seconds)</label>
          <input
            type="number"
            id="duration"
            name="duration"
            value={formData.duration}
            onChange={handleChange}
            required
            placeholder="Enter the duration of your speech in seconds"
            min="1"
            step="0.1"
            disabled={isLoading}
          />
          <div className="duration-help">
            Enter how long your introduction took to speak (in seconds)
          </div>
        </div>

        <button 
          type="submit" 
          className="submit-btn"
          disabled={isLoading}
        >
          {isLoading ? (
            <>
              <span className="loading-spinner"></span>
              Grading...
            </>
          ) : (
            'Grade Introduction'
          )}
        </button>
      </form>

      {isLoading && (
        <div className="loading-overlay">
          <div className="loading-content">
            <div className="loading-spinner-large"></div>
            <p>Analyzing your introduction...</p>
            <p className="loading-subtext">This may take a few seconds</p>
          </div>
        </div>
      )}
    </div>
  );
};

export default IntroductionForm;