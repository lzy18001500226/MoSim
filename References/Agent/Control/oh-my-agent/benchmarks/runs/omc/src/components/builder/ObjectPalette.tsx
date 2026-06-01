"use client";

import { useState } from "react";
import { useWorldStore } from "@/store/worldStore";
import { OBJECT_DEFINITIONS, COLORS } from "@/lib/objects";
import type { WorldObject, ObjectType } from "@/types/world";

export function ObjectPalette() {
  const [activeCategory, setActiveCategory] = useState<string>("shapes");
  const addObject = useWorldStore((s) => s.addObject);
  const selectedObjectId = useWorldStore((s) => s.selectedObjectId);
  const currentWorld = useWorldStore((s) => s.currentWorld);
  const updateObject = useWorldStore((s) => s.updateObject);
  const removeObject = useWorldStore((s) => s.removeObject);

  const categories = [
    { id: "shapes", label: "Shapes", icon: "🔷" },
    { id: "nature", label: "Nature", icon: "🌿" },
    { id: "buildings", label: "Build", icon: "🏠" },
    { id: "characters", label: "Friends", icon: "🧑" },
  ];

  const filteredObjects = OBJECT_DEFINITIONS.filter(
    (o) => o.category === activeCategory
  );

  const handleAddObject = (type: ObjectType, defaultColor: string) => {
    const offset = () => (Math.random() - 0.5) * 4;
    const obj: WorldObject = {
      id: crypto.randomUUID(),
      type,
      position: [offset(), 0.5, offset()],
      rotation: [0, 0, 0],
      scale: [1, 1, 1],
      color: defaultColor,
      name: OBJECT_DEFINITIONS.find((o) => o.type === type)?.label || type,
    };
    addObject(obj);
  };

  const selectedObject = currentWorld?.objects.find(
    (o) => o.id === selectedObjectId
  );

  return (
    <div className="flex h-full flex-col bg-white/95 backdrop-blur">
      <div className="border-b border-indigo-100 p-3">
        <h3 className="mb-2 text-sm font-bold text-indigo-800">Add Objects</h3>
        <div className="flex gap-1">
          {categories.map((cat) => (
            <button
              key={cat.id}
              onClick={() => setActiveCategory(cat.id)}
              className={`flex-1 rounded-lg px-2 py-1.5 text-xs font-medium transition ${
                activeCategory === cat.id
                  ? "bg-indigo-100 text-indigo-700"
                  : "text-gray-500 hover:bg-gray-50"
              }`}
            >
              <span className="block text-lg">{cat.icon}</span>
              {cat.label}
            </button>
          ))}
        </div>
      </div>

      <div className="grid grid-cols-3 gap-2 p-3">
        {filteredObjects.map((obj) => (
          <button
            key={obj.type}
            onClick={() => handleAddObject(obj.type, obj.defaultColor)}
            className="flex flex-col items-center gap-1 rounded-xl bg-gray-50 p-3 hover:bg-indigo-50 hover:shadow transition active:scale-95"
          >
            <span className="text-2xl">{obj.icon}</span>
            <span className="text-xs font-medium text-gray-600">
              {obj.label}
            </span>
          </button>
        ))}
      </div>

      {selectedObject && (
        <div className="mt-auto border-t border-indigo-100 p-3">
          <h4 className="mb-2 text-sm font-bold text-indigo-800">
            Selected: {selectedObject.name}
          </h4>
          <div className="mb-3">
            <label className="mb-1 block text-xs text-gray-500">Color</label>
            <div className="grid grid-cols-8 gap-1">
              {COLORS.map((color) => (
                <button
                  key={color}
                  onClick={() => updateObject(selectedObject.id, { color })}
                  className={`h-6 w-6 rounded-full border-2 transition hover:scale-110 ${
                    selectedObject.color === color
                      ? "border-indigo-500 ring-2 ring-indigo-200"
                      : "border-gray-200"
                  }`}
                  style={{ backgroundColor: color }}
                />
              ))}
            </div>
          </div>
          <div className="mb-3">
            <label className="mb-1 block text-xs text-gray-500">Size</label>
            <input
              type="range"
              min="0.3"
              max="3"
              step="0.1"
              value={selectedObject.scale[0]}
              onChange={(e) => {
                const s = parseFloat(e.target.value);
                updateObject(selectedObject.id, { scale: [s, s, s] });
              }}
              className="w-full accent-indigo-500"
            />
          </div>
          <button
            onClick={() => removeObject(selectedObject.id)}
            className="w-full rounded-lg bg-red-50 py-2 text-sm font-medium text-red-600 hover:bg-red-100 transition"
          >
            Remove 🗑️
          </button>
        </div>
      )}
    </div>
  );
}
