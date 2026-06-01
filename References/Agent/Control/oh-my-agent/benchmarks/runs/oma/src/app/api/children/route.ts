import { NextResponse } from "next/server";
import { prisma } from "@/lib/prisma";
import { z } from "zod";

const createChildSchema = z.object({
  name: z.string().min(1).max(20),
  avatarId: z.string().min(1),
});

export async function POST(request: Request) {
  let body: unknown;

  try {
    body = await request.json();
  } catch {
    return NextResponse.json({ error: "Invalid JSON body" }, { status: 400 });
  }

  const parsed = createChildSchema.safeParse(body);

  if (!parsed.success) {
    return NextResponse.json({ error: "Invalid input" }, { status: 400 });
  }

  const child = await prisma.child.create({
    data: {
      name: parsed.data.name,
      avatarId: parsed.data.avatarId,
    },
  });

  return NextResponse.json(child, { status: 201 });
}
