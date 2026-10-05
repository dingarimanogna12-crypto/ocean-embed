import { NextResponse } from "next/server";
import { spawn } from "child_process";
import fs from "fs";
import path from "path";

function runPythonScript(
  scriptPath: string,
  input: Record<string, number>
): Promise<any> {
  return new Promise((resolve, reject) => {
    const payload = JSON.stringify(input);
    const tempDir = path.join(process.cwd(), ".next", "tmp");
    fs.mkdirSync(tempDir, { recursive: true });

    const outputPath = path.join(
      tempDir,
      `result-${Date.now()}-${Math.random().toString(16).slice(2)}.json`
    );

    const pythonProcess = spawn(
      "python",
      ["-u", scriptPath, payload, outputPath],
      {
        cwd: process.cwd(),
        env: process.env,
        windowsHide: true,
      }
    );

    let output = "";
    let errorOutput = "";

    pythonProcess.stdout.on("data", (data) => {
      output += data.toString();
    });

    pythonProcess.stderr.on("data", (data) => {
      errorOutput += data.toString();
    });

    pythonProcess.on("error", (error) => {
      reject(new Error(`Python could not start: ${error.message}`));
    });

    pythonProcess.on("close", (code) => {
      const fileContent = fs.existsSync(outputPath)
        ? fs.readFileSync(outputPath, "utf-8").trim()
        : "";

      if (fileContent) {
        try {
          resolve(JSON.parse(fileContent));
          return;
        } catch {
          // fall through
        }
      }

      if (code !== 0) {
        const combined = [output, errorOutput].filter(Boolean).join("\n");
        reject(new Error(combined.trim() || `Python process exited with code ${code}`));
        return;
      }

      const combinedOutput = [output, errorOutput].filter(Boolean).join("\n");
      const lines = combinedOutput
        .split(/\r?\n/)
        .map((line) => line.trim())
        .filter(Boolean);

      const jsonLine = [...lines].reverse().find((line) => {
        try {
          JSON.parse(line);
          return true;
        } catch {
          return false;
        }
      });

      if (!jsonLine) {
        reject(
          new Error(
            `Python returned invalid JSON.\n${combinedOutput || "No output received."}`
          )
        );
        return;
      }

      try {
        resolve(JSON.parse(jsonLine));
      } catch {
        reject(
          new Error(
            `Python returned invalid JSON.\n${jsonLine}`
          )
        );
      }
    });
  });
}

export async function POST(request: Request) {
  try {
    const rawBody = await request.text();

    if (!rawBody.trim()) {
      return NextResponse.json(
        {
          success: false,
          error: "Request body is empty.",
        },
        { status: 400 }
      );
    }

    let body: any;

    try {
      body = JSON.parse(rawBody);
    } catch {
      return NextResponse.json(
        {
          success: false,
          error: "Invalid JSON request body.",
          received: rawBody,
        },
        { status: 400 }
      );
    }

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
          {
            success: false,
            error: `Missing field: ${field}`,
          },
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

    for (const [key, value] of Object.entries(input)) {
      if (!Number.isFinite(value)) {
        return NextResponse.json(
          {
            success: false,
            error: `Invalid value for ${key}`,
          },
          { status: 400 }
        );
      }
    }

    const scriptPath = path.join(process.cwd(), "ml", "predict_step32_web.py");
    const prediction = await runPythonScript(scriptPath, input);

    if (!prediction.success) {
      return NextResponse.json(
        {
          success: false,
          error: prediction.error || "Prediction failed.",
        },
        { status: 500 }
      );
    }

    return NextResponse.json({
      ...prediction,
      success: true,
    });
  } catch (error) {
    console.error("API ERROR:", error);

    return NextResponse.json(
      {
        success: false,
        error:
          error instanceof Error
            ? error.message
            : "Unknown server error",
      },
      { status: 500 }
    );
  }
}