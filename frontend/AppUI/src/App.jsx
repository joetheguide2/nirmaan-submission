import { useState } from 'react'
import reactLogo from './assets/react.svg'
import viteLogo from '/vite.svg'
import './App.css'
import IntroPage from "./screens/IntroPage"
import GradingResults from './screens/GradingResults'

function App() {
  const [count, setCount] = useState(0)

  return (
    <>
      <IntroPage></IntroPage>
      <GradingResults></GradingResults>
    </>
  )
}

export default App
