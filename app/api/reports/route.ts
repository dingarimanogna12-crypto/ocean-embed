import { NextResponse } from "next/server";
import fs from "fs";
import path from "path";

export async function GET() {
  try {
    const validationPath = path.join(
      process.cwd(),
      "ml",
      "data",
      "validation",
      "argo_validation_results.csv"
    );

    const uncertaintyPath = path.join(
      process.cwd(),
      "ml",
      "data",
      "validation",
      "final_uncertainty_summary.csv"
    );

    const priorityPath = path.join(
      process.cwd(),
      "ml",
      "data",
      "validation",
      "observation_priority_profile.csv"
    );

    const validationCsv = fs.readFileSync(validationPath, "utf-8");
    const uncertaintyCsv = fs.readFileSync(uncertaintyPath, "utf-8");
    const priorityCsv = fs.readFileSync(priorityPath, "utf-8");

    const validationLines = validationCsv.trim().split(/\r?\n/);
    const validationHeaders = validationLines[0].split(",");

    const validationData = validationLines.slice(1).map((line) => {
      const values = line.split(",");
      const row: Record<string, string> = {};

      validationHeaders.forEach((header, index) => {
        row[header] = values[index];
      });

      return row;
    });

    const errors = validationData.map((row) =>
      Number(row.absolute_error)
    );

    const signedErrors = validationData.map((row) =>
      Number(row.error)
    );

    const mae =
      errors.reduce((sum, value) => sum + Math.abs(value), 0) /
      errors.length;

    const rmse = Math.sqrt(
      signedErrors.reduce(
        (sum, value) => sum + value * value,
        0
      ) / signedErrors.length
    );

    const bias =
      signedErrors.reduce((sum, value) => sum + value, 0) /
      signedErrors.length;

    const priorityLines = priorityCsv.trim().split(/\r?\n/);
    const priorityHeaders = priorityLines[0].split(",");

    const priorityData = priorityLines.slice(1).map((line) => {
      const values = line.split(",");
      const row: Record<string, string> = {};

      priorityHeaders.forEach((header, index) => {
        row[header] = values[index];
      });

      return row;
    });

    const highestPriority = [...priorityData].sort(
      (a, b) =>
        Number(b.priority_score) -
        Number(a.priority_score)
    )[0];

    const mediumZones = priorityData.filter(
      (row) => row.observation_priority === "MEDIUM"
    ).length;

    return NextResponse.json({
      success: true,

      summary: {
        validation_samples: validationData.length,
        mae: Number(mae.toFixed(3)),
        rmse: Number(rmse.toFixed(3)),
        bias: Number(bias.toFixed(3)),
      },

      highest_priority: {
        depth_min_m: Number(highestPriority.depth_min_m),
        depth_max_m: Number(highestPriority.depth_max_m),
        priority_score: Number(
          Number(highestPriority.priority_score).toFixed(2)
        ),
        priority: highestPriority.observation_priority,
      },

      medium_priority_zones: mediumZones,

      message:
        "OceanEmbed combines prediction, independent ARGO validation, uncertainty estimation and observation-priority analysis into an integrated ocean intelligence workflow.",
    });
  } catch (error) {
    return NextResponse.json(
      {
        success: false,
        error:
          error instanceof Error
            ? error.message
            : "Unable to generate report",
      },
      { status: 500 }
    );
  }
}