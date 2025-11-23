import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { useState } from 'react';
import IntroPage from "./screens/IntroPage";
import GradingResults from './screens/GradingResults';

function App() {
  const [gradingResults, setGradingResults] = useState(null);

  const handleGradingComplete = (results) => {
    setGradingResults(results);
  };

  const handleTryAgain = () => {
    setGradingResults(null);
  };

  return (
    <Router>
      <Routes>
        <Route 
          path="/" 
          element={
            <IntroPage onGradingComplete={handleGradingComplete} />
          } 
        />
        <Route 
          path="/results" 
          element={
            <GradingResults 
              results={gradingResults} 
              onTryAgain={handleTryAgain} 
            />
          } 
        />
      </Routes>
    </Router>
  );
}

export default App;