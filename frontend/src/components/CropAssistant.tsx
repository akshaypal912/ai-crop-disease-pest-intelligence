/**
 * AI Crop Assistant — premium agricultural SaaS chat component.
 *
 * - Grounded in the CURRENT prediction result (never stale context).
 * - Context is cleared automatically when the session prop changes.
 * - Suggested question chips for quick access.
 * - Displays context_used pills and grounded status.
 * - Degrades gracefully on API error without breaking the results page.
 */

import { useState, useEffect, useRef, useCallback, useMemo } from 'react';
import { Leaf, Send, Sparkles, AlertTriangle, ChevronRight, Loader2, X } from 'lucide-react';
import { marked } from 'marked';
import DOMPurify from 'dompurify';
import type { PredictionResponse } from '../types/predict';
import { askCropAssistant, ApiError } from '../services/api';
import type { CropAssistantResponse } from '../services/api';
import { useFarmerLanguage } from '../i18n/FarmerLanguageContext';
import { CROP_ASSISTANT_UI_STRINGS } from '../utils/collectReportText';
import { translateBatch } from '../services/translationApi';

/**
 * Configure marked with GitHub-flavored markdown and soft breaks preserved.
 */
marked.setOptions({
  gfm: true,
  breaks: true,
});

/**
 * Clean up escaped markdown characters (e.g. \###, \*\*) and sanitize HTML.
 * Strictly prevents raw HTML or script execution while preserving formatting.
 */
