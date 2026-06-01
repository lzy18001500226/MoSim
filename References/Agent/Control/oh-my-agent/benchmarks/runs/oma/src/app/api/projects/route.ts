import { NextResponse } from "next/server";
import { prisma } from "@/lib/prisma";
import { z } from "zod";

const createProjectSchema = z.object({
  title: z.string().min(1).max(100),
  worldData: z.object({
    objects: z.array(z.any()),
    environment: z.object({
      theme: z.string(),
      skyColor: z.string(),
      groundColor: z.string(),
    }),
  }),
  childId: z.string().min(1),
});

export async function GET(request: Request) {
  const { searchParams } = new URL(request.url);
  const childId = searchParams.get("childId");

  const where = childId ? { childId } : { isSample: true };

  const projects = await prisma.project.findMany({
    where,
    orderBy: { createdAt: "desc" },
    select: {
      id: true,
      title: true,
      thumbnail: true,
      createdAt: true,
      isSample: true,
    },
  });

  return NextResponse.json(projects);
}

export async function POST(request: Request) {
  const body = await request.json();
  const parsed = createProjectSchema.safeParse(body);

  if (!parsed.success) {
    return NextResponse.json({ error: "Invalid input" }, { status: 400 });
  }

  const project = await prisma.project.create({
    data: {
      title: parsed.data.title,
      worldData: JSON.stringify(parsed.data.worldData),
      childId: parsed.data.childId,
    },
  });

  return NextResponse.json(project, { status: 201 });
}
