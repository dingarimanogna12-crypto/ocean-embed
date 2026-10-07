import { NextResponse } from "next/server";
import { createClient } from "@supabase/supabase-js";

type Observation = {
  id: number;
  date: string;
  latitude: number;
  longitude: number;
  sst: number | null;
  sss: number | null;
  ssh: number | null;
  current_u: number | null;
  current_v: number | null;
};

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

    const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL;
    const supabaseKey = process.env.NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY;

    if (!supabaseUrl || !supabaseKey) {
      return NextResponse.json(
        {
          success: false,
          error: "Supabase environment variables are missing.",
        },
        { status: 500 }
      );
    }

    const supabase = createClient(supabaseUrl, supabaseKey);
    const { data, error } = await supabase
      .from("observations")
      .select(
        "id,date,latitude,longitude,sst,sss,ssh,current_u,current_v"
      );

    if (error) {
      console.error("Supabase observation lookup error:", error);
      return NextResponse.json(
        {
          success: false,
          error: "Could not read observations from Supabase.",
          details: error.message,
        },
        { status: 500 }
      );
    }

    if (!data?.length) {
      return NextResponse.json(
        {
          success: false,
          error: "The Supabase observations table is empty.",
        },
        { status: 404 }
      );
    }

    const observations = data as Observation[];
    let nearestObservation: Observation | undefined;
    let smallestDistance = Number.POSITIVE_INFINITY;

    for (const observation of observations) {
      const rowLatitude = Number(observation.latitude);
      const rowLongitude = Number(observation.longitude);
      if (!Number.isFinite(rowLatitude) || !Number.isFinite(rowLongitude)) {
        continue;
      }

      const distance =
        (rowLatitude - latitude) ** 2 + (rowLongitude - longitude) ** 2;

      if (distance < smallestDistance) {
        smallestDistance = distance;
        nearestObservation = observation;
      }
    }

    if (!nearestObservation) {
      return NextResponse.json(
        {
          success: false,
          error: "No Supabase observations have valid coordinates.",
        },
        { status: 404 }
      );
    }

    const requiredValues = {
      sst: nearestObservation.sst,
      sss: nearestObservation.sss,
      ssh: nearestObservation.ssh,
      current_u: nearestObservation.current_u,
      current_v: nearestObservation.current_v,
    };
    const missingField = Object.entries(requiredValues).find(
      ([, value]) => value === null || !Number.isFinite(Number(value))
    )?.[0];

    if (missingField) {
      return NextResponse.json(
        {
          success: false,
          error: `The nearest Supabase observation is missing a valid ${missingField} value.`,
        },
        { status: 422 }
      );
    }

    return NextResponse.json({
      success: true,
      requested_location: { latitude, longitude },
      observation: {
        latitude: Number(nearestObservation.latitude),
        longitude: Number(nearestObservation.longitude),
        sst: Number(nearestObservation.sst),
        sss: Number(nearestObservation.sss),
        ssh: Number(nearestObservation.ssh),
        current_u: Number(nearestObservation.current_u),
        current_v: Number(nearestObservation.current_v),
      },
      distance_degrees: Number(Math.sqrt(smallestDistance).toFixed(4)),
      observation_count: observations.length,
    });
  } catch (error) {
    console.error("Observation lookup error:", error);
    return NextResponse.json(
      {
        success: false,
        error:
          error instanceof Error
            ? error.message
            : "Failed to look up a Supabase observation.",
      },
      { status: 500 }
    );
  }
}
