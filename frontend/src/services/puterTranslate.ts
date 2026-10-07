/**
 * Farmer-facing text translation via Puter.js (LLM-backed, no app API keys).
 * @see https://developer.puter.com/tutorials/free-unlimited-translation-api/
 */

import { puter } from '@heyputer/puter.js';
import type { ChatResponse } from '@heyputer/puter.js';
import type { FarmerLanguageCode } from '../i18n/languages';

const TRANSLATION_MODEL =
  (import.meta.env.VITE_PUTER_TRANSLATION_MODEL as string | undefined)?.trim() ||
  'gpt-5.4-nano';

/** ISO-style codes supported by the farmer language selector (English = passthrough). */
export const PUTER_SUPPORTED_LANGUAGE_CODES = new Set<FarmerLanguageCode>([
  'en',
  'hi',
  'bn',
  'mr',
  'gu',
  'pa',
  'ta',
  'te',
  'kn',
  'ml',
  'ur',
]);

const LANGUAGE_DISPLAY_NAMES: Record<string, string> = {
  hi: 'Hindi',
  bn: 'Bengali',
  mr: 'Marathi',
  gu: 'Gujarati',
  pa: 'Punjabi',
  ta: 'Tamil',
  te: 'Telugu',
  kn: 'Kannada',
  ml: 'Malayalam',
  ur: 'Urdu',
};

function targetLanguageName(code: string): string {
  return LANGUAGE_DISPLAY_NAMES[code] ?? code;
}

function extractChatText(response: ChatResponse | string): string {
  if (typeof response === 'string') return response.trim();
  const content = response.message?.content;
  if (typeof content === 'string') return content.trim();
  if (Array.isArray(content)) {
    return content
      .map((part) => {
        if (typeof part === 'string') return part;
        if (part && typeof part === 'object' && 'text' in part) {
          return String((part as { text?: string }).text ?? '');
        }
        return '';
      })
      .join('')
      .trim();
  }
  return '';
}

function buildTranslationPrompt(text: string, targetLanguageCode: string): string {
  const languageName = targetLanguageName(targetLanguageCode);
  return (
    `Translate the following agricultural / crop-health UI text from English to ${languageName}. ` +
    `Rules:\n` +
    `- Output ONLY the translated text, no quotes, labels, or explanations.\n` +
    `- Keep numbers, percentages, units (°C, mm, %), coordinates, and scientific disease names unchanged.\n` +
    `- Do not add markdown unless the source contains markdown.\n\n` +
    `${text}`
  );
}

/**
 * Translate one English string. Returns original text on failure.
 */
export async function puterTranslateText(
  text: string,
  targetLanguageCode: string
): Promise<{ translated: string; available: boolean }> {
  const target = targetLanguageCode.trim().toLowerCase();
  if (target === 'en' || !text.trim()) {
    return { translated: text, available: true };
  }
  if (!PUTER_SUPPORTED_LANGUAGE_CODES.has(target as FarmerLanguageCode)) {
    return { translated: text, available: false };
  }

  try {
    const response = await puter.ai.chat(buildTranslationPrompt(text, target), {
      model: TRANSLATION_MODEL,
      temperature: 0.2,
      normalize: true,
    });
    const translated = extractChatText(response);
    if (!translated) {
      return { translated: text, available: false };
    }
    return { translated, available: true };
  } catch {
    return { translated: text, available: false };
  }
}

const BATCH_CONCURRENCY = 4;

async function mapWithConcurrency<T, R>(
  items: T[],
  mapper: (item: T, index: number) => Promise<R>,
  concurrency: number
): Promise<R[]> {
  if (items.length === 0) return [];
  const results = new Array<R>(items.length);
  let nextIndex = 0;

  async function worker(): Promise<void> {
    while (nextIndex < items.length) {
      const index = nextIndex;
      nextIndex += 1;
      results[index] = await mapper(items[index], index);
    }
  }

  const workers = Array.from({ length: Math.min(concurrency, items.length) }, () => worker());
  await Promise.all(workers);
  return results;
}

/**
 * Batch translate preserving order; dedupe is handled by the caller.
 */
export async function puterTranslateTexts(
  texts: string[],
  targetLanguageCode: string
): Promise<{ translations: string[]; available: boolean }> {
  const target = targetLanguageCode.trim().toLowerCase();
  if (target === 'en') {
    return { translations: [...texts], available: true };
  }

  const outcomes = await mapWithConcurrency(
    texts,
    async (text) => puterTranslateText(text, target),
    BATCH_CONCURRENCY
  );

  const translations = outcomes.map((o, i) => o.translated ?? texts[i]);
  const available = outcomes.every((o) => o.available);
  return { translations, available };
}
