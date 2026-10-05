import { NextResponse } from "next/server";
import fs from "fs";
import path from "path";

export async function GET() {
  try {
    const filePath = path.join(
      process.cwd(),
      "ml",
      "data",
      "validation",
      "argo_validation_results.csv"
    );

    const csv = fs.readFileSync(filePath, "utf-8");

    const lines = csv.trim().split(/\r?\n/);

    const headers = lines[0].split(",");

    const data = lines.slice(1).map((line) => {
      const values = line.split(",");

      const row: Record<string, string> = {};

      headers.forEach((header, index) => {
        row[header] = values[index];
      });

      return {
        argo_depth: Number(row.argo_depth),
        argo_temperature: Number(row.argo_temperature),
        oceanembed_temperature: Number(
          row.oceanembed_temperature
        ),
        error: Number(row.error),
        absolute_error: Number(row.absolute_error),
      };
    });

    return NextResponse.json({
      success: true,
      data,
    });

  } catch (error) {
    return NextResponse.json(
      {
        success: false,
        error:
          error instanceof Error
            ? error.message
            : "Unable to load validation data",
      },
      { status: 500 }
    );
  }
}