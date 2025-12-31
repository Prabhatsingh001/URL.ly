import { Routes, Route } from 'react-router-dom'
import Home from './components/Home.jsx'
import Profile from './components/Profile.jsx'

function App() {

  return (
    <>
        <Routes>
            <Route path='/' element={<Home />} />
            <Route path='/profile' element={<Profile />} />
        </Routes>
    </>
  )
}

export default App
