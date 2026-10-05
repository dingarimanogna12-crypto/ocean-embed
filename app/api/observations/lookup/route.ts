import { NextResponse } from "next/server";
import fs from "fs";
import path from "path";

export async function GET(request: Request) {
  try {
    const { searchParams } = new URL(request.url);

    const latitude = Number(searchParams.get("latitude"));
    const longitude = Number(searchParams.get("longitude"));

    if (!Number.isFinite(latitude) || !Number.isFinite(longitude)) {
      return NextResponse.json(
        {
          success: false,
          error: "Valid latitude and longitude are required.",
        },
        { status: 400 }
      );
    }

    const csvPath = path.join(
      process.cwd(),
      "ml",
      "data",
      "real",
      "multidate_real_training.csv"
    );

    if (!fs.existsSync(csvPath)) {
      return NextResponse.json(
        {
          success: false,
          error: "Observation dataset not found.",
        },
        { status: 500 }
      );
    }

    const csv = fs.readFileSync(csvPath, "utf-8");

    const lines = csv
      .split(/\r?\n/)
      .filter((line) => line.trim());

    const headers = lines[0].split(",");

    const latitudeIndex = headers.indexOf("latitude");
    const longitudeIndex = headers.indexOf("longitude");
    const sstIndex = headers.indexOf("sst");
    const sssIndex = headers.indexOf("sss");
    const sshIndex = headers.indexOf("ssh");
    const currentUIndex = headers.indexOf("current_u");
    const currentVIndex = headers.indexOf("current_v");

    let bestRow: string[] | null = null;
    let bestDistance = Infinity;

    for (let i = 1; i < lines.length; i++) {
      const row = lines[i].split(",");

      const rowLat = Number(row[latitudeIndex]);
      const rowLon = Number(row[longitudeIndex]);

      if (!Number.isFinite(rowLat) || !Number.isFinite(rowLon)) {
        continue;
      }

      const distance =
        Math.pow(rowLat - latitude, 2) +
        Math.pow(rowLon - longitude, 2);

      if (distance < bestDistance) {
        bestDistance = distance;
        bestRow = row;
      }
    }

    if (!bestRow) {
      return NextResponse.json(
        {
          success: false,
          error: "No nearby observation found.",
        },
        { status: 404 }
      );
    }

    return NextResponse.json({
      success: true,
      requested_location: {
        latitude,
        longitude,
      },
      observation: {
        latitude: Number(bestRow[latitudeIndex]),
        longitude: Number(bestRow[longitudeIndex]),
        sst: Number(bestRow[sstIndex]),
        sss: Number(bestRow[sssIndex]),
        ssh: Number(bestRow[sshIndex]),
        current_u: Number(bestRow[currentUIndex]),
        current_v: Number(bestRow[currentVIndex]),
      },
    });
  } catch (error) {
    console.error("Observation lookup error:", error);

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