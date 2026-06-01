import { useCallback } from "react";

type DictationState = "idle" | "listening" | "processing";

type UseComposerDictationControlsArgs = {
  disabled: boolean;
  dictationEnabled: boolean;
  dictationState: DictationState;
  onToggleDictation?: () => void;
  onCancelDictation?: () => void;
  onOpenDictationSettings?: () => void;
};

export function useComposerDictationControls({
  disabled,
  dictationEnabled,
  dictationState,
  onToggleDictation,
  onCancelDictation,
  onOpenDictationSettings,
}: UseComposerDictationControlsArgs) {
  const isDictating = dictationState === "listening";
  const isDictationProcessing = dictationState === "processing";
  const isDictationBusy = dictationState !== "idle";
  const allowOpenDictationSettings = Boolean(
    onOpenDictationSettings && !dictationEnabled && !disabled && !isDictationProcessing,
  );
  const micDisabled =
    disabled ||
    (!allowOpenDictationSettings &&
      (isDictationProcessing ? !onCancelDictation : !dictationEnabled || !onToggleDictation));
  const micAriaLabel = allowOpenDictationSettings
    ? "Open dictation settings"
    : isDictationProcessing
      ? "Cancel transcription"
      : isDictating
        ? "Stop dictation"
        : "Start dictation";
  const micTitle = allowOpenDictationSettings
    ? "Dictation disabled. Open settings"
    : isDictationProcessing
      ? "Cancel transcription"
      : isDictating
        ? "Stop dictation"
        : "Start dictation";

  const handleMicClick = useCallback(() => {
    if (isDictationProcessing) {
      if (disabled || !onCancelDictation) {
        return;
      }
      onCancelDictation();
      return;
    }
    if (allowOpenDictationSettings) {
      onOpenDictationSettings?.();
      return;
    }
    if (!onToggleDictation || micDisabled) {
      return;
    }
    onToggleDictation();
  }, [
    allowOpenDictationSettings,
    disabled,
    isDictationProcessing,
    micDisabled,
    onCancelDictation,
    onOpenDictationSettings,
    onToggleDictation,
  ]);

  return {
    allowOpenDictationSettings,
    handleMicClick,
    isDictating,
    isDictationBusy,
    isDictationProcessing,
    micAriaLabel,
    micDisabled,
    micTitle,
  };
}
