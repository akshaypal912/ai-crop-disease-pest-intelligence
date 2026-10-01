import React from 'react';
import { Upload, Camera, Image as ImageIcon, X, Check, MapPin, Sprout, Layers } from 'lucide-react';
import type { CropType, GrowthStage, SampleCropImage } from '../types/crop';
import { SAMPLE_CROP_IMAGES } from '../services/cropSamples';
import { PageBanner } from './PageBanner';
import { IMAGES } from '../data/images';

interface UploadSectionProps {
  onStartAnalysis: (
    imageSource: File | string,
    cropType: CropType,
    location: string,
    growthStage: GrowthStage
  ) => void;
  isAnalyzing: boolean;
}

export const UploadSection: React.FC<UploadSectionProps> = ({
  onStartAnalysis,
  isAnalyzing
}) => {
  const [selectedFile, setSelectedFile] = React.useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = React.useState<string | null>(null);
  const [selectedSample, setSelectedSample] = React.useState<SampleCropImage | null>(null);
  const [cropType, setCropType] = React.useState<CropType>('tomato');
  const [location, setLocation] = React.useState('Plot 4B — North Field');
  const [growthStage, setGrowthStage] = React.useState<GrowthStage>('fruiting');
  const [isDragOver, setIsDragOver] = React.useState(false);
  const fileInputRef = React.useRef<HTMLInputElement>(null);

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
    setCropType(sample.cropType);
    if (sample.mockResult.growthStage) setGrowthStage(sample.mockResult.growthStage);
    if (sample.mockResult.location) setLocation(sample.mockResult.location);
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
    onStartAnalysis(source, cropType, location, growthStage);
  };

  return (
    <div className="bg-[#FBF7EE]">
      <PageBanner
        kicker="Detect"
        title="Bring the field to the lens"
        subtitle="Upload a leaf or canopy photograph. CropSense reads texture, lesions and pest signs with agricultural care."
        image={IMAGES.greenRows}
      />

      <div className="max-w-[1400px] mx-auto px-6 sm:px-10 py-16 lg:py-20 space-y-14">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-10 items-end">
          <div className="lg:col-span-7">
            <p className="text-[11px] tracking-[0.28em] uppercase text-[#6E7A4E] mb-3">Sample leaves</p>
            <h2 className="font-display text-4xl sm:text-5xl text-[#161A12] leading-tight">
              Start with a living specimen
            </h2>
          </div>
          <p className="lg:col-span-5 text-[#5A6150] font-light">
            Choose a prepared field sample, or drop in your own photograph. Context helps the model — crop type, growth stage, and plot still matter.
          </p>
        </div>

        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-4">
          {SAMPLE_CROP_IMAGES.map((sample) => {
            const isSelected = selectedSample?.id === sample.id;
            return (
              <button
                key={sample.id}
                type="button"
                onClick={() => handleSelectSample(sample)}
                className="text-left group"
              >
                <div className={`relative h-36 overflow-hidden ${isSelected ? 'ring-2 ring-[#1C2A1A] ring-offset-4 ring-offset-[#FBF7EE]' : ''}`}>
                  <img src={sample.imageUrl} alt={sample.name} className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-700" />
                  {isSelected && (
                    <span className="absolute top-2 right-2 w-6 h-6 rounded-full bg-[#1C2A1A] text-[#E8D5A3] flex items-center justify-center">
                      <Check className="w-3.5 h-3.5" />
                    </span>
                  )}
                </div>
                <span className="mt-2 block font-display text-[#161A12]">{sample.name}</span>
                <span className="text-[11px] uppercase tracking-widest text-[#6E7A4E]">{sample.cropType}</span>
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
                <h3 className="font-display text-3xl text-[#161A12]">Drop a crop image</h3>
                <p className="text-sm text-[#5A6150] font-light">JPEG, PNG or WEBP. Close, well-lit leaf photos read best.</p>
                <div className="flex flex-wrap justify-center gap-3">
                  <button type="button" onClick={() => fileInputRef.current?.click()} className="px-5 py-2 rounded-full bg-[#1C2A1A] text-[#F6F1E6] text-sm">
                    <span className="inline-flex items-center gap-2"><ImageIcon className="w-4 h-4" /> Browse</span>
                  </button>
                  <button type="button" onClick={() => fileInputRef.current?.click()} className="px-5 py-2 rounded-full border border-[#C9C0A8] text-sm text-[#1C2A1A]">
                    <span className="inline-flex items-center gap-2"><Camera className="w-4 h-4" /> Camera</span>
                  </button>
                </div>
              </div>
            ) : (
              <div className="relative w-full max-w-lg">
                <img src={previewUrl} alt="Crop preview" className="w-full h-72 object-cover" />
                <button type="button" onClick={handleClearImage} className="absolute top-3 right-3 p-2 bg-[#1C2A1A] text-white">
                  <X className="w-4 h-4" />
                </button>
                <p className="mt-3 text-sm text-[#5A6150]">
                  {selectedFile ? selectedFile.name : selectedSample?.name}
                </p>
              </div>
            )}
          </div>

          <div className="lg:col-span-5 space-y-6 bg-[#6E7A4E] text-[#F6F1E6] p-8">
            <p className="text-[11px] tracking-[0.28em] uppercase text-[#E8D5A3]">Field context</p>
            <h3 className="font-display text-3xl leading-tight">Tell us about the plot</h3>

            <label className="block space-y-2">
              <span className="text-xs uppercase tracking-widest flex items-center gap-2"><Sprout className="w-3.5 h-3.5" /> Crop</span>
              <select
                value={cropType}
                onChange={(e) => setCropType(e.target.value as CropType)}
                className="w-full bg-[#5F6A42] text-white border-b border-white/30 py-2 text-sm focus:outline-none"
              >
                <option value="tomato">Tomato</option>
                <option value="potato">Potato</option>
                <option value="corn">Corn / Maize</option>
                <option value="apple">Apple</option>
                <option value="cotton">Cotton</option>
                <option value="wheat">Wheat</option>
                <option value="rice">Rice</option>
                <option value="other">Other</option>
              </select>
            </label>

            <label className="block space-y-2">
              <span className="text-xs uppercase tracking-widest flex items-center gap-2"><Layers className="w-3.5 h-3.5" /> Growth stage</span>
              <select
                value={growthStage}
                onChange={(e) => setGrowthStage(e.target.value as GrowthStage)}
                className="w-full bg-[#5F6A42] text-white border-b border-white/30 py-2 text-sm focus:outline-none"
              >
                <option value="seedling">Seedling</option>
                <option value="vegetative">Vegetative</option>
                <option value="flowering">Flowering</option>
                <option value="fruiting">Fruiting</option>
                <option value="harvest">Harvest</option>
              </select>
            </label>

            <label className="block space-y-2">
              <span className="text-xs uppercase tracking-widest flex items-center gap-2"><MapPin className="w-3.5 h-3.5" /> Location</span>
              <input
                type="text"
                value={location}
                onChange={(e) => setLocation(e.target.value)}
                className="w-full bg-transparent border-b border-white/30 py-2 text-sm focus:outline-none placeholder:text-white/50"
              />
            </label>

            <button
              type="submit"
              disabled={!previewUrl || isAnalyzing}
              className="w-full mt-4 py-3 rounded-full bg-[#E8D5A3] text-[#1C2A1A] font-semibold disabled:opacity-40"
            >
              {isAnalyzing ? 'Reading the crop…' : 'Detect Disease'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
