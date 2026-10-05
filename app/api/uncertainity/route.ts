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
      "final_uncertainty_profile.csv"
    );

    if (!fs.existsSync(filePath)) {
      return NextResponse.json(
        {
          success: false,
          error: "Uncertainty CSV file not found.",
        },
        { status: 404 }
      );
    }

    const csv = fs.readFileSync(filePath, "utf8");

    const lines = csv
      .trim()
      .split(/\r?\n/)
      .filter((line) => line.trim() !== "");

    if (lines.length < 2) {
      return NextResponse.json({
        success: true,
        data: [],
      });
    }

    const headers = lines[0]
      .split(",")
      .map((header) => header.trim());

    const data = lines.slice(1).map((line) => {
      const values = line.split(",");

      const row: Record<string, string | number> = {};

      headers.forEach((header, index) => {
        const value = values[index]?.trim() ?? "";

        const numericValue = Number(value);

        row[header] =
          value !== "" && !Number.isNaN(numericValue)
            ? numericValue
            : value;
      });

      return row;
    });

    return NextResponse.json({
      success: true,
      data,
    });
  } catch (error) {
    console.error("Uncertainty API error:", error);

    return NextResponse.json(
      {
        success: false,
        error:
          error instanceof Error
            ? error.message
            : "Unknown error",
      },
      { status: 500 }
    );
  }
}