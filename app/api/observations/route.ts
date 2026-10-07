import { NextResponse } from "next/server";

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
      if (
        body[field] === undefined ||
        body[field] === null ||
        body[field] === ""
      ) {
        return NextResponse.json(
          {
            success: false,
            error: `Missing field: ${field}`,
          },
          { status: 400 }
        );
      }
    }

    const apiUrl = process.env.OCEANEMBED_API_URL;

    if (!apiUrl) {
      return NextResponse.json(
        {
          success: false,
          error:
            "OceanEmbed backend URL is not configured in Vercel.",
        },
        { status: 500 }
      );
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

    const response = await fetch(`${apiUrl}/predict`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(input),
      cache: "no-store",
    });

    const data = await response.json();

    if (!response.ok) {
      return NextResponse.json(
        {
          success: false,
          error:
            data?.error ||
            "OceanEmbed backend prediction failed.",
          details: data?.details,
        },
        { status: response.status }
      );
    }

    return NextResponse.json(data);
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