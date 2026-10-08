import { NextResponse } from "next/server";
import { spawn } from "child_process";
import path from "path";

export const maxDuration = 60;

const DEFAULT_PREDICTION_API_URL = "https://ocean-embed-8int.onrender.com";

async function runLocalPrediction(
  input: Record<string, number>
): Promise<unknown> {
  const scriptPath = path.join(
    process.cwd(),
    "ml",
    "predict_step32_web.py"
  );
  const python = spawn(
    process.platform === "win32" ? "python.exe" : "python3",
    ["-u", scriptPath],
    {
      cwd: process.cwd(),
      env: process.env,
      windowsHide: true,
    }
  );

  let stdout = "";
  let stderr = "";

  python.stdout.on("data", (data) => {
    stdout += data.toString();
  });
  python.stderr.on("data", (data) => {
    stderr += data.toString();
  });

  const exitCode = await new Promise<number>((resolve, reject) => {
    python.once("error", (error) => {
      reject(new Error(`Could not start local Python model: ${error.message}`));
    });
    python.once("close", (code) => resolve(code ?? 1));
    python.stdin.end(JSON.stringify(input));
  });

  if (exitCode !== 0) {
    throw new Error(stderr.trim() || `Local Python model exited with code ${exitCode}.`);
  }

  try {
    return JSON.parse(stdout);
  } catch {
    throw new Error("The local Python model returned invalid JSON.");
  }
}

export async function POST(request: Request) {
  try {
    let body: unknown;

    try {
      body = await request.json();
    } catch {
      return NextResponse.json(
        { success: false, error: "Request body must be valid JSON." },
        { status: 400 }
      );
    }

    if (!body || typeof body !== "object" || Array.isArray(body)) {
      return NextResponse.json(
        { success: false, error: "Request body must be a JSON object." },
        { status: 400 }
      );
    }

    const values = body as Record<string, unknown>;

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
      const value = values[field];
      if (value === undefined || value === null || value === "") {
        return NextResponse.json(
          {
            success: false,
            error: `Missing field: ${field}`,
          },
          { status: 400 }
        );
      }
    }

    const input = Object.fromEntries(
      requiredFields.map((field) => [field, Number(values[field])])
    ) as Record<(typeof requiredFields)[number], number>;

    const invalidField = Object.entries(input).find(
      ([, value]) => !Number.isFinite(value)
    )?.[0];

    if (invalidField) {
      return NextResponse.json(
        {
          success: false,
          error: `Invalid numeric value for ${invalidField}.`,
        },
        { status: 400 }
      );
    }

    const configuredApiUrl = process.env.OCEANEMBED_API_URL?.trim();

    if (!configuredApiUrl && process.env.NODE_ENV === "development") {
      try {
        return NextResponse.json(await runLocalPrediction(input));
      } catch (error) {
        console.error("Local OceanEmbed prediction failed:", error);
        return NextResponse.json(
          {
            success: false,
            error:
              error instanceof Error
                ? error.message
                : "Local prediction failed.",
          },
          { status: 500 }
        );
      }
    }

    const apiUrl = (
      configuredApiUrl || DEFAULT_PREDICTION_API_URL
    ).replace(/\/+$/, "");

    let response: Response;

    try {
      response = await fetch(`${apiUrl}/predict`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(input),
        cache: "no-store",
        signal: AbortSignal.timeout(55_000),
      });
    } catch (error) {
      console.error("OceanEmbed backend request failed:", error);
      return NextResponse.json(
        {
          success: false,
          error:
            error instanceof Error && error.name === "TimeoutError"
              ? "Prediction backend timed out. Try again in a moment."
              : "Could not connect to the prediction backend.",
        },
        { status: 502 }
      );
    }

    let prediction: unknown;

    try {
      prediction = await response.json();
    } catch {
      console.error(
        "OceanEmbed backend returned non-JSON response:",
        response.status
      );
      return NextResponse.json(
        {
          success: false,
          error: "Prediction backend returned an invalid response.",
        },
        { status: 502 }
      );
    }

    if (!response.ok) {
      const backendError =
        prediction &&
        typeof prediction === "object" &&
        "detail" in prediction &&
        typeof prediction.detail === "string"
          ? prediction.detail
          : "Prediction backend rejected the request.";

      return NextResponse.json(
        { success: false, error: backendError },
        { status: response.status }
      );
    }

    return NextResponse.json(prediction);
  } catch (error) {
    console.error("OceanEmbed production prediction error:", error);

    return NextResponse.json(
      {
        success: false,
        error:
          error instanceof Error
            ? error.message
            : "Unable to connect to OceanEmbed backend.",
      },
      { status: 500 }
    );
  }
}