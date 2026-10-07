import type { AppPage } from '../components/Navbar';
import { getDiseaseBySlug } from '../data/diseaseLibrary';

export function diseaseDetailPath(slug: string): string {
  return `/diseases/${slug}`;
}

export const DISEASE_LIBRARY_RETURN_PATH = '/detect';

export type ParsedRoute =
  | { type: 'disease-detail'; slug: string }
  | { type: 'app'; page: AppPage };

export function parsePathname(pathname: string): ParsedRoute {
  const diseaseMatch = pathname.match(/^\/diseases\/([a-z0-9-]+)\/?$/);
  if (diseaseMatch) {
    return { type: 'disease-detail', slug: diseaseMatch[1] };
  }

  if (pathname === '/detect' || pathname === '/detect/') {
    return { type: 'app', page: 'detect' };
  }
  if (pathname === '/history' || pathname === '/history/') {
    return { type: 'app', page: 'history' };
  }
  if (pathname === '/dashboard' || pathname === '/dashboard/') {
    return { type: 'app', page: 'dashboard' };
  }

  return { type: 'app', page: 'home' };
}

export function pathForAppPage(page: AppPage): string {
  if (page === 'home') return '/';
  if (page === 'result') return DISEASE_LIBRARY_RETURN_PATH;
  return `/${page}`;
}

export function isValidDiseaseSlug(slug: string): boolean {
  return Boolean(getDiseaseBySlug(slug));
}
