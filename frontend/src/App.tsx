import { Navigate, Route, Routes } from 'react-router-dom'
import { Navbar } from './components/Navbar'
import { Sidebar } from './components/Sidebar'
import { BookingDetails } from './pages/BookingDetails'
import { Bookings } from './pages/Bookings'
import { CreateHold } from './pages/CreateHold'
import { Dashboard } from './pages/Dashboard'
import { Fares } from './pages/Fares'
import { Payments } from './pages/Payments'
import { SystemEvents } from './pages/SystemEvents'

export default function App() {
  return (
    <div className="min-h-screen bg-slate-50">
      <Navbar />
      <div className="flex min-h-[calc(100vh-73px)]">
        <Sidebar />
        <main className="flex-1 p-6">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/fares" element={<Fares />} />
            <Route path="/holds/new" element={<CreateHold />} />
            <Route path="/bookings" element={<Bookings />} />
            <Route path="/bookings/:reference" element={<BookingDetails />} />
            <Route path="/payments" element={<Payments />} />
            <Route path="/events" element={<SystemEvents />} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </main>
      </div>
    </div>
  )
}
