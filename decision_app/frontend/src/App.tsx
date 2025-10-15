import { Routes, Route } from 'react-router-dom'
import { Toaster } from '@/components/ui/toaster'
import Layout from '@/components/layout/Layout'
import Dashboard from '@/pages/Dashboard'
import Recommendations from '@/pages/Recommendations'
import Backtests from '@/pages/Backtests'
import MarketData from '@/pages/MarketData'
import Settings from '@/pages/Settings'

function App() {
  return (
    <div className="min-h-screen bg-background">
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<Dashboard />} />
          <Route path="recommendations" element={<Recommendations />} />
          <Route path="backtests" element={<Backtests />} />
          <Route path="market-data" element={<MarketData />} />
          <Route path="settings" element={<Settings />} />
        </Route>
      </Routes>
      <Toaster />
    </div>
  )
}

export default App

