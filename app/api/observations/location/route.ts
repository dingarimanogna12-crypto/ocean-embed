import { NextResponse } from "next/server";
import { createClient } from "@supabase/supabase-js";

export async function GET(request: Request) {
  try {
    const { searchParams } = new URL(request.url);

    const latitude = Number(searchParams.get("lat"));
    const longitude = Number(searchParams.get("lon"));

    // Validate coordinates
    if (
      !Number.isFinite(latitude) ||
      !Number.isFinite(longitude)
    ) {
      return NextResponse.json(
        {
          success: false,
          error: "Latitude and longitude are required.",
        },
        { status: 400 }
      );
    }

    // OceanEmbed study region
    if (
      latitude < 5 ||
      latitude > 30 ||
      longitude < 45 ||
      longitude > 105
    ) {
      return NextResponse.json(
        {
          success: false,
          error:
            "Location is outside the OceanEmbed study region.",
        },
        { status: 400 }
      );
    }

    // Supabase environment variables
    const supabaseUrl =
      process.env.NEXT_PUBLIC_SUPABASE_URL;

    const supabaseKey =
      process.env.NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY;

    if (!supabaseUrl || !supabaseKey) {
      return NextResponse.json(
        {
          success: false,
          error:
            "Supabase environment variables are missing.",
        },
        { status: 500 }
      );
    }

    // Create Supabase client
    const supabase = createClient(
      supabaseUrl,
      supabaseKey
    );

    // Get observations inside OceanEmbed region
    const { data, error } = await supabase
      .from("observations")
      .select("*")
      .gte("latitude", 5)
      .lte("latitude", 30)
      .gte("longitude", 45)
      .lte("longitude", 105);

    if (error) {
      console.error("Supabase error:", error);

      return NextResponse.json(
        {
          success: false,
          error: "Unable to retrieve ocean observations.",
          details: error.message,
        },
        { status: 500 }
      );
    }

    if (!data || data.length === 0) {
      return NextResponse.json(
        {
          success: false,
          error:
            "No ocean observations found in the study region.",
        },
        { status: 404 }
      );
    }

    // Find the nearest observation
    let nearestObservation = data[0];
    let smallestDistance = Number.POSITIVE_INFINITY;

    for (const observation of data) {
      const latDifference =
        Number(observation.latitude) - latitude;

      const lonDifference =
        Number(observation.longitude) - longitude;

      const distance = Math.sqrt(
        latDifference * latDifference +
          lonDifference * lonDifference
      );

      if (distance < smallestDistance) {
        smallestDistance = distance;
        nearestObservation = observation;
      }
    }

    return NextResponse.json({
      success: true,

      selected_location: {
        latitude,
        longitude,
      },

      observation: {
        id: nearestObservation.id,
        date: nearestObservation.date,
        latitude: nearestObservation.latitude,
        longitude: nearestObservation.longitude,
        sst: nearestObservation.sst,
        sss: nearestObservation.sss,
        ssh: nearestObservation.ssh,
        current_u: nearestObservation.current_u,
        current_v: nearestObservation.current_v,
        wind_u: nearestObservation.wind_u,
        wind_v: nearestObservation.wind_v,
      },

      distance_degrees: Number(
        smallestDistance.toFixed(4)
      ),
    });
  } catch (error) {
    console.error(
      "Location observation API error:",
      error
    );

    return NextResponse.json(
      {
        success: false,
        error:
          error instanceof Error
            ? error.message
            : "Failed to retrieve observation.",
      },
      { status: 500 }
    );
  }
}