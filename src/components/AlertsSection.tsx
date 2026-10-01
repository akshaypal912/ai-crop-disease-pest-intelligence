import React from 'react';
import { ShieldAlert, AlertTriangle, Info, Bell, ArrowRight } from 'lucide-react';
import type { Alert } from '../types/crop';

interface AlertsSectionProps {
  alerts: Alert[];
  onActionClick?: (alert: Alert) => void;
}

export const AlertsSection: React.FC<AlertsSectionProps> = ({ alerts = [], onActionClick }) => {
  const alertStyles = {
    critical: {
      bg: 'bg-[#FDF2F1]',
      border: 'border-[#B65B55]/50',
      text: 'text-[#B65B55]',
      badge: 'bg-[#B65B55] text-white',
      icon: ShieldAlert
    },
    warning: {
      bg: 'bg-[#F7EFCF]',
      border: 'border-[#D4AF37]/60',
      text: 'text-[#8C6D1F]',
      badge: 'bg-[#8C6D1F] text-white',
      icon: AlertTriangle
    },
    info: {
      bg: 'bg-[#E3ECE5]',
      border: 'border-[#0F3322]/30',
      text: 'text-[#0F3322]',
      badge: 'bg-[#0F3322] text-white',
      icon: Info
    }
  };

  return (
    <section id="alerts" className="py-16 px-4 sm:px-6 lg:px-8 bg-[#EBF1EC] bg-organic-texture border-t border-[#CFDAD2]">
      <div className="max-w-5xl mx-auto space-y-8">
        
        {/* Section Header */}
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div>
            <div className="inline-flex items-center gap-2 px-3.5 py-1 rounded-full bg-[#FDF2F1] text-[#B65B55] text-xs font-extrabold uppercase tracking-wider border border-[#B65B55]/30">
              <Bell className="w-3.5 h-3.5" />
              <span>FIELD OUTBREAK WARNINGS</span>
            </div>
            <h2 className="text-2xl sm:text-3xl font-extrabold text-[#0F3322] tracking-tight mt-2">
              Actionable Field Alerts ({alerts.length})
            </h2>
          </div>

          <span className="text-xs text-[#43544A] font-bold">
            Updated in real-time from microclimate telemetry
          </span>
        </div>

        {/* Alerts List */}
        {alerts.length === 0 ? (
          <div className="p-8 rounded-3xl bg-[#F6F3EC] border border-[#CFDAD2] text-center space-y-2">
            <Bell className="w-8 h-8 text-[#10B981] mx-auto opacity-60" />
            <h3 className="text-base font-extrabold text-[#0F3322]">No Active Field Alerts</h3>
            <p className="text-xs text-[#43544A] font-medium">
              All monitored crop plots are within safe microclimate and pathogen risk thresholds.
            </p>
          </div>
        ) : (
          <div className="space-y-4">
            {alerts.map((alt) => {
              const style = alertStyles[alt.severity] || alertStyles.info;
              const Icon = style.icon;

              return (
                <div
                  key={alt.id}
                  className={`p-5 rounded-3xl border ${style.bg} ${style.border} shadow-sm flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 transition-all hover:shadow-md`}
                >
                  <div className="flex items-start gap-4">
                    <div className={`w-10 h-10 rounded-2xl flex items-center justify-center shrink-0 ${style.badge}`}>
                      <Icon className="w-5 h-5 text-white" />
                    </div>

                    <div className="space-y-1 text-left">
                      <div className="flex flex-wrap items-center gap-2">
                        <span className={`px-2.5 py-0.5 rounded-full text-[10px] font-extrabold uppercase ${style.badge}`}>
                          {alt.severity}
                        </span>
                        {alt.cropType && (
                          <span className="px-2 py-0.5 rounded text-[10px] font-extrabold bg-white text-[#0F3322] border border-[#CFDAD2]">
                            {alt.cropType} Crop
                          </span>
                        )}
                        <span className="text-[11px] text-[#43544A] font-bold">
                          {alt.timestamp}
                        </span>
                      </div>

                      <h4 className="text-sm font-extrabold text-[#0F3322]">
                        {alt.reason}
                      </h4>
                      <p className="text-xs text-[#0D1611] font-semibold">
                        <strong className="text-[#0F3322]">Recommended Action:</strong> {alt.action}
                      </p>
                    </div>
                  </div>

                  {onActionClick && (
                    <button
                      onClick={() => onActionClick(alt)}
                      className="px-4 py-2 rounded-full bg-white border border-[#CFDAD2] text-[#0F3322] text-xs font-extrabold hover:bg-[#F6F3EC] transition-all shrink-0 flex items-center gap-1.5 shadow-sm"
                    >
                      <span>Take Action</span>
                      <ArrowRight className="w-3.5 h-3.5 text-[#10B981]" />
                    </button>
                  )}
                </div>
              );
            })}
          </div>
        )}

      </div>
    </section>
  );
};
