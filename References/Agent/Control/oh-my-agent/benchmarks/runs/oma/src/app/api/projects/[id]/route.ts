import { NextResponse } from "next/server";
import { prisma } from "@/lib/prisma";
import { z } from "zod";

interface RouteParams {
  params: Promise<{ id: string }>;
}

export async function GET(_request: Request, { params }: RouteParams) {
  const { id } = await params;

  const project = await prisma.project.findUnique({ where: { id } });

  if (!project) {
    return NextResponse.json({ error: "Not found" }, { status: 404 });
  }

  return NextResponse.json({
    ...project,
    worldData: JSON.parse(project.worldData),
  });
}

const updateSchema = z.object({
  title: z.string().min(1).max(100).optional(),
  worldData: z
    .object({
      objects: z.array(z.any()),
      environment: z.object({
        theme: z.string(),
        skyColor: z.string(),
        groundColor: z.string(),
      }),
    })
    .optional(),
});

export async function PUT(request: Request, { params }: RouteParams) {
  const { id } = await params;
  const body = await request.json();
  const parsed = updateSchema.safeParse(body);

  if (!parsed.success) {
    return NextResponse.json({ error: "Invalid input" }, { status: 400 });
  }

  const data: Record<string, unknown> = {};
  if (parsed.data.title) data.title = parsed.data.title;
  if (parsed.data.worldData) data.worldData = JSON.stringify(parsed.data.worldData);

  const project = await prisma.project.update({
    where: { id },
    data,
  });

  return NextResponse.json(project);
}

export async function DELETE(_request: Request, { params }: RouteParams) {
  const { id } = await params;

  await prisma.project.delete({ where: { id } });

  return NextResponse.json({ success: true });
}
