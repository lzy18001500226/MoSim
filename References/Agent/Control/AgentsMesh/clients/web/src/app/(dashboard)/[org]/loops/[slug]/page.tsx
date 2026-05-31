"use client";

import { useParams } from "next/navigation";
import { LoopDetailPane } from "@/components/loops/LoopDetailPane";

export default function LoopDetailPage() {
  const params = useParams();
  const slug = params.slug as string;
  const orgSlug = params.org as string;

  return <LoopDetailPane slug={slug} orgSlug={orgSlug} />;
}
