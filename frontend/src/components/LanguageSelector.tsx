import { Globe } from 'lucide-react';
import { useFarmerLanguage } from '../i18n/FarmerLanguageContext';
import type { FarmerLanguageCode } from '../i18n/languages';

interface LanguageSelectorProps {
  /** Light text on hero overlay */
  overHero?: boolean;
}

export function LanguageSelector({ overHero }: LanguageSelectorProps) {
  const { language, setLanguage, languages } = useFarmerLanguage();
  const current = languages.find((l) => l.code === language) ?? languages[0];

  return (
    <div className="flex items-center gap-1.5">
      <label
        htmlFor="farmer-language-select"
        className={`sr-only`}
      >
        Language
      </label>
      <Globe
        className={`w-4 h-4 flex-shrink-0 ${overHero ? 'text-white/90' : 'text-[#5A6150]'}`}
        aria-hidden
      />
      <select
        id="farmer-language-select"
        value={language}
        onChange={(e) => setLanguage(e.target.value as FarmerLanguageCode)}
        aria-label="Select language"
        className={[
          'max-w-[9.5rem] sm:max-w-[11rem] rounded-full border px-3 py-1.5 text-[12px] sm:text-[13px] font-medium',
          'cursor-pointer outline-none focus-visible:ring-2 focus-visible:ring-[#6E7A4E]/50',
          overHero
            ? 'bg-white/10 border-white/30 text-white'
            : 'bg-white border-[#DDD6C4] text-[#1C2A1A]',
        ].join(' ')}
      >
        {languages.map((opt) => (
          <option key={opt.code} value={opt.code}>
            {opt.nativeLabel}
          </option>
        ))}
      </select>
      <span className="sr-only">{current.nativeLabel}</span>
    </div>
  );
}
