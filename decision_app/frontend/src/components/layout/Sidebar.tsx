import { NavLink } from 'react-router-dom'
import { 
  BarChart3, 
  TrendingUp, 
  History, 
  Database, 
  Settings,
  Activity,
  Sparkles,
  ChevronDown,
  ChevronUp
} from 'lucide-react'
import { cn } from '@/lib/utils'
import { useAssistantMode } from '@/contexts/AssistantModeContext'
import { useState } from 'react'

const essentialNavigation = [
  { name: 'Inicio', href: '/', icon: BarChart3, isEssential: true },
  { name: 'Recomendaciones', href: '/recommendations', icon: TrendingUp, isEssential: true },
]

const advancedNavigation = [
  { name: 'Backtests', href: '/backtests', icon: History, isEssential: false },
  { name: 'Datos de Mercado', href: '/market-data', icon: Database, isEssential: false },
  { name: 'Configuración', href: '/settings', icon: Settings, isEssential: false },
]

export default function Sidebar() {
  const { isAssistantMode, toggleAssistantMode } = useAssistantMode();
  const [showAdvanced, setShowAdvanced] = useState(false);

  return (
    <div className="w-64 bg-card border-r border-border">
      <div className="flex items-center h-16 px-6 border-b border-border">
        <Activity className="h-8 w-8 text-primary" />
        <span className="ml-2 text-xl font-bold">One Trade</span>
      </div>
      
      <div className="px-3 py-4 border-b border-border">
        <button onClick={toggleAssistantMode} className={cn("w-full flex items-center justify-between px-3 py-2 text-sm font-medium rounded-md transition-colors", isAssistantMode ? 'bg-blue-100 text-blue-700 hover:bg-blue-200' : 'bg-gray-100 text-gray-700 hover:bg-gray-200')}>
          <div className="flex items-center">
            <Sparkles className="mr-2 h-4 w-4" />
            <span>Modo Asistente</span>
          </div>
          <div className={cn("w-10 h-5 rounded-full transition-colors relative", isAssistantMode ? 'bg-blue-600' : 'bg-gray-300')}>
            <div className={cn("absolute top-0.5 w-4 h-4 rounded-full bg-white transition-transform", isAssistantMode ? 'translate-x-5' : 'translate-x-0.5')} />
          </div>
        </button>
        {isAssistantMode && (
          <p className="text-xs text-gray-500 mt-2 px-3">Solo mostrando lo esencial para que sea más fácil</p>
        )}
      </div>

      <nav className="mt-6 px-3">
        <ul className="space-y-1">
          {essentialNavigation.map((item) => (
            <li key={item.name}>
              <NavLink to={item.href} className={({ isActive }) => cn('flex items-center px-3 py-2 text-sm font-medium rounded-md transition-colors', isActive ? 'bg-primary text-primary-foreground' : 'text-muted-foreground hover:text-foreground hover:bg-accent')}>
                <item.icon className="mr-3 h-5 w-5" />
                {item.name}
              </NavLink>
            </li>
          ))}
        </ul>

        {!isAssistantMode && (
          <>
            <div className="mt-6 mb-2">
              <button onClick={() => setShowAdvanced(!showAdvanced)} className="w-full flex items-center justify-between px-3 py-1 text-xs font-semibold text-gray-500 uppercase tracking-wider hover:text-gray-700">
                <span>Opciones Avanzadas</span>
                {showAdvanced ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
              </button>
            </div>
            {showAdvanced && (
              <ul className="space-y-1">
                {advancedNavigation.map((item) => (
                  <li key={item.name}>
                    <NavLink to={item.href} className={({ isActive }) => cn('flex items-center px-3 py-2 text-sm font-medium rounded-md transition-colors', isActive ? 'bg-primary text-primary-foreground' : 'text-muted-foreground hover:text-foreground hover:bg-accent')}>
                      <item.icon className="mr-3 h-5 w-5" />
                      {item.name}
                    </NavLink>
                  </li>
                ))}
              </ul>
            )}
          </>
        )}
      </nav>
    </div>
  )
}

