import type { HealthResponse, PredictionResponse } from '../types/predict';
import type { CropAnalysisSession, CropDeclarationChoice } from '../types/session';
import { buildPredictQueryParams, normalizeGrowthStage } from './predictParams';

const HISTORY_STORAGE_KEY = 'cropsense_backend_history_v1';

export function getApiBaseUrl(): string {
  const raw = import.meta.env.VITE_API_BASE_URL || import.meta.env.VITE_API_URL;
  if (raw) {
    return String(raw).replace(/\/$/, '').replace(/\/api$/, '');
  }
  // Vite dev: same-origin requests hit the dev server and are proxied to FastAPI.
  if (import.meta.env.DEV && typeof window !== 'undefined') {
    return window.location.origin;
  }
  return 'http://localhost:8000';
}

/** Build an absolute URL for a FastAPI path (works with dev proxy and direct backend). */
export function apiUrl(path: string): string {
  const normalized = path.startsWith('/') ? path : `/${path}`;
  const base = getApiBaseUrl();
  if (base.startsWith('http://') || base.startsWith('https://')) {
    return new URL(normalized, base.endsWith('/') ? base : `${base}/`).href;
  }
  return normalized;
}

export interface ProgressStage {
  stage: number;
  title: string;
  description: string;
}

export const ANALYSIS_STAGES: ProgressStage[] = [
  { stage: 1, title: 'Uploading image', description: 'Sending your photo to the CropSense API' },
  { stage: 2, title: 'Running visual assessment', description: 'Optional AI visual assessment (Phase 1)' },
  { stage: 3, title: 'Running validated specialists', description: 'Specialist router and tomato disease model when allowed' },
  { stage: 4, title: 'Checking pests', description: 'Pest24 YOLO detection (independent of disease routing)' },
  { stage: 5, title: 'Building crop health report', description: 'Weather context, risk, recommendations, and alerts' },
];

export class ApiError extends Error {
  status: number;
  detail: string;

  constructor(status: number, detail: string) {
    super(detail);
    this.status = status;
    this.detail = detail;
  }
}

export async function fetchHealth(): Promise<HealthResponse> {
  const res = await fetch(apiUrl('/health'), { method: 'GET' });
  if (!res.ok) {
    throw new ApiError(res.status, `Health check failed (${res.status})`);
  }
  return res.json() as Promise<HealthResponse>;
}

async function imageSourceToFile(imageSource: File | string, filename = 'upload.jpg'): Promise<File> {
  if (imageSource instanceof File) return imageSource;
  const res = await fetch(imageSource);
  if (!res.ok) throw new ApiError(res.status, 'Could not load image for upload');
  const blob = await res.blob();
  return new File([blob], filename, { type: blob.type || 'image/jpeg' });
}

export async function predictCrop(
  imageSource: File | string,
  options: {
    cropDeclaration: CropDeclarationChoice;
    city?: string;
    growthStage?: string;
    onStageUpdate?: (stageIndex: number) => void;
  }
): Promise<CropAnalysisSession> {
  const file = await imageSourceToFile(
    imageSource,
    imageSource instanceof File ? imageSource.name : 'sample.jpg'
  );

  const query = buildPredictQueryParams({
    cropDeclaration: options.cropDeclaration,
    city: options.city,
    growthStage: options.growthStage ? normalizeGrowthStage(options.growthStage) : undefined,
  });

  const url = new URL(apiUrl('/predict'));
  Object.entries(query).forEach(([k, v]) => url.searchParams.set(k, v));

  for (let i = 0; i < ANALYSIS_STAGES.length - 1; i++) {
    options.onStageUpdate?.(i);
    await new Promise((r) => setTimeout(r, 120));
  }

  const controller = new AbortController();
  const timeoutMs = 120_000;
  const timer = setTimeout(() => controller.abort(), timeoutMs);

  let response: Response;
  try {
    response = await fetch(url.toString(), {
      method: 'POST',
      body: (() => {
        const fd = new FormData();
        fd.append('file', file);
        return fd;
      })(),
      signal: controller.signal,
    });
  } catch (err) {
    if (err instanceof DOMException && err.name === 'AbortError') {
      throw new ApiError(408, 'Analysis timed out. Try a smaller image or try again.');
    }
    throw new ApiError(0, 'Network error — is the FastAPI server running on port 8000?');
  } finally {
    clearTimeout(timer);
  }

  options.onStageUpdate?.(ANALYSIS_STAGES.length - 1);

  if (!response.ok) {
    let detail = response.statusText;
    try {
      const body = await response.json();
      detail = body.detail || JSON.stringify(body);
    } catch {
      detail = await response.text().catch(() => detail);
    }
    throw new ApiError(response.status, detail);
  }

  const report = (await response.json()) as PredictionResponse;
  const imageUrl = URL.createObjectURL(file);

  const session: CropAnalysisSession = {
    id: `analysis-${Date.now()}`,
    timestamp: new Date().toISOString(),
    imageUrl,
    cropDeclaration: options.cropDeclaration,
    city: options.city,
    growthStage: options.growthStage,
    report,
  };

  saveSessionToHistory(session);
  return session;
}

export function getHistory(): CropAnalysisSession[] {
  try {
    const raw = localStorage.getItem(HISTORY_STORAGE_KEY);
    if (!raw) return [];
    return JSON.parse(raw) as CropAnalysisSession[];
  } catch {
    return [];
  }
}

export function saveSessionToHistory(session: CropAnalysisSession): void {
  const history = [session, ...getHistory().filter((h) => h.id !== session.id)].slice(0, 50);
  localStorage.setItem(HISTORY_STORAGE_KEY, JSON.stringify(history));
}

export function deleteFromHistory(id: string): CropAnalysisSession[] {
  const history = getHistory().filter((item) => item.id !== id);
  localStorage.setItem(HISTORY_STORAGE_KEY, JSON.stringify(history));
  return history;
}

export function clearHistory(): void {
  localStorage.removeItem(HISTORY_STORAGE_KEY);
}

// ---------------------------------------------------------------------------
// AI Crop Assistant
// ---------------------------------------------------------------------------

export interface CropAssistantResponse {
  answer: string;
  grounded: boolean;
  context_used: string[];
  warning: string | null;
}

export async function askCropAssistant(
  question: string,
  context: PredictionResponse,
  targetLanguage = 'en'
): Promise<CropAssistantResponse> {
  const controller = new AbortController();
  const timeoutMs = 90_000;
  const timer = setTimeout(() => controller.abort(), timeoutMs);

  let response: Response;
  try {
    response = await fetch(apiUrl('/assistant'), {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ question, context, target_language: targetLanguage }),
      signal: controller.signal,
    });
  } catch (err) {
    if (err instanceof DOMException && err.name === 'AbortError') {
      throw new ApiError(408, 'Assistant request timed out.');
    }
    throw new ApiError(0, 'Network error reaching assistant endpoint.');
  } finally {
    clearTimeout(timer);
  }

  if (!response.ok) {
    let detail = response.statusText;
    try {
      const body = await response.json();
      detail = body.detail || JSON.stringify(body);
    } catch {
      detail = await response.text().catch(() => detail);
    }
    throw new ApiError(response.status, detail);
  }

  return response.json() as Promise<CropAssistantResponse>;
}
