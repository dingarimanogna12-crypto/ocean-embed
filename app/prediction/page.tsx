"use client";

import { Suspense, useEffect, useState } from "react";
import { useSearchParams } from "next/navigation";

import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";

type Observation = {
  id: number;
  date: string;
  latitude: number;
  longitude: number;
  sst: number;
  sss: number;
  ssh: number;
  current_u: number;
  current_v: number;
  wind_u?: number;
  wind_v?: number;
};

type Prediction = {
  depth: number;
  temperature: number;
  uncertainty?: number;
  confidence?: string;
  priority_score?: number;
  priority?: string;
  recommendation?: string;
};

type PriorityData = {
  highest_priority_depth: number;
  highest_priority_score: number;
  recommendation?: string;
};

// ======================================================
// MAIN PREDICTION CONTENT
// ======================================================

function PredictionPageContent() {
  const searchParams = useSearchParams();

  const latitude = searchParams.get("lat");
  const longitude = searchParams.get("lon");

  const [observation, setObservation] =
    useState<Observation | null>(null);

  const [loadingObservation, setLoadingObservation] =
    useState(true);

  const [observationError, setObservationError] =
    useState("");

  const [predictions, setPredictions] =
    useState<Prediction[]>([]);

  const [loadingPrediction, setLoadingPrediction] =
    useState(false);

  const [predictionError, setPredictionError] =
    useState("");

  const [priority, setPriority] =
    useState<PriorityData | null>(null);

  // ==================================================
  // LOAD OCEAN OBSERVATION
  // ==================================================

  useEffect(() => {
    async function loadObservation() {
      if (!latitude || !longitude) {
        setObservationError(
          "No location was selected from the Ocean Map."
        );

        setLoadingObservation(false);
        return;
      }

      try {
        setLoadingObservation(true);
        setObservationError("");

        const response = await fetch(
          `/api/observations/location?lat=${latitude}&lon=${longitude}`,
          {
            cache: "no-store",
          }
        );

        const data = await response.json();

        if (!response.ok || !data.success) {
          throw new Error(
            data.error ||
              "Unable to retrieve ocean observation."
          );
        }

        setObservation(data.observation);
      } catch (error) {
        console.error(
          "Observation loading error:",
          error
        );

        setObservationError(
          error instanceof Error
            ? error.message
            : "Failed to load ocean observation."
        );
      } finally {
        setLoadingObservation(false);
      }
    }

    loadObservation();
  }, [latitude, longitude]);

  // ==================================================
  // RUN OCEANEMBED PREDICTION
  // ==================================================

  async function runPrediction() {
    if (!observation) {
      setPredictionError(
        "Ocean observation is not available yet."
      );

      return;
    }

    try {
      setLoadingPrediction(true);
      setPredictionError("");
      setPredictions([]);
      setPriority(null);

      const response = await fetch(
        "/api/observations/predictions",
        {
          method: "POST",

          headers: {
            "Content-Type": "application/json",
          },

          body: JSON.stringify({
            latitude: observation.latitude,
            longitude: observation.longitude,
            sst: observation.sst,
            sss: observation.sss,
            ssh: observation.ssh,
            current_u: observation.current_u,
            current_v: observation.current_v,
          }),
        }
      );

      const data = await response.json();

      console.log(
        "OceanEmbed prediction response:",
        data
      );

      if (!response.ok || !data.success) {
        throw new Error(
          data.error ||
            "OceanEmbed prediction failed."
        );
      }

      // ----------------------------------------------
      // TEMPERATURE PROFILE
      // ----------------------------------------------

      const profile =
        Array.isArray(data.profile)
          ? data.profile
          : [];

      setPredictions(profile);

      // ----------------------------------------------
      // OBSERVATION PRIORITY
      // ----------------------------------------------

      const priorityData =
        data.observation_priority;

      let depth: number | undefined;
      let score: number | undefined;
      let recommendation: string | undefined;

      if (
        priorityData &&
        priorityData.highest_priority_depth !==
          undefined
      ) {
        depth = Number(
          priorityData.highest_priority_depth
        );
      }

      if (
        priorityData &&
        priorityData.highest_priority_score !==
          undefined
      ) {
        score = Number(
          priorityData.highest_priority_score
        );
      }

      if (
        priorityData &&
        priorityData.recommendation
      ) {
        recommendation =
          priorityData.recommendation;
      }

      // ----------------------------------------------
      // DIRECT API FALLBACK
      // ----------------------------------------------

      if (
        depth === undefined ||
        Number.isNaN(depth)
      ) {
        if (
          data.highest_priority_depth !==
          undefined
        ) {
          depth = Number(
            data.highest_priority_depth
          );
        }
      }

      if (
        score === undefined ||
        Number.isNaN(score)
      ) {
        if (
          data.highest_priority_score !==
          undefined
        ) {
          score = Number(
            data.highest_priority_score
          );
        }
      }

      // ----------------------------------------------
      // CALCULATE FROM PROFILE IF NEEDED
      // ----------------------------------------------

      if (
        depth === undefined ||
        Number.isNaN(depth) ||
        score === undefined ||
        Number.isNaN(score)
      ) {
        const candidates =
          profile.filter(
            (item: Prediction) =>
              typeof item.priority_score ===
                "number" &&
              Number.isFinite(
                item.priority_score
              )
          );

        if (candidates.length > 0) {
          const highest =
            candidates.reduce(
              (
                previous: Prediction,
                current: Prediction
              ) =>
                (current.priority_score ?? 0) >
                (previous.priority_score ?? 0)
                  ? current
                  : previous
            );

          depth = highest.depth;

          score =
            highest.priority_score ?? 0;

          recommendation =
            highest.recommendation;
        }
      }

      // ----------------------------------------------
      // SET PRIORITY
      // ----------------------------------------------

      if (
        depth !== undefined &&
        score !== undefined &&
        Number.isFinite(depth) &&
        Number.isFinite(score)
      ) {
        setPriority({
          highest_priority_depth: depth,
          highest_priority_score: score,
          recommendation,
        });
      } else {
        console.warn(
          "Priority information was not found in API response."
        );

        setPriority(null);
      }
    } catch (error) {
      console.error(
        "Prediction error:",
        error
      );

      setPredictionError(
        error instanceof Error
          ? error.message
          : "Failed to generate OceanEmbed prediction."
      );
    } finally {
      setLoadingPrediction(false);
    }
  }

  // ==================================================
  // NO LOCATION SELECTED
  // ==================================================

  if (!latitude || !longitude) {
    return (
      <main className="min-h-screen bg-slate-950 text-white p-8">
        <div className="max-w-5xl mx-auto">

          <div className="mb-8">
            <p className="text-cyan-400 text-sm font-semibold tracking-widest">
              OCEANEMBED
            </p>

            <h1 className="text-4xl font-bold mt-2">
              Subsurface Temperature Prediction
            </h1>
          </div>

          <div className="bg-red-500/10 border border-red-500/30 rounded-2xl p-6">

            <h2 className="text-xl font-semibold text-red-300">
              No Ocean Location Selected
            </h2>

            <p className="text-slate-300 mt-2">
              Please select a location from the
              Ocean Map before running a prediction.
            </p>

            <a
              href="/map"
              className="inline-block mt-5 px-6 py-3 rounded-xl bg-cyan-500 text-slate-950 font-bold hover:bg-cyan-400"
            >
              Open Ocean Map →
            </a>

          </div>

        </div>
      </main>
    );
  }

  // ==================================================
  // MAIN PAGE
  // ==================================================

  return (
    <main className="min-h-screen bg-slate-950 text-white p-8">

      <div className="max-w-7xl mx-auto">

        {/* HEADER */}

        <div className="mb-8">

          <p className="text-cyan-400 text-sm font-semibold tracking-[0.25em]">
            OCEANEMBED AI RECONSTRUCTION
          </p>

          <h1 className="text-4xl font-bold mt-3">
            Subsurface Temperature Prediction
          </h1>

          <p className="text-slate-400 mt-3 max-w-3xl">
            Satellite and ocean surface observations
            are used to reconstruct the temperature
            profile beneath the selected location.
          </p>

        </div>

        {/* LOCATION */}

        <section className="bg-slate-900 border border-slate-800 rounded-2xl p-6 mb-6">

          <div className="flex items-center justify-between mb-5">

            <div>
              <h2 className="text-xl font-semibold">
                {"\uD83D\uDCCD"} Selected Ocean Location
              </h2>

              <p className="text-slate-400 text-sm mt-1">
                Location selected from OceanEmbed Map
              </p>
            </div>

            <div className="px-3 py-1 rounded-full bg-cyan-500/10 text-cyan-400 text-sm">
              North Indian Ocean
            </div>

          </div>

          <div className="grid md:grid-cols-3 gap-4">

            <InfoCard
              label="Latitude"
              value={`${Number(latitude).toFixed(4)}°N`}
            />

            <InfoCard
              label="Longitude"
              value={`${Number(longitude).toFixed(4)}°E`}
            />

            <InfoCard
              label="Study Region"
              value="North Indian Ocean"
            />

          </div>

        </section>

        {/* SURFACE OBSERVATION */}

        <section className="bg-slate-900 border border-slate-800 rounded-2xl p-6 mb-6">

          <div className="flex items-center justify-between mb-6">

            <div>
              <h2 className="text-xl font-semibold">
                🌊 Surface Ocean Observation
              </h2>

              <p className="text-slate-400 text-sm mt-1">
                Observation retrieved from OceanEmbed data source
              </p>
            </div>

            {observation && (
              <span className="px-3 py-1 rounded-full bg-green-500/10 text-green-400 text-sm">
                ● Data Loaded
              </span>
            )}

          </div>

          {loadingObservation && (
            <div className="bg-slate-800 rounded-xl p-5">
              <p className="text-cyan-400">
                Loading ocean observation...
              </p>
            </div>
          )}

          {observationError && (
            <div className="bg-red-500/10 border border-red-500/30 rounded-xl p-5">

              <p className="text-red-300">
                {observationError}
              </p>

            </div>
          )}

          {observation && (
            <>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">

                <InfoCard
                  label="SST"
                  value={`${observation.sst} °C`}
                />

                <InfoCard
                  label="SSS"
                  value={`${observation.sss}`}
                />

                <InfoCard
                  label="SSH"
                  value={`${observation.ssh} m`}
                />

                <InfoCard
                  label="Current U"
                  value={`${observation.current_u}`}
                />

                <InfoCard
                  label="Current V"
                  value={`${observation.current_v}`}
                />

                <InfoCard
                  label="Wind U"
                  value={
                    observation.wind_u !== undefined
                      ? `${observation.wind_u}`
                      : "Not available"
                  }
                />

                <InfoCard
                  label="Wind V"
                  value={
                    observation.wind_v !== undefined
                      ? `${observation.wind_v}`
                      : "Not available"
                  }
                />

                <InfoCard
                  label="Observation Date"
                  value={observation.date}
                />

              </div>

              <div className="mt-6 flex flex-wrap items-center gap-4">

                <button
                  onClick={runPrediction}
                  disabled={loadingPrediction}
                  className="px-7 py-3 rounded-xl bg-cyan-500 text-slate-950 font-bold hover:bg-cyan-400 transition disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {loadingPrediction
                    ? "Running OceanEmbed AI..."
                    : "Run OceanEmbed Prediction →"}
                </button>

                <p className="text-sm text-slate-500">
                  Uses the loaded surface observation
                  as the ML input.
                </p>

              </div>

            </>
          )}

        </section>

        {/* PREDICTION ERROR */}

        {predictionError && (
          <section className="bg-red-500/10 border border-red-500/30 rounded-2xl p-5 mb-6">

            <h3 className="font-semibold text-red-300">
              Prediction Error
            </h3>

            <p className="text-red-300 mt-2">
              {predictionError}
            </p>

          </section>
        )}

        {/* OBSERVATION PRIORITY */}

        {priority && (
          <section className="bg-slate-900 border border-slate-800 rounded-2xl p-6 mb-6">

            <div className="flex items-center justify-between mb-5">

              <div>
                <h2 className="text-xl font-semibold">
                  🎯 Observation Priority
                </h2>

                <p className="text-slate-400 text-sm mt-1">
                  Identifies where additional in-situ
                  observations may be valuable.
                </p>
              </div>

              <span
                className={`px-3 py-1 rounded-full text-sm font-semibold ${
                  priority.highest_priority_score >= 70
                    ? "bg-red-500/10 text-red-400"
                    : priority.highest_priority_score >= 30
                    ? "bg-yellow-500/10 text-yellow-400"
                    : "bg-green-500/10 text-green-400"
                }`}
              >
                {priority.highest_priority_score >= 70
                  ? "HIGH"
                  : priority.highest_priority_score >= 30
                  ? "MEDIUM"
                  : "LOW"}
              </span>

            </div>

            <div className="grid md:grid-cols-3 gap-4">

              <InfoCard
                label="Priority Depth"
                value={`${priority.highest_priority_depth} m`}
              />

              <InfoCard
                label="Priority Score"
                value={`${priority.highest_priority_score.toFixed(
                  1
                )} / 100`}
              />

              <InfoCard
                label="Recommended Action"
                value={
                  priority.recommendation ||
                  (priority.highest_priority_score >= 70
                    ? "Additional in-situ observation recommended"
                    : priority.highest_priority_score >= 30
                    ? "Monitor with additional observations"
                    : "Current prediction is relatively stable")
                }
              />

            </div>

          </section>
        )}

        {/* TEMPERATURE PROFILE */}

        {predictions.length > 0 && (
          <section className="bg-slate-900 border border-slate-800 rounded-2xl p-6 mb-6">

            <div className="mb-6">

              <h2 className="text-xl font-semibold">
                {"\uD83C\uDF21\uFE0F"} Reconstructed Temperature Profile
              </h2>

              <p className="text-slate-400 text-sm mt-2">
                OceanEmbed AI reconstruction from the
                surface to the available modeled depth range.
              </p>

            </div>

            <div className="h-[500px] w-full">

              <ResponsiveContainer
                width="100%"
                height="100%"
              >

                <LineChart
                  data={predictions}
                  layout="vertical"
                  margin={{
                    top: 20,
                    right: 30,
                    left: 30,
                    bottom: 30,
                  }}
                >

                  <CartesianGrid
                    strokeDasharray="3 3"
                  />

                  <XAxis
                    type="number"
                    dataKey="temperature"
                    label={{
                      value: "Temperature (°C)",
                      position: "insideBottom",
                      offset: -15,
                    }}
                  />

                  <YAxis
                    type="number"
                    dataKey="depth"
                    reversed
                    domain={[
                      "dataMin",
                      "dataMax",
                    ]}
                    label={{
                      value: "Depth (m)",
                      angle: -90,
                      position: "insideLeft",
                    }}
                  />

                  <Tooltip
                    formatter={(value) => [
                      `${Number(value ?? 0).toFixed(3)} °C`,
                      "Temperature",
                    ]}
                  />

                  <Line
                    type="monotone"
                    dataKey="temperature"
                    strokeWidth={3}
                    dot={{
                      r: 4,
                    }}
                    activeDot={{
                      r: 6,
                    }}
                  />

                </LineChart>

              </ResponsiveContainer>

            </div>

          </section>
        )}

        {/* PREDICTION TABLE */}

        {predictions.length > 0 && (
          <section className="bg-slate-900 border border-slate-800 rounded-2xl p-6 mb-8">

            <div className="mb-5">

              <h2 className="text-xl font-semibold">
                Prediction Details
              </h2>

              <p className="text-slate-400 text-sm mt-1">
                Temperature, uncertainty and observation
                priority for each reconstructed depth.
              </p>

            </div>

            <div className="overflow-x-auto">

              <table className="w-full text-left">

                <thead>

                  <tr className="border-b border-slate-700 text-slate-400">

                    <th className="p-3">
                      Depth
                    </th>

                    <th className="p-3">
                      Temperature
                    </th>

                    <th className="p-3">
                      Uncertainty
                    </th>

                    <th className="p-3">
                      Confidence
                    </th>

                    <th className="p-3">
                      Priority
                    </th>

                  </tr>

                </thead>

                <tbody>

                  {predictions.map(
                    (item) => (
                      <tr
                        key={item.depth}
                        className="border-b border-slate-800 hover:bg-slate-800/50"
                      >

                        <td className="p-3 font-medium">
                          {item.depth} m
                        </td>

                        <td className="p-3">
                          {Number(
                            item.temperature
                          ).toFixed(3)}
                          {" °C"}
                        </td>

                        <td className="p-3">
                          {item.uncertainty !==
                            undefined
                            ? Number(
                                item.uncertainty
                              ).toFixed(3)
                            : "—"}
                        </td>

                        <td className="p-3">

                          <span
                            className={
                              item.confidence ===
                              "HIGH"
                                ? "text-green-400"
                                : item.confidence ===
                                  "MEDIUM"
                                ? "text-yellow-400"
                                : "text-red-400"
                            }
                          >
                            {item.confidence ||
                              "—"}
                          </span>

                        </td>

                        <td className="p-3">

                          <span
                            className={
                              item.priority ===
                              "HIGH"
                                ? "text-red-400"
                                : item.priority ===
                                  "MEDIUM"
                                ? "text-yellow-400"
                                : "text-green-400"
                            }
                          >
                            {item.priority ||
                              "—"}
                          </span>

                        </td>

                      </tr>
                    )
                  )}

                </tbody>

              </table>

            </div>

          </section>
        )}

      </div>

    </main>
  );
}

// ======================================================
// REUSABLE INFO CARD
// ======================================================

function InfoCard({
  label,
  value,
}: {
  label: string;
  value: string;
}) {
  return (
    <div className="bg-slate-800 rounded-xl p-4 border border-slate-700">

      <p className="text-slate-400 text-sm">
        {label}
      </p>

      <p className="text-lg font-semibold mt-2 break-words">
        {value}
      </p>

    </div>
  );
}

// ======================================================
// PAGE WRAPPER WITH SUSPENSE
// ======================================================

export default function PredictionPage() {
  return (
    <Suspense
      fallback={
        <main className="min-h-screen bg-slate-950 text-white flex items-center justify-center">
          <div className="text-center">

            <div className="text-cyan-400 text-lg font-semibold">
              Loading OceanEmbed...
            </div>

            <p className="text-slate-400 mt-2">
              Preparing the ocean prediction profile...
            </p>

          </div>
        </main>
      }
    >
      <PredictionPageContent />
    </Suspense>i
  );
}