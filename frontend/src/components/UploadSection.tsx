import React, { useEffect } from 'react';
import { Upload, X, Check, MapPin, Layers } from 'lucide-react';
import type { GrowthStage, SampleCropImage } from '../types/crop';
import type { CropDeclarationChoice } from '../types/session';
import { SAMPLE_CROP_IMAGES } from '../services/cropSamples';
import { PageBanner } from './PageBanner';
import { IMAGES } from '../data/images';
import { useFarmerLanguage } from '../i18n/FarmerLanguageContext';
import { UPLOAD_UI_STRINGS } from '../utils/collectReportText';

interface UploadSectionProps {
  onStartAnalysis: (
    imageSource: File | string,
    cropDeclaration: CropDeclarationChoice,
    city: string,
    growthStage: GrowthStage
  ) => void;
  isAnalyzing: boolean;
  analysisError?: string | null;
  backendConnected?: boolean;
}

export const UploadSection: React.FC<UploadSectionProps> = ({
  onStartAnalysis,
  isAnalyzing,
  analysisError,
  backendConnected,
}) => {
  const { localize, ingestTranslations } = useFarmerLanguage();
  const [selectedFile, setSelectedFile] = React.useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = React.useState<string | null>(null);
  const [selectedSample, setSelectedSample] = React.useState<SampleCropImage | null>(null);
  const [cropDeclaration, setCropDeclaration] = React.useState<CropDeclarationChoice>('auto');
  const [city, setCity] = React.useState('');
  const [growthStage, setGrowthStage] = React.useState<GrowthStage>('vegetative');
  const [isDragOver, setIsDragOver] = React.useState(false);
  const fileInputRef = React.useRef<HTMLInputElement>(null);

  useEffect(() => {
    void ingestTranslations(UPLOAD_UI_STRINGS);
  }, [ingestTranslations]);

  const declarationLabels: Record<CropDeclarationChoice, string> = {
    auto: localize('Auto / Not specified'),
    tomato: localize('Tomato'),
    other: localize('Other / Non-Tomato'),
  };

  const handleFileChange = (file: File) => {
    if (!file.type.startsWith('image/')) return;
    setSelectedFile(file);
    setSelectedSample(null);
    setPreviewUrl(URL.createObjectURL(file));
  };

  const handleSelectSample = (sample: SampleCropImage) => {
    setSelectedSample(sample);
    setSelectedFile(null);
    setPreviewUrl(sample.imageUrl);
  };

  const handleClearImage = () => {
    setSelectedFile(null);
    setSelectedSample(null);
    setPreviewUrl(null);
    if (fileInputRef.current) fileInputRef.current.value = '';
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!previewUrl) return;
    const source = selectedFile ? selectedFile : (selectedSample ? selectedSample.imageUrl : previewUrl);
    onStartAnalysis(source, cropDeclaration, city, growthStage);
  };

  return (
    <div className="bg-[#FBF7EE]">
      <PageBanner
        kicker={localize('Detect')}
        title={localize('Bring the field to the lens')}
        subtitle={localize(
          'Upload a leaf or canopy photograph. Results come from the live FastAPI pipeline — no mock diagnoses.'
        )}
        image={IMAGES.greenRows}
      />

      <div className="max-w-[1400px] mx-auto px-6 sm:px-10 py-16 lg:py-20 space-y-14">
        {backendConnected === false && (
          <p className="border border-[#8A3E38] bg-[#F6F1E6] p-4 text-sm text-[#5A6150]">
            {localize('Backend unavailable. Start FastAPI with')}{' '}
            <code className="text-[#161A12]">uvicorn api.main:app --port 8000</code>{' '}
            {localize('before analyzing.')}
          </p>
        )}
        {analysisError && (
          <p className="border border-[#8A3E38] bg-[#F6F1E6] p-4 text-sm text-[#8A3E38]">{analysisError}</p>
        )}

        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-4">
          {SAMPLE_CROP_IMAGES.map((sample) => {
            const isSelected = selectedSample?.id === sample.id;
            return (
              <button key={sample.id} type="button" onClick={() => handleSelectSample(sample)} className="text-left group">
                <div className={`relative h-36 overflow-hidden ${isSelected ? 'ring-2 ring-[#1C2A1A] ring-offset-4 ring-offset-[#FBF7EE]' : ''}`}>
                  <img src={sample.imageUrl} alt={sample.name} className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-700" />
                  {isSelected && (
                    <span className="absolute top-2 right-2 w-6 h-6 rounded-full bg-[#1C2A1A] text-[#E8D5A3] flex items-center justify-center">
                      <Check className="w-3.5 h-3.5" />
                    </span>
                  )}
                </div>
                <span className="mt-2 block font-display text-[#161A12]">{sample.name}</span>
              </button>
            );
          })}
        </div>

        <form onSubmit={handleSubmit} className="grid grid-cols-1 lg:grid-cols-12 gap-10">
          <div
            onDragOver={(e) => { e.preventDefault(); setIsDragOver(true); }}
            onDragLeave={() => setIsDragOver(false)}
            onDrop={(e) => {
              e.preventDefault();
              setIsDragOver(false);
              if (e.dataTransfer.files?.[0]) handleFileChange(e.dataTransfer.files[0]);
            }}
            className={`lg:col-span-7 min-h-[360px] border border-dashed p-8 flex items-center justify-center ${
              isDragOver ? 'border-[#1C2A1A] bg-[#EFE8D8]' : 'border-[#C9C0A8] bg-[#F6F1E6]'
            }`}
          >
            <input
              type="file"
              ref={fileInputRef}
              accept="image/*"
              className="hidden"
              onChange={(e) => {
                if (e.target.files?.[0]) handleFileChange(e.target.files[0]);
              }}
            />

            {!previewUrl ? (
              <div className="text-center space-y-5 max-w-md">
                <Upload className="w-8 h-8 mx-auto text-[#6E7A4E]" />
                <h3 className="font-display text-3xl text-[#161A12]">{localize('Drop a crop image')}</h3>
                <p className="text-sm text-[#5A6150] font-light">{localize('JPEG, PNG or WEBP.')}</p>
                <button type="button" onClick={() => fileInputRef.current?.click()} className="px-5 py-2 rounded-full bg-[#1C2A1A] text-[#F6F1E6] text-sm">
                  {localize('Browse')}
                </button>
              </div>
            ) : (
              <div className="relative w-full max-w-lg">
                <img src={previewUrl} alt="Crop preview" className="w-full h-72 object-cover" />
                <button type="button" onClick={handleClearImage} className="absolute top-3 right-3 p-2 bg-[#1C2A1A] text-white">
                  <X className="w-4 h-4" />
                </button>
              </div>
            )}
          </div>

          <div className="lg:col-span-5 space-y-6 bg-[#6E7A4E] text-[#F6F1E6] p-8">
            <p className="text-[11px] tracking-[0.28em] uppercase text-[#E8D5A3]">{localize('Analysis settings')}</p>

            <fieldset className="space-y-3">
              <legend className="text-xs uppercase tracking-widest">{localize('Crop declaration')}</legend>
              <p className="text-xs text-[#E8D5A3]/90 font-light">
                {localize(
                  'Crop declaration enables a validated crop-specific specialist. AI visual assessment does not automatically activate a specialist.'
                )}
              </p>
              {(['auto', 'tomato', 'other'] as CropDeclarationChoice[]).map((key) => (
                <label key={key} className="flex items-center gap-2 text-sm cursor-pointer">
                  <input
                    type="radio"
                    name="cropDeclaration"
                    checked={cropDeclaration === key}
                    onChange={() => setCropDeclaration(key)}
                  />
                  {declarationLabels[key]}
                </label>
              ))}
            </fieldset>

            <label className="block space-y-2">
              <span className="text-xs uppercase tracking-widest flex items-center gap-2"><Layers className="w-3.5 h-3.5" /> {localize('Growth stage')}</span>
              <select
                value={growthStage}
                onChange={(e) => setGrowthStage(e.target.value as GrowthStage)}
                className="w-full bg-[#5F6A42] text-white border-b border-white/30 py-2 text-sm focus:outline-none"
              >
                <option value="seedling">{localize('Seedling')}</option>
                <option value="vegetative">{localize('Vegetative')}</option>
                <option value="flowering">{localize('Flowering')}</option>
                <option value="fruiting">{localize('Fruiting')}</option>
                <option value="harvest">{localize('Ripening / harvest')}</option>
              </select>
            </label>

            <label className="block space-y-2">
              <span className="text-xs uppercase tracking-widest flex items-center gap-2"><MapPin className="w-3.5 h-3.5" /> {localize('City (optional)')}</span>
              <input
                type="text"
                value={city}
                onChange={(e) => setCity(e.target.value)}
                placeholder={localize('e.g. Mumbai')}
                className="w-full bg-transparent border-b border-white/30 py-2 text-sm focus:outline-none placeholder:text-white/50"
              />
            </label>

            <button
              type="submit"
              disabled={!previewUrl || isAnalyzing || backendConnected === false}
              className="w-full mt-4 py-3 rounded-full bg-[#E8D5A3] text-[#1C2A1A] font-semibold disabled:opacity-40"
            >
              {isAnalyzing ? localize('Analyzing crop…') : localize('Analyze crop health')}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
