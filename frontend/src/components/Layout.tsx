import React from 'react';
import { Button } from './ui/button';
import { Inbox, BarChart3 } from 'lucide-react';

interface LayoutProps {
  children: React.ReactNode;
  currentPage: string;
  onNavigate: (page: string) => void;
}

export function Layout({ children, currentPage, onNavigate }: LayoutProps) {
  return (
    <div className="flex flex-col h-screen w-full bg-background">
      <header className="border-b border-border bg-card p-4">
        <div className="flex items-center justify-between">
          <h1 className="gradient-text text-xl font-bold">RevEase</h1>

          <nav className="flex items-center gap-2">
            <Button
              variant={currentPage === 'inbox' ? 'default' : 'ghost'}
              size="sm"
              onClick={() => onNavigate('inbox')}
              className={currentPage === 'inbox' ? 'bg-primary text-primary-foreground' : 'hover:bg-muted'}
            >
              <Inbox className="mr-2 h-4 w-4" />
              Inbox
            </Button>
            <Button
              variant={currentPage === 'analytics' ? 'default' : 'ghost'}
              size="sm"
              onClick={() => onNavigate('analytics')}
              className={currentPage === 'analytics' ? 'bg-primary text-primary-foreground' : 'hover:bg-muted'}
            >
              <BarChart3 className="mr-2 h-4 w-4" />
              Analytics
            </Button>
          </nav>
        </div>
      </header>

      <main className="flex-1 overflow-auto bg-grid-pattern">
        {children}
      </main>
    </div>
  );
}