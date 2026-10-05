"use client";

import dynamic from "next/dynamic";
import { useState } from "react";

const LeafletMap = dynamic(
  () => import("./LeafletMap"),
  {
    ssr: false,
    loading: () => (
      <div className="w-full h-[520px] flex items-center justify-center bg-slate-900 text-cyan-400">
        Loading Ocean Map...
      </div>
    ),
  }
);

type PredictionPoint = {
  depth: number;
  temperature: number;
  uncertainty?: number;
  confidence?: string;
  priority?: string;
};

export default function MapPicker() {
  const [location, setLocation] = useState({
    lat: 15.5,
    lon: 72.5,
  });

  const [loading, setLoading] = useState(false);
  const [observation, setObservation] = useState<any>(null);
  const [profile, setProfile] = useState<PredictionPoint[]>([]);

  const runPrediction = async () => {
    setLoading(true);
    setObservation(null);
    setProfile([]);

    try {
      // 1. Find nearest real GLORYS observation
      const observationResponse = await fetch(
        `/api/observations/lookup?latitude=${location.lat}&longitude=${location.lon}`
      );

      const observationResult = await observationResponse.json();

      if (!observationResponse.ok || !observationResult.success) {
        throw new Error(
          observationResult.error || "Could not find observation"
        );
      }

      const obs = observationResult.observation;

      setObservation(obs);

      // 2. Send REAL observation values to ML model
      const predictionResponse = await fetch(
        "/api/observations/predictions",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            latitude: location.lat,
            longitude: location.lon,
            sst: obs.sst,
            sss: obs.sss,
            ssh: obs.ssh,
            current_u: obs.current_u,
            current_v: obs.current_v,
          }),
        }
      );

      const predictionResult = await predictionResponse.json();

      if (!predictionResponse.ok || !predictionResult.success) {
        throw new Error(
          predictionResult.error || "Prediction failed"
        );
      }

      console.log("OceanEmbed Prediction:", predictionResult);

      // 3. Store reconstructed temperature profile
      const predictionProfile =
        predictionResult.profile || [];

      setProfile(predictionProfile);

    } catch (error) {
      console.error(
        "OceanEmbed prediction error:",
        error
      );

      alert(
        error instanceof Error
          ? error.message
          : "Prediction failed."
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-4">

      {/* MAP */}
      <div className="relative w-full h-[520px] rounded-2xl overflow-hidden border border-slate-700">
        <LeafletMap
          onLocation={(lat, lon) => {
            setLocation({
              lat: Number(lat.toFixed(4)),
              lon: Number(lon.toFixed(4)),
            });

            setObservation(null);
            setProfile([]);
          }}
        />

        <div className="absolute top-4 left-4 z-[1000] bg-slate-950/90 border border-slate-700 rounded-xl px-4 py-3">
          <div className="text-xs text-cyan-400 font-semibold">
            OCEANEMBED AI
          </div>

          <div className="text-white font-semibold">
            North Indian Ocean
          </div>

          <div className="text-xs text-slate-400 mt-1">
            Click anywhere on the ocean
          </div>
        </div>

        <div className="absolute bottom-4 left-4 z-[1000] bg-slate-950/90 border border-slate-700 rounded-xl px-4 py-3">
          <div className="text-xs text-slate-400">
            Selected Location
          </div>

          <div className="text-cyan-300 font-semibold">
            {location.lat}° N, {location.lon}° E
          </div>
        </div>
      </div>

      {/* CONTROL PANEL */}
      <div className="bg-slate-900 border border-slate-700 rounded-xl p-4">

        <div className="flex items-center justify-between">

          <div>
            <div className="text-sm text-slate-400">
              Selected Ocean Point
            </div>

            <div className="text-white font-semibold">
              {location.lat}° N, {location.lon}° E
            </div>
          </div>

          <button
            onClick={runPrediction}
            disabled={loading}
            className="px-5 py-3 rounded-xl bg-cyan-500 hover:bg-cyan-400 disabled:bg-slate-600 text-slate-950 font-semibold transition"
          >
            {loading
              ? "Running OceanEmbed..."
              : "Run OceanEmbed Prediction"}
          </button>

        </div>

        {/* REAL OBSERVATION */}
        {observation && (
          <div className="mt-4 pt-4 border-t border-slate-700">

            <div className="text-sm text-cyan-400 font-semibold mb-3">
              REAL GLORYS SURFACE OBSERVATION
            </div>

            <div className="grid grid-cols-2 md:grid-cols-5 gap-3">

              <div>
                <div className="text-xs text-slate-500">
                  SST
                </div>
                <div className="text-white">
                  {observation.sst.toFixed(2)} °C
                </div>
              </div>

              <div>
                <div className="text-xs text-slate-500">
                  SSS
                </div>
                <div className="text-white">
                  {observation.sss.toFixed(2)}
                </div>
              </div>

              <div>
                <div className="text-xs text-slate-500">
                  SSH
                </div>
                <div className="text-white">
                  {observation.ssh.toFixed(3)} m
                </div>
              </div>

              <div>
                <div className="text-xs text-slate-500">
                  Current U
                </div>
                <div className="text-white">
                  {observation.current_u.toFixed(3)}
                </div>
              </div>

              <div>
                <div className="text-xs text-slate-500">
                  Current V
                </div>
                <div className="text-white">
                  {observation.current_v.toFixed(3)}
                </div>
              </div>

            </div>
          </div>
        )}

        {/* TEMPERATURE PROFILE */}
        {profile.length > 0 && (
          <div className="mt-6 pt-5 border-t border-slate-700">

            <div className="flex items-center justify-between mb-4">
              <div>
                <div className="text-sm text-cyan-400 font-semibold">
                  RECONSTRUCTED SUBSURFACE TEMPERATURE
                </div>

                <div className="text-xs text-slate-400 mt-1">
                  OceanEmbed AI temperature profile
                </div>
              </div>

              <div className="text-xs text-slate-500">
                {profile.length} depth levels
              </div>
            </div>

            {/* VISUAL PROFILE */}
            <div className="relative bg-slate-950 rounded-xl p-4">

              <div className="space-y-2">

                {profile.map((point, index) => (
                  <div
                    key={`${point.depth}-${index}`}
                    className="grid grid-cols-[70px_1fr_90px] gap-3 items-center"
                  >

                    <div className="text-xs text-slate-400">
                      {point.depth} m
                    </div>

                    <div className="relative h-7 bg-slate-800 rounded-lg overflow-hidden">

                      <div
                        className="h-full bg-cyan-500 rounded-lg"
                        style={{
                          width: `${Math.max(
                            8,
                            Math.min(
                              100,
                              ((point.temperature - 8) / 23) * 100
                            )
                          )}%`,
                        }}
                      />

                      <div className="absolute inset-0 flex items-center px-3 text-xs font-semibold text-white">
                        {point.temperature.toFixed(2)} °C
                      </div>

                    </div>

                    <div className="text-right text-xs text-slate-400">
                      {point.uncertainty !== undefined
                        ? `±${point.uncertainty.toFixed(2)} °C`
                        : "—"}
                    </div>

                  </div>
                ))}

              </div>
            </div>

            {/* PROFILE TABLE */}
            <div className="mt-4 overflow-x-auto">

              <table className="w-full text-sm">

                <thead>
                  <tr className="border-b border-slate-700 text-slate-400">
                    <th className="text-left py-2">
                      Depth
                    </th>

                    <th className="text-left py-2">
                      Temperature
                    </th>

                    <th className="text-left py-2">
                      Uncertainty
                    </th>

                    <th className="text-left py-2">
                      Confidence
                    </th>

                    <th className="text-left py-2">
                      Priority
                    </th>
                  </tr>
                </thead>

                <tbody>

                  {profile.map((point, index) => (
                    <tr
                      key={`${point.depth}-table-${index}`}
                      className="border-b border-slate-800"
                    >

                      <td className="py-2 text-slate-300">
                        {point.depth} m
                      </td>

                      <td className="py-2 text-white font-semibold">
                        {point.temperature.toFixed(2)} °C
                      </td>

                      <td className="py-2 text-slate-300">
                        {point.uncertainty !== undefined
                          ? `±${point.uncertainty.toFixed(2)} °C`
                          : "—"}
                      </td>

                      <td className="py-2 text-slate-300">
                        {point.confidence || "—"}
                      </td>

                      <td className="py-2 text-slate-300">
                        {point.priority || "—"}
                      </td>

                    </tr>
                  ))}

                </tbody>

              </table>

            </div>

          </div>
        )}

      </div>

    </div>
  );
}