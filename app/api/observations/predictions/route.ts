import { NextResponse } from "next/server";
import { spawn } from "child_process";
import path from "path";

export async function POST(request: Request) {
  try {
    const body = await request.json();

    const requiredFields = [
      "latitude",
      "longitude",
      "sst",
      "sss",
      "ssh",
      "current_u",
      "current_v",
    ];

    for (const field of requiredFields) {
      if (body[field] === undefined || body[field] === null || body[field] === "") {
        return NextResponse.json(
          { success: false, error: `Missing field: ${field}` },
          { status: 400 }
        );
      }
    }

    const input = {
      latitude: Number(body.latitude),
      longitude: Number(body.longitude),
      sst: Number(body.sst),
      sss: Number(body.sss),
      ssh: Number(body.ssh),
      current_u: Number(body.current_u),
      current_v: Number(body.current_v),
    };

    const scriptPath = path.join(
      process.cwd(),
      "ml",
      "predict_step32_web.py"
    );

    const python = spawn("python", [scriptPath]);

    let stdout = "";
    let stderr = "";

    python.stdout.on("data", (data) => {
      stdout += data.toString();
    });

    python.stderr.on("data", (data) => {
      stderr += data.toString();
    });

    python.stdin.write(JSON.stringify(input));
    python.stdin.end();

    const result = await new Promise<{
      code: number | null;
      stdout: string;
      stderr: string;
    }>((resolve) => {
      python.on("close", (code) => {
        resolve({ code, stdout, stderr });
      });
    });

    if (result.code !== 0) {
      return NextResponse.json(
        {
          success: false,
          error: "Python prediction failed.",
          details: result.stderr,
        },
        { status: 500 }
      );
    }

    const firstBrace = result.stdout.indexOf("{");
    const lastBrace = result.stdout.lastIndexOf("}");

    if (firstBrace === -1 || lastBrace === -1) {
      return NextResponse.json(
        {
          success: false,
          error: "Invalid prediction output.",
          raw: result.stdout,
        },
        { status: 500 }
      );
    }

    const prediction = JSON.parse(
      result.stdout.substring(firstBrace, lastBrace + 1)
    );

    return NextResponse.json(prediction);
  } catch (error) {
    console.error("Prediction API error:", error);

    return NextResponse.json(
      {
        success: false,
        error: error instanceof Error ? error.message : "Unknown error",
      },
      { status: 500 }
    );
  }
}
