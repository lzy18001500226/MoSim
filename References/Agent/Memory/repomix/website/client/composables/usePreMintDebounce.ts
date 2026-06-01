import { onBeforeUnmount, type Ref, watch } from 'vue';

// Debounced trigger for the Turnstile pre-mint. Watches a (valid + touched)
// gate and fires `onTrigger` after `delayMs` of quiet — short enough that
// the token is usually ready by the time the user reaches for the Pack
// button, long enough that rapid typing or quick mode-switches don't
// trigger multiple mints.
//
// `loading` is intentionally NOT a watch source — only a guard inside the
// callback. Including it in the deps would re-fire the watch on
// `loading: true → false`, scheduling a fresh pre-mint immediately after
// every pack completion even though the user hasn't done anything new,
// re-introducing dashboard counter inflation through a different path.
// The `clear()` callers (e.g. `submitRequest`'s start) are what stop a
// pending debounce from firing mid-submit.
export interface PreMintDebounceOptions {
  // Source refs the watch should react to. Pre-mint fires when both are
  // truthy AND `loading.value` is false at the time the timer fires.
  isSubmitValid: Readonly<Ref<boolean>>;
  userTouched: Readonly<Ref<boolean>>;
  loading: Readonly<Ref<boolean>>;
  // Called when the debounce window elapses. Should kick off the actual
  // background mint — errors should be swallowed by the caller since
  // failures surface on the explicit submit path.
  onTrigger: () => void;
  delayMs: number;
}

export function usePreMintDebounce(opts: PreMintDebounceOptions) {
  const { isSubmitValid, userTouched, loading, onTrigger, delayMs } = opts;
  let timer: ReturnType<typeof setTimeout> | undefined;

  function clear() {
    if (timer !== undefined) {
      clearTimeout(timer);
      timer = undefined;
    }
  }

  watch(
    [isSubmitValid, userTouched],
    ([valid, touched]) => {
      clear();
      if (!valid || !touched || loading.value) return;
      timer = setTimeout(() => {
        timer = undefined;
        onTrigger();
      }, delayMs);
    },
    { flush: 'post' },
  );

  onBeforeUnmount(() => clear());

  return { clear };
}
