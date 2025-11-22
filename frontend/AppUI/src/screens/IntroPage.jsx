import React, { useState } from 'react';
import './IntroductionForm.css';

const IntroductionForm = () => {
  const [formData, setFormData] = useState({
    rollNumber: '',
    email: '',
    introduction: ''
  });

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prevState => ({
      ...prevState,
      [name]: value
    }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    // Here you would typically send the data to your backend
    console.log('Form submitted:', formData);
    alert('Introduction submitted successfully!');
  };

  return (
    <div className="form-container">
      <div className="form-header">
        <h1>Student Self-Introduction</h1>
        <p>Please fill in your details and write a brief introduction about yourself</p>
      </div>

      <form onSubmit={handleSubmit} className="introduction-form">
        <div className="form-group">
          <label htmlFor="rollNumber">Student Roll Number</label>
          <input
            type="text"
            id="rollNumber"
            name="rollNumber"
            value={formData.rollNumber}
            onChange={handleChange}
            required
            placeholder="Enter your roll number"
          />
        </div>

        <div className="form-group">
          <label htmlFor="email">School Email ID</label>
          <input
            type="email"
            id="email"
            name="email"
            value={formData.email}
            onChange={handleChange}
            required
            placeholder="Enter your school email"
          />
        </div>

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
          />
          <div className="word-count">
            Words: {formData.introduction.trim() ? formData.introduction.trim().split(/\s+/).length : 0}
          </div>
        </div>

        <button type="submit" className="submit-btn">
          Grade Introduction
        </button>
      </form>
    </div>
  );
};

export default IntroductionForm;