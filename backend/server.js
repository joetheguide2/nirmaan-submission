const express = require('express');
const { spawn } = require('child_process');
const path = require('path');
const cors = require('cors');

const app = express();
const PORT = process.env.PORT || 5000;

// Middleware
app.use(cors());
app.use(express.json());

// Serve static files from React build (if exists)
app.use(express.static(path.join(__dirname, 'build')));

// Store submissions (in production, use database)
let submissions = [];

// Health check endpoint
app.get('/api/health', (req, res) => {
  res.json({ 
    status: 'Server is running',
    timestamp: new Date().toISOString(),
    submissionsCount: submissions.length
  });
});

// Analyze introduction endpoint
app.post('/api/analyze-introduction', (req, res) => {
  try {
    const { introduction, duration } = req.body;

    // Validate input
    if (!introduction || !duration) {
      return res.status(400).json({
        success: false,
        message: 'Introduction text and duration are required'
      });
    }

    // Create submission record
    const submission = {
      id: Date.now().toString(),
      introduction: introduction,
      duration: parseFloat(duration),
      timestamp: new Date().toISOString(),
      status: 'processing'
    };

    submissions.push(submission);

    // Call Python script with proper Java configuration
    const pythonProcess = spawn('python3', [
    './python/main.py', 
    JSON.stringify({
        introduction: introduction,
        duration: parseFloat(duration)
        })
    ], {
        env: process.env // Just pass the existing environment
    });

    let result = '';
    let errorOutput = '';

    pythonProcess.stdout.on('data', (data) => {
      result += data.toString();
    });

    pythonProcess.stderr.on('data', (data) => {
      errorOutput += data.toString();
      console.error('Python stderr:', data.toString());
    });

    pythonProcess.on('close', (code) => {
      if (code === 0) {
        try {
          const gradingResult = JSON.parse(result);
          
          // Update submission with results
          const submissionIndex = submissions.findIndex(s => s.id === submission.id);
          if (submissionIndex !== -1) {
            submissions[submissionIndex] = {
              ...submissions[submissionIndex],
              status: 'completed',
              gradingResult: gradingResult
            };
          }

          res.json({
            success: true,
            message: 'Analysis completed successfully',
            data: gradingResult
          });

        } catch (parseError) {
          console.error('JSON Parse Error:', parseError);
          console.error('Raw output:', result);
          res.status(500).json({
            success: false,
            message: 'Error parsing analysis results',
            error: errorOutput || parseError.message,
            rawOutput: result
          });
        }
      } else {
        console.error('Python process exited with code:', code);
        res.status(500).json({
          success: false,
          message: 'Analysis failed',
          error: errorOutput,
          exitCode: code
        });
      }
    });

    pythonProcess.on('error', (error) => {
      console.error('Failed to start Python process:', error);
      res.status(500).json({
        success: false,
        message: 'Failed to start analysis process',
        error: error.message
      });
    });

  } catch (error) {
    console.error('Server Error:', error);
    res.status(500).json({
      success: false,
      message: 'Internal server error',
      error: error.message
    });
  }
});

// Get submission results
app.get('/api/results/:submissionId', (req, res) => {
  try {
    const { submissionId } = req.params;
    const submission = submissions.find(s => s.id === submissionId);
    
    if (!submission) {
      return res.status(404).json({
        success: false,
        message: 'Submission not found'
      });
    }

    res.json({
      success: true,
      data: submission
    });

  } catch (error) {
    res.status(500).json({
      success: false,
      message: 'Error fetching results'
    });
  }
});

// Get all submissions (for debugging)
app.get('/api/submissions', (req, res) => {
  res.json({
    success: true,
    data: submissions
  });
});

// Delete all submissions (for cleanup)
app.delete('/api/submissions', (req, res) => {
  submissions = [];
  res.json({
    success: true,
    message: 'All submissions cleared'
  });
});

// FIXED: 404 handler for API routes only (must come BEFORE catch-all)
app.use('/api/*', (req, res) => {
  res.status(404).json({
    success: false,
    message: 'API endpoint not found',
    requestedPath: req.path,
    method: req.method
  });
});

// Catch-all handler for React routing (must be LAST)
app.get('*', (req, res) => {
  const buildPath = path.join(__dirname, 'build', 'index.html');
  if (require('fs').existsSync(buildPath)) {
    res.sendFile(buildPath);
  } else {
    res.json({
      message: 'Server is running. Frontend build not found.',
      endpoints: {
        health: '/api/health',
        analyze: '/api/analyze-introduction',
        results: '/api/results/:id',
        submissions: '/api/submissions'
      }
    });
  }
});

// Error handling middleware
app.use((error, req, res, next) => {
  console.error('Unhandled error:', error);
  res.status(500).json({
    success: false,
    message: 'Something went wrong!',
    error: error.message
  });
});

// Start server
app.listen(PORT, () => {
  console.log(`🚀 Server is running on port ${PORT}`);
  console.log(`📊 Health check: http://localhost:${PORT}/api/health`);
  console.log(`📝 Submit form: POST http://localhost:${PORT}/api/analyze-introduction`);
  console.log(`📋 Get results: GET http://localhost:${PORT}/api/results/:id`);
});

module.exports = app;