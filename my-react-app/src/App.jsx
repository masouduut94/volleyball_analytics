import { useState } from 'react'
import reactLogo from './assets/react.svg'
import viteLogo from '/vite.svg'
import './App.css'
import FileForm from './FileForm'

function App() {
  const [count, setCount] = useState(0)

  return (
    <>

      <div className="App">
        <FileForm />
      </div>

    </>
  )
}

export default App
