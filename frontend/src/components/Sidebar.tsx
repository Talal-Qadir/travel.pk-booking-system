import { NavLink } from 'react-router-dom'

const links = [
  { to: '/', label: 'Dashboard' },
  { to: '/fares', label: 'Fares' },
  { to: '/holds/new', label: 'Create Hold' },
  { to: '/bookings', label: 'Bookings' },
  { to: '/payments', label: 'Payments' },
  { to: '/events', label: 'System Events' },
]

export function Sidebar() {
  return (
    <aside className="w-56 shrink-0 border-r border-slate-200 bg-white p-4">
      <nav className="space-y-1">
        {links.map((link) => (
          <NavLink
            key={link.to}
            to={link.to}
            end={link.to === '/'}
            className={({ isActive }) =>
              `block rounded-md px-3 py-2 text-sm font-medium ${
                isActive ? 'bg-sky-50 text-sky-800' : 'text-slate-700 hover:bg-slate-50'
              }`
            }
          >
            {link.label}
          </NavLink>
        ))}
      </nav>
    </aside>
  )
}
