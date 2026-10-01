import React, { useEffect, useState } from 'react';
import { Leaf, Menu, X } from 'lucide-react';

export type AppPage = 'home' | 'detect' | 'result' | 'history' | 'dashboard';

interface NavbarProps {
  activePage: AppPage;
  onNavigate: (page: AppPage) => void;
  overlay: boolean;
}

export const Navbar: React.FC<NavbarProps> = ({ activePage, onNavigate, overlay }) => {
  const [scrolled, setScrolled] = useState(false);
  const [mobileOpen, setMobileOpen] = useState(false);

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 24);
    window.addEventListener('scroll', onScroll);
    return () => window.removeEventListener('scroll', onScroll);
  }, []);

  const overHero = overlay && !scrolled;
  const navItems: { id: AppPage; label: string }[] = [
    { id: 'home', label: 'Home' },
    { id: 'detect', label: 'Detect' },
    { id: 'history', label: 'History' },
    { id: 'dashboard', label: 'Dashboard' },
  ];

  return (
    <header className={`fixed top-0 left-0 right-0 z-50 transition-all duration-500 ${
      overHero ? 'bg-transparent' : 'bg-[#FBF7EE]/95 border-b border-[#DDD6C4] shadow-[0_8px_30px_rgba(18,25,16,0.06)] backdrop-blur-md'
    }`}>
      <div className="max-w-[1400px] mx-auto px-5 sm:px-8 h-[72px] flex items-center justify-between">
        <button
          onClick={() => onNavigate('home')}
          className="flex items-center gap-2.5 group"
        >
          <span className={`w-9 h-9 rounded-full flex items-center justify-center border ${
            overHero ? 'bg-white/10 border-white/30 text-[#E8D5A3]' : 'bg-[#1C2A1A] border-[#1C2A1A] text-[#E8D5A3]'
          }`}>
            <Leaf className="w-5 h-5" />
          </span>
          <span className={`font-display text-[22px] tracking-tight ${overHero ? 'text-white' : 'text-[#1C2A1A]'}`}>
            CropSense
          </span>
        </button>

        <nav className="hidden lg:flex items-center gap-8">
          {navItems.map((item) => {
            const active = activePage === item.id || (item.id === 'detect' && activePage === 'result');
            return (
              <button
                key={item.id}
                onClick={() => onNavigate(item.id)}
                className={`text-[13px] tracking-[0.14em] uppercase font-medium transition-colors ${
                  overHero
                    ? active ? 'text-[#E8D5A3]' : 'text-white/80 hover:text-white'
                    : active ? 'text-[#4F5A38]' : 'text-[#5A6150] hover:text-[#1C2A1A]'
                }`}
              >
                {item.label}
              </button>
            );
          })}
        </nav>

        <div className="flex items-center gap-3">
          <button
            onClick={() => onNavigate('detect')}
            className={`hidden sm:inline-flex items-center px-5 py-2 rounded-full text-[13px] font-semibold tracking-wide transition-all ${
              overHero
                ? 'bg-[#E8D5A3] text-[#1C2A1A] hover:bg-white'
                : 'bg-[#1C2A1A] text-[#F6F1E6] hover:bg-[#4F5A38]'
            }`}
          >
            Detect Disease
          </button>
          <button
            onClick={() => setMobileOpen(!mobileOpen)}
            className={`lg:hidden p-2 rounded-full ${overHero ? 'text-white' : 'text-[#1C2A1A]'}`}
          >
            {mobileOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
          </button>
        </div>
      </div>

      {mobileOpen && (
        <div className="lg:hidden bg-[#FBF7EE] border-t border-[#DDD6C4] px-5 py-4 space-y-1">
          {navItems.map((item) => (
            <button
              key={item.id}
              onClick={() => {
                onNavigate(item.id);
                setMobileOpen(false);
              }}
              className="block w-full text-left px-3 py-2.5 text-sm font-medium text-[#1C2A1A]"
            >
              {item.label}
            </button>
          ))}
        </div>
      )}
    </header>
  );
};
