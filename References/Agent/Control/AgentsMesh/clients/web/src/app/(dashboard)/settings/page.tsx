import { redirect } from "next/navigation";

// Personal settings root redirects to the General tab. Server-side
// redirect (HTTP 307) — no client-side spinner flash, no useEffect race.
export default function PersonalSettingsPage() {
  redirect("/settings/general");
}
