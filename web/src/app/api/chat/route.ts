import { NextResponse } from "next/server";

/** Legacy server route — generation now runs in-browser via transformers.js. */
export async function POST() {
  return NextResponse.json(
    {
      error:
        "Chat generation runs in the browser now. Use the AlignLab UI (no server model host required).",
    },
    { status: 410 }
  );
}
