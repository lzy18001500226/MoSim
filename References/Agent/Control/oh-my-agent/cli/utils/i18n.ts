export type Locale = "ko" | "en";

export function resolveLocale(): Locale {
  const lang = (process.env.LANG ?? "").toLowerCase();
  if (lang.startsWith("ko")) return "ko";
  return "en";
}

type Catalog = Record<string, { en: string; ko: string }>;

// Bilingual messages used by install / update flows.
// Keys are stable identifiers; values are localized strings.
// Interpolation: use {key} placeholders; pass a Record<string,string|number> as second arg to t().
export const MESSAGES: Catalog = {
  "install.sudoRefused": {
    en: "Refusing to install under sudo. Re-run as the target user.",
    ko: "sudo로는 설치할 수 없습니다. 대상 사용자로 다시 실행하세요.",
  },
  "install.cwdHomeWarn": {
    en: "Running in your HOME directory without --global. This will scatter files in ~/. Are you sure?",
    ko: "HOME 디렉토리에서 --global 없이 실행 중입니다. ~/ 에 파일이 흩어집니다. 진행할까요?",
  },
  "install.ciGlobalWarn": {
    en: "Running `oma install --global` in CI. This will modify the CI user's HOME.",
    ko: "CI에서 `oma install --global`을 실행합니다. CI 사용자의 HOME을 수정합니다.",
  },
  "install.wslHomeInfo": {
    en: "WSL detected. $HOME is distinct from Windows %USERPROFILE%; oma installs only to the WSL HOME. To install on the Windows side, run from PowerShell.",
    ko: "WSL이 감지됐습니다. $HOME은 Windows %USERPROFILE%과 다릅니다; oma는 WSL HOME에만 설치합니다. Windows 쪽에 설치하려면 PowerShell에서 실행하세요.",
  },
  "install.firstGlobalIntro": {
    en: "This is your first global install of oh-my-agent.",
    ko: "oh-my-agent를 글로벌로 처음 설치합니다.",
  },
  "install.lockHeld": {
    en: "Another oma install/update is running (pid={pid}). Try again in a moment.",
    ko: "다른 oma install/update가 실행 중입니다 (pid={pid}). 잠시 후 다시 시도하세요.",
  },
  "install.outroSuccess": {
    en: "Done! Next steps:\n  1. Open your project in your IDE\n  2. Type /orchestrate to spawn a multi-agent workflow\n  3. Run `oma doctor` if anything looks off",
    ko: "완료! 다음 단계:\n  1. 에디터에서 프로젝트 열기\n  2. /orchestrate 입력해 멀티 에이전트 워크플로우 실행\n  3. 이상이 있으면 `oma doctor` 실행",
  },
};

export function t(
  key: keyof typeof MESSAGES,
  vars: Record<string, string | number> = {},
): string {
  const locale = resolveLocale();
  const entry = MESSAGES[key];
  if (!entry) return String(key);
  let msg = entry[locale] ?? entry.en;
  for (const [k, v] of Object.entries(vars)) {
    msg = msg.replaceAll(`{${k}}`, String(v));
  }
  return msg;
}
