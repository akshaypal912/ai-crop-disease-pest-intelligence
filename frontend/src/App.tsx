import { useState, useEffect } from 'react';
import { Navbar, type AppPage } from './components/Navbar';
import { Hero } from './components/Hero';
import { MissionSection } from './components/MissionSection';
import { CropCollage } from './components/CropCollage';
import { EditorialFeature } from './components/EditorialFeature';
import { UploadSection } from './components/UploadSection';
import { AnalysisProgress } from './components/AnalysisProgress';
import { ResultsView } from './components/ResultsView';
import { HistorySection } from './components/HistorySection';
import { DashboardSection } from './components/DashboardSection';
import { Footer } from './components/Footer';
import { useFarmerLanguage } from './i18n/FarmerLanguageContext';
import { APP_SHELL_UI_STRINGS } from './utils/collectReportText';

import type { CropAnalysisSession, CropDeclarationChoice } from './types/session';
import type { GrowthStage } from './types/crop';
import {
  predictCrop,
  getHistory,
  deleteFromHistory,
  clearHistory,
  fetchHealth,
  ApiError,
  getApiBaseUrl,
} from './services/api';
import type { HealthResponse } from './types/predict';

export function App() {
  const { ingestTranslations } = useFarmerLanguage();
  const [activePage, setActivePage] = useState<AppPage>('home');
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [currentStage, setCurrentStage] = useState(0);
  const [activeSession, setActiveSession] = useState<CropAnalysisSession | null>(null);
  const [historyItems, setHistoryItems] = useState<CropAnalysisSession[]>([]);
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [healthError, setHealthError] = useState<string | null>(null);
  const [analysisError, setAnalysisError] = useState<string | null>(null);

  useEffect(() => {
    setHistoryItems(getHistory());
    fetchHealth()
      .then(setHealth)
      .catch((e) => setHealthError(e instanceof ApiError ? e.detail : 'Unavailable'));
    const interval = setInterval(() => {
      fetchHealth()
        .then((h) => {
          setHealth(h);
          setHealthError(null);
        })
        .catch(() => setHealthError('Unavailable'));
    }, 30_000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    void ingestTranslations(APP_SHELL_UI_STRINGS);
  }, [ingestTranslations]);

  const goTo = (page: AppPage) => {
    if (page !== 'result') setActiveSession(null);
    setActivePage(page);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const handleStartAnalysis = async (
    imageSource: File | string,
    cropDeclaration: CropDeclarationChoice,
    city: string,
    growthStage: GrowthStage
  ) => {
    setIsAnalyzing(true);
    setCurrentStage(0);
    setAnalysisError(null);

    try {
      const session = await predictCrop(imageSource, {
        cropDeclaration,
        city,
        growthStage,
        onStageUpdate: setCurrentStage,
      });
      setActiveSession(session);
      setHistoryItems(getHistory());
      setActivePage('result');
      window.scrollTo({ top: 0, behavior: 'smooth' });
    } catch (err) {
      const msg =
        err instanceof ApiError
          ? err.detail
          : err instanceof Error
            ? err.message
            : 'Analysis failed';
      setAnalysisError(msg);
      if (import.meta.env.DEV) console.error('Analysis error:', err);
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleSelectHistoryItem = (item: CropAnalysisSession) => {
    setActiveSession(item);
    setActivePage('result');
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const handleDeleteHistoryItem = (id: string) => {
    const updated = deleteFromHistory(id);
    setHistoryItems(updated);
    if (activeSession?.id === id) {
      setActiveSession(null);
      setActivePage('history');
    }
  };

  const handleClearAllHistory = () => {
    clearHistory();
    setHistoryItems([]);
    setActiveSession(null);
  };

  const backendConnected = Boolean(health) && !healthError;

  return (
    <div className="min-h-screen bg-[#FBF7EE] text-[#161A12] selection:bg-[#6E7A4E] selection:text-white">
      <Navbar
        activePage={activePage}
        onNavigate={goTo}
        overlay={activePage === 'home'}
        backendConnected={backendConnected}
        apiBaseUrl={getApiBaseUrl()}
      />

      {activePage === 'home' && (
        <main>
          <Hero onDetect={() => goTo('detect')} onExplore={() => {
            const el = document.getElementById('explore');
            if (el) el.scrollIntoView({ behavior: 'smooth' });
          }} />
          <MissionSection onDetect={() => goTo('detect')} />
          <CropCollage />
          <EditorialFeature onDetect={() => goTo('detect')} />
        </main>
      )}

      {activePage === 'detect' && (
        <main>
          <UploadSection
            onStartAnalysis={handleStartAnalysis}
            isAnalyzing={isAnalyzing}
            analysisError={analysisError}
            backendConnected={backendConnected}
          />
        </main>
      )}

      {activePage === 'result' && activeSession && (
        <ResultsView
          session={activeSession}
          onBack={() => goTo('detect')}
          onAnalyzeAnother={() => goTo('detect')}
        />
      )}

      {activePage === 'history' && (
        <HistorySection
          historyItems={historyItems}
          onSelectResult={handleSelectHistoryItem}
          onClearHistory={handleClearAllHistory}
          onDeleteItem={handleDeleteHistoryItem}
        />
      )}

      {activePage === 'dashboard' && (
        <DashboardSection
          historyItems={historyItems}
          onDetect={() => goTo('detect')}
          onOpenResult={handleSelectHistoryItem}
        />
      )}

      <AnalysisProgress currentStage={currentStage} isOpen={isAnalyzing} />
      <Footer onNavigate={goTo} />
    </div>
  );
}

export default App;
