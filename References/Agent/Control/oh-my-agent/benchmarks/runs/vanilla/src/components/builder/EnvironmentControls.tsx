'use client';

import { useWorldStore } from '@/store/useWorldStore';
import { ENVIRONMENT_THEMES, COLORS } from '@/lib/objects';
import { useState } from 'react';

export default function EnvironmentControls() {
  const { theme, setTheme, selectedObjectId, objects, updateObject, removeObject } = useWorldStore();
  const [showColors, setShowColors] = useState(false);

  const selectedObj = objects.find((o) => o.id === selectedObjectId);

  return (
    <div className="bg-white/90 backdrop-blur-sm border-t border-border p-3">
      {selectedObj ? (
        <div className="animate-slide-up">
          <div className="flex items-center justify-between mb-2">
            <h4 className="text-sm font-bold text-foreground/80">
              Selected: {selectedObj.name}
            </h4>
            <button
              onClick={() => removeObject(selectedObj.id)}
              className="text-xs px-3 py-1 bg-danger/10 text-danger rounded-full font-bold hover:bg-danger/20 transition-colors"
            >
              🗑️ Delete
            </button>
          </div>

          <div className="space-y-2">
            <div>
              <label className="text-xs font-bold text-muted block mb-1">Color</label>
              <div className="flex gap-1.5 flex-wrap">
                {COLORS.slice(0, 12).map((c) => (
                  <button
                    key={c}
                    onClick={() => updateObject(selectedObj.id, { color: c })}
                    className={`w-7 h-7 rounded-full border-2 transition-all hover:scale-110 ${
                      selectedObj.color === c ? 'border-foreground scale-110' : 'border-transparent'
                    }`}
                    style={{ backgroundColor: c }}
                  />
                ))}
                <button
                  onClick={() => setShowColors(!showColors)}
                  className="w-7 h-7 rounded-full border-2 border-dashed border-muted text-xs font-bold text-muted hover:border-primary hover:text-primary transition-colors"
                >
                  +
                </button>
              </div>
              {showColors && (
                <div className="flex gap-1.5 flex-wrap mt-1.5">
                  {COLORS.slice(12).map((c) => (
                    <button
                      key={c}
                      onClick={() => updateObject(selectedObj.id, { color: c })}
                      className={`w-7 h-7 rounded-full border-2 transition-all hover:scale-110 ${
                        selectedObj.color === c ? 'border-foreground scale-110' : 'border-transparent'
                      }`}
                      style={{ backgroundColor: c }}
                    />
                  ))}
                </div>
              )}
            </div>

            <div>
              <label className="text-xs font-bold text-muted block mb-1">Animation</label>
              <div className="flex gap-1.5">
                {(['none', 'bounce', 'spin', 'float', 'pulse'] as const).map((anim) => (
                  <button
                    key={anim}
                    onClick={() => updateObject(selectedObj.id, { animation: anim })}
                    className={`px-3 py-1 rounded-full text-xs font-bold transition-all ${
                      selectedObj.animation === anim
                        ? 'bg-primary text-white'
                        : 'bg-gray-100 text-foreground/60 hover:bg-gray-200'
                    }`}
                  >
                    {anim === 'none' ? '⏹️' : anim === 'bounce' ? '⬆️' : anim === 'spin' ? '🔄' : anim === 'float' ? '🎈' : '💫'}{' '}
                    {anim}
                  </button>
                ))}
              </div>
            </div>

            <div>
              <label className="text-xs font-bold text-muted block mb-1">Size</label>
              <div className="flex gap-1.5">
                {[0.5, 0.75, 1, 1.5, 2].map((s) => (
                  <button
                    key={s}
                    onClick={() => updateObject(selectedObj.id, { scale: [s, s, s] })}
                    className={`px-3 py-1 rounded-full text-xs font-bold transition-all ${
                      selectedObj.scale[0] === s
                        ? 'bg-secondary text-white'
                        : 'bg-gray-100 text-foreground/60 hover:bg-gray-200'
                    }`}
                  >
                    {s === 0.5 ? 'XS' : s === 0.75 ? 'S' : s === 1 ? 'M' : s === 1.5 ? 'L' : 'XL'}
                  </button>
                ))}
              </div>
            </div>
          </div>
        </div>
      ) : (
        <div>
          <h4 className="text-xs font-bold text-muted uppercase tracking-wide mb-2">
            Environment
          </h4>
          <div className="flex gap-2 flex-wrap">
            {ENVIRONMENT_THEMES.map((t) => (
              <button
                key={t.id}
                onClick={() => setTheme(t.id)}
                className={`px-3 py-1.5 rounded-full text-xs font-bold transition-all ${
                  theme === t.id
                    ? 'bg-primary text-white shadow-md scale-105'
                    : 'bg-gray-100 text-foreground/70 hover:bg-gray-200'
                }`}
              >
                {t.emoji} {t.label}
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
