import { Link } from "wouter";

export default function SettingsPage() {
  return (
    <div>
      SettingsPage
      <div style={{ marginTop: 16 }}>
        <Link href="/app/settings/model-provider">Model Provider Settings</Link>
      </div>
    </div>
  );
}