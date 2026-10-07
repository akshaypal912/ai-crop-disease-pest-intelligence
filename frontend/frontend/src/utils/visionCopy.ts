/** Provider-neutral copy for API strings that may still say "Gemini visual assessment". */
export function neutralizeVisionProviderCopy(text: string): string {
  return text.replace(/\bGemini visual assessment\b/gi, 'AI visual assessment');
}
