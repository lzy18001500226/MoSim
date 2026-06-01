"use client";

import { useWorldStore } from "@/stores/world-store";
import { EnvironmentPicker } from "./environment-picker";
import { ColorPicker } from "./color-picker";

export function PropertiesPanel() {
  const selectedObjectId = useWorldStore((s) => s.selectedObjectId);
  const removeObject = useWorldStore((s) => s.removeObject);
  const resetWorld = useWorldStore((s) => s.resetWorld);
  const objectCount = useWorldStore((s) => s.objects.length);

  return (
    <div className="w-52 md:w-60 bg-[var(--color-surface)] border-l border-gray-200 p-4 flex flex-col gap-4 overflow-y-auto">
      <EnvironmentPicker />
      <hr className="border-gray-100" />
      <ColorPicker />

      {selectedObjectId && (
        <>
          <hr className="border-gray-100" />
          <button
            onClick={() => removeObject(selectedObjectId)}
            className="w-full py-2 text-sm font-medium text-red-600 bg-red-50 rounded-lg hover:bg-red-100 transition-colors"
          >
            Delete Object
          </button>
        </>
      )}

      <div className="mt-auto space-y-2">
        <p className="text-xs text-[var(--color-text-muted)]">{objectCount} objects placed</p>
        {objectCount > 0 && (
          <button
            onClick={resetWorld}
            className="w-full py-2 text-xs text-[var(--color-text-muted)] border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
          >
            Clear All
          </button>
        )}
      </div>
    </div>
  );
}
