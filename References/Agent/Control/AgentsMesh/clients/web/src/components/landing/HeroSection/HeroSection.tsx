"use client";

import { useState } from "react";
import { useTranslations } from "next-intl";
import { HeroContent } from "./HeroContent";
import { DemoVideoModal } from "./DemoVideoModal";
import { MeshBackground } from "./MeshBackground";

export function HeroSection() {
  const t = useTranslations();
  const [demoOpen, setDemoOpen] = useState(false);

  return (
    <section className="relative pt-24 pb-20 sm:pt-40 sm:pb-32 px-4 sm:px-6 lg:px-8 azure-mesh-bg overflow-hidden">
      <div className="absolute -top-20 -right-20 w-[300px] h-[300px] sm:w-[500px] sm:h-[500px] bg-[var(--azure-cyan)]/10 blur-[120px] rounded-full azure-orb pointer-events-none" />
      <div
        className="absolute bottom-10 -left-10 w-[260px] h-[260px] sm:w-[400px] sm:h-[400px] bg-[var(--azure-mint)]/10 blur-[100px] rounded-full azure-orb pointer-events-none"
        style={{ animationDelay: "1.5s" }}
      />
      <div
        className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[400px] h-[400px] sm:w-[700px] sm:h-[700px] bg-[var(--azure-cyan)]/[0.04] blur-[140px] rounded-full pointer-events-none"
      />

      <MeshBackground />

      <div className="relative z-10 max-w-6xl mx-auto">
        <HeroContent t={t} onWatchDemo={() => setDemoOpen(true)} />
      </div>

      <DemoVideoModal
        open={demoOpen}
        onClose={() => setDemoOpen(false)}
        iframeTitle={t("landing.demoVideo.iframeTitle")}
      />
    </section>
  );
}

export default HeroSection;
