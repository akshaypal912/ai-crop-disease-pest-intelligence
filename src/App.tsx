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

import type { AnalysisResult, CropType, GrowthStage } from './types/crop';
import { analyzeCrop, getHistory, deleteFromHistory, clearHistory } from './services/api';

export function App() {
  const [activePage, setActivePage] = useState<AppPage>('home');
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [currentStage, setCurrentStage] = useState(0);
  const [activeResult, setActiveResult] = useState<AnalysisResult | null>(null);
  const [historyItems, setHistoryItems] = useState<AnalysisResult[]>([]);

  useEffect(() => {
    setHistoryItems(getHistory());
  }, []);

  const allAlerts = historyItems.flatMap((h) => h.alerts || []);

  const goTo = (page: AppPage) => {
    if (page !== 'result') {
      setActiveResult(null);
    }
    setActivePage(page);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const handleStartAnalysis = async (
    imageSource: File | string,
    cropType: CropType,
    location: string,
    growthStage: GrowthStage
  ) => {
    setIsAnalyzing(true);
    setCurrentStage(0);

    try {
      const result = await analyzeCrop(
        imageSource,
        cropType,
        location,
        growthStage,
        (stageIndex) => setCurrentStage(stageIndex)
      );
      await new Promise((r) => setTimeout(r, 400));
      setActiveResult(result);
      setHistoryItems(getHistory());
      setActivePage('result');
      window.scrollTo({ top: 0, behavior: 'smooth' });
    } catch (err) {
      console.error('Analysis error:', err);
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleSelectHistoryItem = (item: AnalysisResult) => {
    setActiveResult(item);
    setActivePage('result');
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const handleDeleteHistoryItem = (id: string) => {
    const updated = deleteFromHistory(id);
    setHistoryItems(updated);
    if (activeResult?.id === id) {
      setActiveResult(null);
      setActivePage('history');
    }
  };

  const handleClearAllHistory = () => {
    clearHistory();
    setHistoryItems([]);
    setActiveResult(null);
  };

  return (
    <div className="min-h-screen bg-[#FBF7EE] text-[#161A12] selection:bg-[#6E7A4E] selection:text-white">
      <Navbar
        activePage={activePage}
        onNavigate={goTo}
        overlay={activePage === 'home'}
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
          <UploadSection onStartAnalysis={handleStartAnalysis} isAnalyzing={isAnalyzing} />
        </main>
      )}

      {activePage === 'result' && activeResult && (
        <ResultsView
          result={activeResult}
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
          alerts={allAlerts}
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