function renderSafeMarkdown(content: string): string {
  if (!content) return '';
  // 1. Unescape escaped markdown characters if present in raw LLM output
  const unescaped = content.replace(/\\([\\`*{}[\]()#+\-.!_>~|])/g, '$1');
  // 2. Parse markdown into HTML string
  const rawHtml = marked.parse(unescaped, { async: false }) as string;
  // 3. Sanitize HTML via DOMPurify, only allowing safe formatting tags
  return DOMPurify.sanitize(rawHtml, {
    ALLOWED_TAGS: [
      'p', 'strong', 'em', 'b', 'i', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
      'ul', 'ol', 'li', 'blockquote', 'code', 'pre', 'hr', 'br', 'span'
    ],
    ALLOWED_ATTR: ['class'],
    RETURN_TRUSTED_TYPE: false,
  });
}

interface CropAssistantProps {
  report: PredictionResponse;
  sessionId: string; // changes when image / analysis changes — clears stale context
}

const SUGGESTED_QUESTIONS = [
  'What should I do today?',
  'Why was this result given?',
  'What symptoms should I monitor?',
  'Are the detected pests concerning?',
  'What should I check tomorrow?',
];

const CONTEXT_LABEL_MAP: Record<string, string> = {
  crop: 'Crop ID',
  vision_assessment: 'AI visual assessment',
  specialist_routing: 'Specialist routing',
  disease: 'Disease diagnosis',
  pest_detection: 'Pest detection',
  pest_recommendations: 'Pest recommendations',
  weather: 'Weather',
  risk: 'Risk assessment',
  recommendations: 'Recommendations',
  alert: 'Alert',
};

export function CropAssistant({ report, sessionId }: CropAssistantProps) {
  const { language, localize, ingestTranslations, translationWarning } = useFarmerLanguage();
  const [question, setQuestion] = useState('');
  const [response, setResponse] = useState<CropAssistantResponse | null>(null);
  const [englishAnswer, setEnglishAnswer] = useState<string | null>(null);
  const [displayAnswer, setDisplayAnswer] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const responseRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    void ingestTranslations(CROP_ASSISTANT_UI_STRINGS);
  }, [ingestTranslations]);

  // Clear stale context whenever the analysis changes
  useEffect(() => {
    setResponse(null);
    setEnglishAnswer(null);
    setDisplayAnswer('');
    setError(null);
    setQuestion('');
  }, [sessionId]);

  useEffect(() => {
    if (!englishAnswer) {
      setDisplayAnswer('');
      return;
    }
    if (language === 'en') {
      setDisplayAnswer(englishAnswer);
      return;
    }
    let cancelled = false;
    void translateBatch([englishAnswer], language).then((res) => {
      if (cancelled) return;
      setDisplayAnswer(res.items[0]?.translated_text ?? englishAnswer);
    });
    return () => {
      cancelled = true;
    };
  }, [englishAnswer, language]);

  const renderedAnswer = useMemo(() => {
    if (!displayAnswer) return '';
    return renderSafeMarkdown(displayAnswer);
  }, [displayAnswer]);

  const sendQuestion = useCallback(
    async (q: string) => {
      const trimmed = q.trim();
      if (!trimmed || isLoading) return;

      setIsLoading(true);
      setError(null);
      setResponse(null);

      try {
        const result = await askCropAssistant(trimmed, report, 'en');
        setResponse(result);
        setEnglishAnswer(result.answer);
        // Scroll to response smoothly
        setTimeout(() => {
          responseRef.current?.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        }, 100);
      } catch (err) {
        const msg =
          err instanceof ApiError
            ? err.detail
            : err instanceof Error
              ? err.message
              : 'Unknown error';
        setError(msg);
      } finally {
        setIsLoading(false);
      }
    },
    [isLoading, report]
  );

  const handleSend = () => sendQuestion(question);

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleSuggestion = (q: string) => {
    setQuestion(q);
    sendQuestion(q);
  };

  return (
    <section
      id="crop-assistant"
      aria-label="AI Crop Assistant"
      className="relative rounded-2xl overflow-hidden border border-[#D6CDB7] bg-gradient-to-br from-[#F5EFE0] via-[#FDFAF4] to-[#EEF4E8] shadow-sm"
    >
      {/* Decorative accent line */}
      <div className="absolute top-0 left-0 right-0 h-[3px] bg-gradient-to-r from-[#6E7A4E] via-[#9BAF6A] to-[#C5D48A]" />

      {/* Header */}
      <div className="px-6 sm:px-8 pt-7 pb-5 border-b border-[#DDD6C4]">
        <div className="flex items-start gap-3">
          <div className="flex-shrink-0 w-10 h-10 rounded-xl bg-[#6E7A4E] flex items-center justify-center shadow-sm">
            <Sparkles className="w-5 h-5 text-[#E8D5A3]" />
          </div>
          <div>
            <h2 className="font-display text-xl text-[#1C2A1A] leading-tight">
              {localize('AI Crop Assistant')}
            </h2>
            <p className="text-[11px] tracking-[0.16em] uppercase text-[#6E7A4E] mt-0.5">
              {localize('Ask questions about this crop analysis')}
            </p>
          </div>
        </div>
      </div>

      {/* Suggested chips */}
      <div className="px-6 sm:px-8 pt-5 pb-3">
        <p className="text-[10px] tracking-[0.22em] uppercase text-[#8A9272] mb-3">
          {localize('Suggested')}
        </p>
        <div className="flex flex-wrap gap-2">
          {SUGGESTED_QUESTIONS.map((q) => (
            <button
              key={q}
              id={`suggestion-${q.replace(/\W+/g, '-').toLowerCase()}`}
              onClick={() => handleSuggestion(q)}
              disabled={isLoading}
              className={[
                'inline-flex items-center gap-1.5 px-3.5 py-1.5 rounded-full text-xs font-medium',
                'border border-[#C4BC9E] bg-white/70 text-[#3D4A2E]',
                'hover:bg-[#6E7A4E] hover:text-white hover:border-[#6E7A4E]',
                'transition-all duration-200 cursor-pointer select-none',
                'disabled:opacity-50 disabled:cursor-not-allowed',
              ].join(' ')}
            >
              <ChevronRight className="w-3 h-3 opacity-60" />
              {localize(q)}
            </button>
          ))}
        </div>
      </div>

      {/* Text input */}
      <div className="px-6 sm:px-8 pb-5">
        <div className="relative flex items-center gap-2 bg-white rounded-xl border border-[#C8C0A8] shadow-sm focus-within:border-[#6E7A4E] focus-within:ring-1 focus-within:ring-[#6E7A4E]/30 transition-all duration-200">
          <Leaf className="absolute left-3.5 w-4 h-4 text-[#9BAF6A] pointer-events-none flex-shrink-0" />
          <input
            ref={inputRef}
            id="crop-assistant-input"
            type="text"
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder={localize('Ask about this crop analysis…')}
            maxLength={500}
            disabled={isLoading}
            aria-label="Ask the AI Crop Assistant"
            className={[
              'flex-1 pl-9 pr-3 py-3 bg-transparent text-sm text-[#1C2A1A] placeholder:text-[#A8A090]',
              'outline-none rounded-xl font-light',
              'disabled:opacity-50',
            ].join(' ')}
          />
          {question && !isLoading && (
            <button
              onClick={() => setQuestion('')}
              aria-label="Clear question"
              className="mr-1 p-1 rounded-full text-[#A8A090] hover:text-[#5A6150] transition-colors"
            >
              <X className="w-3.5 h-3.5" />
            </button>
          )}
          <button
            id="crop-assistant-send"
            onClick={handleSend}
            disabled={isLoading || !question.trim()}
            aria-label="Ask the AI Crop Assistant"
            className={[
              'mr-2 flex-shrink-0 flex items-center gap-1.5 px-4 py-2 rounded-lg text-xs font-semibold',
              'bg-[#3D4A2E] text-[#E8D5A3] shadow-sm',
              'hover:bg-[#6E7A4E] transition-all duration-200',
              'disabled:opacity-40 disabled:cursor-not-allowed',
            ].join(' ')}
          >
            {isLoading ? (
              <Loader2 className="w-3.5 h-3.5 animate-spin" />
            ) : (
              <Send className="w-3.5 h-3.5" />
            )}
            {localize('Ask')}
          </button>
        </div>
      </div>

      {/* Loading state */}
      {isLoading && (
        <div className="px-6 sm:px-8 pb-6">
          <div className="rounded-xl bg-white/80 border border-[#DDD6C4] p-5">
            <div className="flex items-center gap-3 mb-3">
              <div className="w-7 h-7 rounded-full bg-[#6E7A4E] flex items-center justify-center flex-shrink-0">
                <Sparkles className="w-3.5 h-3.5 text-[#E8D5A3]" />
              </div>
              <span className="text-xs text-[#6E7A4E] font-medium tracking-wide uppercase">
                {localize('AI Crop Assistant · Analysing…')}
              </span>
            </div>
            <div className="space-y-2 pl-10">
              <div className="h-3 bg-[#E8E4D8] rounded-full w-3/4 animate-pulse" />
              <div className="h-3 bg-[#E8E4D8] rounded-full w-5/6 animate-pulse" />
              <div className="h-3 bg-[#E8E4D8] rounded-full w-2/3 animate-pulse" />
            </div>
          </div>
        </div>
      )}

      {/* Error state */}
      {error && !isLoading && (
        <div className="px-6 sm:px-8 pb-6">
          <div className="rounded-xl bg-[#FFF8F0] border border-[#E8C882] p-4 flex items-start gap-3">
            <AlertTriangle className="w-4 h-4 text-[#B87333] flex-shrink-0 mt-0.5" />
            <div>
              <p className="text-sm font-medium text-[#7A4A1A]">
                {localize('AI Crop Assistant is temporarily unavailable.')}
              </p>
              <p className="text-xs text-[#9A6A3A] mt-1 font-light">
                {localize('Your crop analysis is still available above.')} ({error})
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Response card */}
      {response && !isLoading && (
        <div ref={responseRef} className="px-6 sm:px-8 pb-7">
          <div className="rounded-xl bg-white border border-[#DDD6C4] overflow-hidden shadow-sm">
            {/* Card header */}
            <div className="flex items-center gap-2.5 px-5 py-3.5 bg-gradient-to-r from-[#F0EAD8] to-[#F8F5EC] border-b border-[#DDD6C4]">
              <div className="w-6 h-6 rounded-full bg-[#6E7A4E] flex items-center justify-center flex-shrink-0">
                <Sparkles className="w-3 h-3 text-[#E8D5A3]" />
              </div>
              <span className="text-[11px] tracking-[0.18em] uppercase text-[#5A6150] font-medium">
                {localize('AI Crop Assistant')}
              </span>
              {!response.grounded && (
                <span className="ml-auto inline-flex items-center gap-1 px-2 py-0.5 rounded-full bg-[#FFF3DC] border border-[#E8C882] text-[9px] tracking-wide uppercase text-[#7A5A20]">
                  <AlertTriangle className="w-2.5 h-2.5" />
                  {localize('Limited context')}
                </span>
              )}
            </div>

            {/* Answer body */}
            <div className="px-5 py-4">
              <div
                className="assistant-markdown"
                dangerouslySetInnerHTML={{ __html: renderedAnswer }}
              />
            </div>

            {/* Context used pills */}
            {response.context_used.length > 0 && (
              <div className="px-5 pb-4 flex flex-wrap items-center gap-1.5">
                <span className="text-[10px] text-[#8A9272] uppercase tracking-wide mr-1">
                  {localize('Context used:')}
                </span>
                {response.context_used.map((key) => (
                  <span
                    key={key}
                    className="inline-block px-2 py-0.5 rounded-full bg-[#EEF4E8] border border-[#C4D4A0] text-[10px] text-[#4A6030] font-medium"
                  >
                    {localize(CONTEXT_LABEL_MAP[key] || key)}
                  </span>
                ))}
              </div>
            )}

            {/* Warning */}
            {response.warning && (
              <div className="px-5 pb-4">
                <p className="text-[10px] text-[#9A7A3A] flex items-center gap-1.5">
                  <AlertTriangle className="w-3 h-3 flex-shrink-0" />
                  {localize(response.warning)}
                </p>
              </div>
            )}
            {translationWarning && (
              <div className="px-5 pb-4">
                <p className="text-[10px] text-[#9A7A3A] flex items-center gap-1.5" role="status">
                  {localize(translationWarning)}
                </p>
              </div>
            )}
          </div>
        </div>
      )}
    </section>
  );
}
