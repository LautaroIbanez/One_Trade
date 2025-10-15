import { Bell, User } from 'lucide-react'
import { Button } from '@/components/ui/button'

export default function Header() {
  return (
    <header className="h-16 border-b border-border bg-background">
      <div className="flex items-center justify-between h-full px-6">
        <div>
          <h1 className="text-2xl font-semibold text-foreground">
            One Trade Decision App
          </h1>
        </div>
        <div className="flex items-center space-x-4">
          <Button variant="ghost" size="icon">
            <Bell className="h-5 w-5" />
          </Button>
          <Button variant="ghost" size="icon">
            <User className="h-5 w-5" />
          </Button>
        </div>
      </div>
    </header>
  )
}

