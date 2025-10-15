import { Settings as SettingsIcon } from 'lucide-react'
import StrategyWeights from '@/components/StrategyWeights'
import SymbolManager from '@/components/SymbolManager'

export default function Settings() {
  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-3xl font-bold tracking-tight">Settings</h2>
        <p className="text-muted-foreground">
          Configure your trading strategies and preferences
        </p>
      </div>

      <div className="grid gap-6">
        {/* Strategy Weights Configuration */}
        <div className="rounded-lg border bg-card p-6">
          <div className="flex items-center space-x-2 mb-4">
            <SettingsIcon className="h-5 w-5" />
            <h3 className="text-lg font-semibold">Strategy Configuration</h3>
          </div>
          <StrategyWeights />
        </div>

        {/* Symbol Management */}
        <div className="rounded-lg border bg-card p-6">
          <div className="flex items-center space-x-2 mb-4">
            <SettingsIcon className="h-5 w-5" />
            <h3 className="text-lg font-semibold">Symbol Management</h3>
          </div>
          <SymbolManager />
        </div>

        {/* Additional Settings */}
        <div className="rounded-lg border bg-card p-6">
          <div className="flex items-center space-x-2 mb-4">
            <SettingsIcon className="h-5 w-5" />
            <h3 className="text-lg font-semibold">Additional Settings</h3>
          </div>
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <h4 className="text-sm font-medium">Auto-refresh recommendations</h4>
                <p className="text-xs text-gray-500">Automatically refresh recommendations every 5 minutes</p>
              </div>
              <input type="checkbox" className="h-4 w-4" defaultChecked />
            </div>
            
            <div className="flex items-center justify-between">
              <div>
                <h4 className="text-sm font-medium">Email notifications</h4>
                <p className="text-xs text-gray-500">Receive email alerts for strong buy/sell signals</p>
              </div>
              <input type="checkbox" className="h-4 w-4" />
            </div>
            
            <div className="flex items-center justify-between">
              <div>
                <h4 className="text-sm font-medium">Risk level alerts</h4>
                <p className="text-xs text-gray-500">Show alerts when risk level is HIGH</p>
              </div>
              <input type="checkbox" className="h-4 w-4" defaultChecked />
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}