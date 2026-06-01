'use client';

import { useState } from 'react';
import { OBJECT_CATALOG, CATEGORIES, ObjectDefinition } from '@/lib/objects';
import { useWorldStore } from '@/store/useWorldStore';

export default function ObjectPalette() {
  const [activeCategory, setActiveCategory] = useState<string>('shapes');
  const addObject = useWorldStore((s) => s.addObject);

  const filtered = OBJECT_CATALOG.filter((o) => o.category === activeCategory);

  const handleAdd = (def: ObjectDefinition) => {
    const spread = 8;
    const x = (Math.random() - 0.5) * spread;
    const z = (Math.random() - 0.5) * spread;
    addObject({
      type: def.type,
      name: def.label,
      position: [x, 0.5, z],
      rotation: [0, 0, 0],
      scale: [1, 1, 1],
      color: def.defaultColor,
      animation: 'none',
    });
  };

  return (
    <div className="flex flex-col h-full bg-white/90 backdrop-blur-sm">
      <div className="p-3 border-b border-border">
        <h3 className="text-sm font-bold text-foreground/70 uppercase tracking-wide mb-2">
          Objects
        </h3>
        <div className="flex gap-1 flex-wrap">
          {CATEGORIES.map((cat) => (
            <button
              key={cat.id}
              onClick={() => setActiveCategory(cat.id)}
              className={`px-3 py-1.5 rounded-full text-xs font-bold transition-all ${
                activeCategory === cat.id
                  ? 'bg-primary text-white shadow-md scale-105'
                  : 'bg-gray-100 text-foreground/70 hover:bg-gray-200'
              }`}
            >
              {cat.emoji} {cat.label}
            </button>
          ))}
        </div>
      </div>
      <div className="flex-1 overflow-y-auto p-3">
        <div className="grid grid-cols-2 gap-2">
          {filtered.map((def) => (
            <button
              key={def.type}
              onClick={() => handleAdd(def)}
              className="flex flex-col items-center justify-center p-3 rounded-2xl border-2 border-transparent bg-gray-50 hover:border-primary hover:bg-primary/5 hover:shadow-md transition-all active:scale-95 cursor-pointer"
            >
              <span className="text-3xl mb-1">{def.emoji}</span>
              <span className="text-xs font-bold text-foreground/80">{def.label}</span>
            </button>
          ))}
        </div>
        {filtered.length === 0 && (
          <p className="text-center text-muted text-sm mt-8">Coming soon!</p>
        )}
      </div>
    </div>
  );
}
