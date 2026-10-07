import React, { useState } from 'react';
import { Eye, Layers, ZoomIn, RefreshCw, Crosshair, Tag } from 'lucide-react';
import type { BoundingBox } from '../types/crop';

interface DetectionOverlayProps {
  imageUrl: string;
  boundingBoxes: BoundingBox[];
  pestBoxes?: BoundingBox[];
}

export const DetectionOverlay: React.FC<DetectionOverlayProps> = ({
  imageUrl,
  boundingBoxes = [],
  pestBoxes = []
}) => {
  const [showOverlay, setShowOverlay] = useState(true);
  const [selectedBoxId, setSelectedBoxId] = useState<string | null>(null);
  const [zoomLevel, setZoomLevel] = useState(1);

  const allBoxes = [...boundingBoxes, ...pestBoxes];

  const handleResetZoom = () => setZoomLevel(1);
  const handleZoomIn = () => setZoomLevel((prev) => Math.min(prev + 0.25, 2));

  return (
    <div className="space-y-4">
      
      {/* Top Action Bar: Toggle & Controls */}
      <div className="flex flex-wrap items-center justify-between gap-3 pb-3 border-b border-border">
        
        {/* Toggle Mode Segmented Control */}
        <div className="flex items-center gap-1">
          <button
            type="button"
            onClick={() => setShowOverlay(false)}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs transition-all ${
              !showOverlay ? 'bg-[#1C2A1A] text-[#F6F1E6]' : 'text-ink-muted border border-[#C9C0A8]'
            }`}
          >
            <Eye className="w-3.5 h-3.5" />
            <span>Original Image</span>
          </button>
          
          <button
            type="button"
            onClick={() => setShowOverlay(true)}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs transition-all ${
              showOverlay ? 'bg-[#1C2A1A] text-[#F6F1E6]' : 'text-ink-muted border border-[#C9C0A8]'
            }`}
          >
            <Layers className="w-3.5 h-3.5" />
            <span>AI Vision Overlay ({allBoxes.length})</span>
          </button>
        </div>

        {/* Image Controls */}
        <div className="flex items-center gap-2">
          <button
            type="button"
            onClick={handleZoomIn}
            className="p-2 text-ink-strong text-xs flex items-center gap-1"
            title="Zoom in image"
          >
            <ZoomIn className="w-3.5 h-3.5" />
            <span className="hidden sm:inline">Zoom ({Math.round(zoomLevel * 100)}%)</span>
          </button>
          {zoomLevel > 1 && (
            <button
              type="button"
              onClick={handleResetZoom}
              className="p-2 rounded-xl bg-white border border-border-soft text-[#B65B55] hover:bg-[#FDF2F1] text-xs font-bold"
              title="Reset Zoom"
            >
              <RefreshCw className="w-3.5 h-3.5" />
            </button>
          )}
        </div>
      </div>

      {/* Main Image Frame Container */}
      <div className="relative w-full overflow-hidden bg-[#1C2A1A] shadow-xl group">
        <div
          className="relative w-full h-[400px] sm:h-[480px] overflow-hidden flex items-center justify-center transition-transform duration-300"
          style={{ transform: `scale(${zoomLevel})` }}
        >
          <img
            src={imageUrl}
            alt="Analyzed Crop Leaf"
            className="w-full h-full object-cover select-none"
          />

          {/* Render Interactive Bounding Boxes Overlay */}
          {showOverlay && allBoxes.map((box) => {
            const isSelected = selectedBoxId === box.id;
            const isPest = box.type === 'pest';
            const isSymptom = box.type === 'symptom';

            const borderColor = isPest
              ? 'border-[#8A936C] bg-[#8A936C]/20'
              : isSymptom
              ? 'border-[#E8D5A3] bg-[#E8D5A3]/20'
              : 'border-[#B65B55] bg-[#B65B55]/20';

            const badgeBg = isPest
              ? 'bg-[#0B2518] text-[#10B981] border-[#10B981]/60'
              : isSymptom
              ? 'bg-[#0B2518] text-[#E5C378] border-[#E5C378]/60'
              : 'bg-[#0B2518] text-[#B65B55] border-[#B65B55]/60';

            return (
              <div
                key={box.id}
                onClick={() => setSelectedBoxId(isSelected ? null : box.id)}
                className={`absolute border-2 transition-all cursor-pointer rounded-lg ${borderColor} ${
                  isSelected ? 'ring-4 ring-white shadow-2xl scale-[1.02] z-20' : 'hover:scale-[1.01] z-10'
                }`}
                style={{
                  left: `${box.x}%`,
                  top: `${box.y}%`,
                  width: `${box.width}%`,
                  height: `${box.height}%`,
                }}
              >
                {/* Corner Crosshair Anchors */}
                <div className="absolute -top-1 -left-1 w-2 h-2 border-t-2 border-l-2 border-white" />
                <div className="absolute -top-1 -right-1 w-2 h-2 border-t-2 border-r-2 border-white" />
                <div className="absolute -bottom-1 -left-1 w-2 h-2 border-b-2 border-l-2 border-white" />
                <div className="absolute -bottom-1 -right-1 w-2 h-2 border-b-2 border-r-2 border-white" />

                {/* Box Label Tag */}
                <div className={`absolute -top-7 left-0 flex items-center gap-1.5 px-2 py-0.5 rounded text-[11px] font-extrabold shadow-md border ${badgeBg}`}>
                  <Crosshair className="w-3 h-3 text-[#E5C378]" />
                  <span>{box.label}</span>
                  <span className="opacity-80">({box.confidence}%)</span>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Bounding Box Selection Cards list */}
      {showOverlay && allBoxes.length > 0 && (
        <div className="space-y-2 text-left">
          <span className="text-[11px] uppercase tracking-[0.2em] text-olive flex items-center gap-1.5">
            <Tag className="w-3.5 h-3.5" />
            Detected AI Bounding Zones ({allBoxes.length})
          </span>

          <div className="flex flex-wrap gap-2">
            {allBoxes.map((box) => {
              const isSelected = selectedBoxId === box.id;
              return (
                <button
                  key={box.id}
                  type="button"
                  onClick={() => setSelectedBoxId(isSelected ? null : box.id)}
                  className={`px-3 py-1.5 rounded-full border text-xs flex items-center gap-2 transition-all ${
                    isSelected
                      ? 'bg-[#1C2A1A] text-[#F6F1E6] border-[#1C2A1A]'
                      : 'bg-transparent text-ink-strong border-[#C9C0A8]'
                  }`}
                >
                  <span className={`w-2 h-2 rounded-full ${box.type === 'pest' ? 'bg-[#6E7A4E]' : 'bg-[#B65B55]'}`} />
                  <span>{box.label}</span>
                  <span className="text-[10px] text-olive">{box.confidence}%</span>
                </button>
              );
            })}
          </div>
        </div>
      )}

    </div>
  );
};
