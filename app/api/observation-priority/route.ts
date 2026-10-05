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
      "observation_priority_profile.csv"
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
        depth_min_m: Number(row.depth_min_m),
        depth_max_m: Number(row.depth_max_m),
        uncertainty_score: Number(row.uncertainty_score),
        error_score: Number(row.error_score),
        sample_bonus: Number(row.sample_bonus),
        reliability_bonus: Number(row.reliability_bonus),
        priority_score: Number(row.priority_score),
        observation_priority: row.observation_priority,
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
            : "Unable to load observation priority data",
      },
      { status: 500 }
    );
  }
}