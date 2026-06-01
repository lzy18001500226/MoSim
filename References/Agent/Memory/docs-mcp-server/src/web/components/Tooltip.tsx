import type { PropsWithChildren } from "@kitajs/html";

/**
 * Props for the Tooltip component.
 */
interface TooltipProps extends PropsWithChildren {
  text: string | Promise<string> | Element;
  position?: "top" | "right" | "bottom" | "left";
}

/**
 * Reusable Tooltip component using Alpine.js for state management.
 * Displays a help icon that shows a tooltip on hover/focus.
 *
 * @param props - Component props including text and optional position.
 */
const Tooltip = ({ text, position = "top" }: TooltipProps) => {
  // Map position to Tailwind classes
  const positionClasses = {
    top: "bottom-full left-1/2 transform -translate-x-1/2 -translate-y-1 mb-1",
    right: "left-full top-1/2 transform -translate-y-1/2 translate-x-1 ml-1",
    bottom: "top-full left-1/2 transform -translate-x-1/2 translate-y-1 mt-1",
    left: "right-full top-1/2 transform -translate-y-1/2 -translate-x-1 mr-1",
  };

  return (
    <div
      class="relative ml-1.5 flex items-center"
      x-data="{ isVisible: false }"
    >
      <button
        type="button"
        class="text-gray-400 hover:text-gray-500 dark:text-gray-500 dark:hover:text-gray-400 focus:outline-none flex items-center"
        aria-label="Help"
        x-on:mouseenter="isVisible = true"
        x-on:mouseleave="isVisible = false"
        x-on:focus="isVisible = true"
        x-on:blur="isVisible = false"
        tabindex="0"
      >
        <svg
          xmlns="http://www.w3.org/2000/svg"
          fill="none"
          viewBox="0 0 24 24"
          stroke-width="1.5"
          stroke="currentColor"
          class="w-4 h-4"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            d="M9.879 7.519c1.171-1.025 3.071-1.025 4.242 0 1.172 1.025 1.172 2.687 0 3.712-.203.179-.43.326-.67.442-.745.361-1.45.999-1.45 1.827v.75M21 12a9 9 0 11-18 0 9 9 0 0118 0zm-9 5.25h.008v.008H12v-.008z"
          />
        </svg>
      </button>
      <div
        x-show="isVisible"
        x-cloak
        class={`absolute z-10 w-64 p-2 text-sm text-gray-500 bg-white border border-gray-200 rounded-lg shadow-sm dark:bg-gray-800 dark:border-gray-600 dark:text-gray-400 ${positionClasses[position]}`}
      >
        {text as "safe"}
      </div>
    </div>
  );
};

export default Tooltip;
