import { Routes, Route, Navigate } from 'react-router-dom'
import { MainLayout } from './components/Layout'
import { Dashboard } from './pages/Dashboard'
import { Backtest } from './pages/Backtest'
import { Skills } from './pages/Skills'
import { Portfolio } from './pages/Portfolio'

function App() {
  return (
    <MainLayout>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/backtest" element={<Backtest />} />
        <Route path="/skills" element={<Skills />} />
        <Route path="/portfolio" element={<Portfolio />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </MainLayout>
  )
}

export default App