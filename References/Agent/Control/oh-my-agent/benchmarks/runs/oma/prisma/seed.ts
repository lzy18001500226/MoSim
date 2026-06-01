import { PrismaClient } from "@prisma/client";

const prisma = new PrismaClient();

const sampleWorlds = [
  {
    title: "Enchanted Forest",
    worldData: JSON.stringify({
      objects: [
        { id: "s1", shape: "tree", label: "Tree", position: { x: -2, y: 0.75, z: 0 }, rotation: { x: 0, y: 0, z: 0 }, scale: { x: 1, y: 1.5, z: 1 }, color: "#27AE60" },
        { id: "s2", shape: "tree", label: "Tree", position: { x: 2, y: 0.75, z: -1 }, rotation: { x: 0, y: 0.5, z: 0 }, scale: { x: 1.2, y: 1.8, z: 1.2 }, color: "#229954" },
        { id: "s3", shape: "sphere", label: "Ball", position: { x: 0, y: 0.5, z: 2 }, rotation: { x: 0, y: 0, z: 0 }, scale: { x: 0.8, y: 0.8, z: 0.8 }, color: "#F39C12" },
        { id: "s4", shape: "torus", label: "Ring", position: { x: 0, y: 2, z: 0 }, rotation: { x: 0.5, y: 0, z: 0 }, scale: { x: 1.5, y: 1.5, z: 1.5 }, color: "#FFEAA7" },
        { id: "s5", shape: "box", label: "Box", position: { x: -3, y: 0.5, z: 3 }, rotation: { x: 0, y: 0.3, z: 0 }, scale: { x: 0.6, y: 0.6, z: 0.6 }, color: "#8E44AD" },
      ],
      environment: { theme: "forest", skyColor: "#355E3B", groundColor: "#228B22" },
    }),
    isSample: true,
  },
  {
    title: "Space Station",
    worldData: JSON.stringify({
      objects: [
        { id: "s6", shape: "cylinder", label: "Tube", position: { x: 0, y: 1, z: 0 }, rotation: { x: 0, y: 0, z: 0 }, scale: { x: 2, y: 2, z: 2 }, color: "#BDC3C7" },
        { id: "s7", shape: "sphere", label: "Ball", position: { x: 3, y: 1.5, z: 0 }, rotation: { x: 0, y: 0, z: 0 }, scale: { x: 1.2, y: 1.2, z: 1.2 }, color: "#3498DB" },
        { id: "s8", shape: "star", label: "Star", position: { x: -2, y: 2, z: -2 }, rotation: { x: 0.3, y: 0.5, z: 0 }, scale: { x: 0.8, y: 0.8, z: 0.8 }, color: "#F1C40F" },
        { id: "s9", shape: "cone", label: "Cone", position: { x: 1, y: 0.5, z: 3 }, rotation: { x: 0, y: 0, z: 0 }, scale: { x: 1, y: 2, z: 1 }, color: "#E74C3C" },
      ],
      environment: { theme: "space", skyColor: "#0a0a2a", groundColor: "#2d2d5e" },
    }),
    isSample: true,
  },
  {
    title: "Ocean Discovery",
    worldData: JSON.stringify({
      objects: [
        { id: "s10", shape: "sphere", label: "Ball", position: { x: 0, y: 1, z: 0 }, rotation: { x: 0, y: 0, z: 0 }, scale: { x: 1.5, y: 1.5, z: 1.5 }, color: "#1ABC9C" },
        { id: "s11", shape: "cylinder", label: "Tube", position: { x: -3, y: 0.5, z: 1 }, rotation: { x: 0, y: 0, z: 0 }, scale: { x: 0.3, y: 2, z: 0.3 }, color: "#16A085" },
        { id: "s12", shape: "torus", label: "Ring", position: { x: 2, y: 0.8, z: -1 }, rotation: { x: 1.5, y: 0, z: 0 }, scale: { x: 1, y: 1, z: 1 }, color: "#2ECC71" },
        { id: "s13", shape: "box", label: "Box", position: { x: -1, y: 0.3, z: 3 }, rotation: { x: 0, y: 0.7, z: 0 }, scale: { x: 2, y: 0.3, z: 1.5 }, color: "#F4D03F" },
      ],
      environment: { theme: "ocean", skyColor: "#1a5276", groundColor: "#2E86C1" },
    }),
    isSample: true,
  },
];

async function main() {
  const sampleChild = await prisma.child.create({
    data: { name: "Sample Creator", avatarId: "star" },
  });

  for (const world of sampleWorlds) {
    await prisma.project.create({
      data: { ...world, childId: sampleChild.id },
    });
  }

  console.log("Seed complete: created sample child and 3 sample worlds");
}

main()
  .then(() => prisma.$disconnect())
  .catch((e) => {
    console.error(e);
    prisma.$disconnect();
    process.exit(1);
  });
