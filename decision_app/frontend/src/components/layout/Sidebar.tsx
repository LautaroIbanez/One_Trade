import { NavLink } from 'react-router-dom'
import { 
  BarChart3, 
  TrendingUp, 
  History, 
  Database, 
  Settings,
  Activity
} from 'lucide-react'
import { cn } from '@/lib/utils'

const navigation = [
  { name: 'Dashboard', href: '/', icon: BarChart3 },
  { name: 'Recommendations', href: '/recommendations', icon: TrendingUp },
  { name: 'Backtests', href: '/backtests', icon: History },
  { name: 'Market Data', href: '/market-data', icon: Database },
  { name: 'Settings', href: '/settings', icon: Settings },
]

export default function Sidebar() {
  return (
    <div className="w-64 bg-card border-r border-border">
      <div className="flex items-center h-16 px-6 border-b border-border">
        <Activity className="h-8 w-8 text-primary" />
        <span className="ml-2 text-xl font-bold">One Trade</span>
      </div>
      <nav className="mt-6 px-3">
        <ul className="space-y-1">
          {navigation.map((item) => (
            <li key={item.name}>
              <NavLink
                to={item.href}
                className={({ isActive }) =>
                  cn(
                    'flex items-center px-3 py-2 text-sm font-medium rounded-md transition-colors',
                    isActive
                      ? 'bg-primary text-primary-foreground'
                      : 'text-muted-foreground hover:text-foreground hover:bg-accent'
                  )
                }
              >
                <item.icon className="mr-3 h-5 w-5" />
                {item.name}
              </NavLink>
            </li>
          ))}
        </ul>
      </nav>
    </div>
  )
}

