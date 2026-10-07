import { Moon, Sun } from 'lucide-react';
import { useTheme } from '../theme/ThemeContext';

interface ThemeToggleProps {
  overHero?: boolean;
}

export function ThemeToggle({ overHero }: ThemeToggleProps) {
  const { theme, toggleTheme } = useTheme();
  const isDark = theme === 'dark';

  return (
    <button
      type="button"
      onClick={toggleTheme}
      className={[
        'p-2 rounded-full transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-[#6E7A4E]/50',
        overHero
          ? 'text-white/90 hover:bg-white/10'
          : 'text-ink-muted hover:bg-surface-elevated border border-transparent hover:border-border',
      ].join(' ')}
      aria-label={isDark ? 'Switch to light theme' : 'Switch to dark theme'}
      title={isDark ? 'Light mode' : 'Dark mode'}
    >
      {isDark ? <Sun className="w-4 h-4" aria-hidden /> : <Moon className="w-4 h-4" aria-hidden />}
    </button>
  );
}
