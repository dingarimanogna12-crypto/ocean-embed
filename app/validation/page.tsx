"use client";

import { useEffect, useState } from "react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";

type ValidationRow = {
  argo_depth: number;
  argo_temperature: number;
  oceanembed_temperature: number;
  error: number;
  absolute_error: number;
};

type ProfileGroup = {
  depths: number[];
  argo: number[];
  oceanembed: number[];
};

export default function Validation() {
  const [data, setData] = useState<ValidationRow[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch("/api/validation")
      .then((res) => res.json())
      .then((result) => {
        setData(result.data || []);
        setLoading(false);
      })
      .catch(() => {
        setLoading(false);
      });
  }, []);

  // -----------------------------
  // Validation Metrics
  // -----------------------------

  const mae =
    data.length > 0
      ? data.reduce((sum, row) => sum + Math.abs(row.error), 0) /
        data.length
      : 0;

  const rmse =
    data.length > 0
      ? Math.sqrt(
          data.reduce(
            (sum, row) => sum + row.error * row.error,
            0
          ) / data.length
        )
      : 0;

  const bias =
    data.length > 0
      ? data.reduce((sum, row) => sum + row.error, 0) /
        data.length
      : 0;

  // -----------------------------
  // Create clean depth-binned
  // ARGO vs OceanEmbed profile
  // -----------------------------

  const groupedProfiles = data.reduce(
    (groups, row) => {
      // 25 metre depth bins
      const bin = Math.floor(row.argo_depth / 25) * 25;

      if (!groups[bin]) {
        groups[bin] = {
          depths: [],
          argo: [],
          oceanembed: [],
        };
      }

      groups[bin].depths.push(row.argo_depth);
      groups[bin].argo.push(row.argo_temperature);
      groups[bin].oceanembed.push(
        row.oceanembed_temperature
      );

      return groups;
    },
    {} as Record<number, ProfileGroup>
  );

  const profileData = Object.values(groupedProfiles).map(
    (group) => ({
      depth:
        group.depths.reduce(
          (sum, value) => sum + value,
          0
        ) / group.depths.length,

      argo_temperature:
        group.argo.reduce(
          (sum, value) => sum + value,
          0
        ) / group.argo.length,

      oceanembed_temperature:
        group.oceanembed.reduce(
          (sum, value) => sum + value,
          0
        ) / group.oceanembed.length,
    })
  );

  return (
    <main className="min-h-screen bg-slate-950 text-white p-8">

      {/* -------------------------------- */}
      {/* HEADER */}
      {/* -------------------------------- */}

      <p className="text-cyan-400 text-sm font-medium">
        OCEANEMBED VALIDATION
      </p>

      <h1 className="mt-2 text-4xl font-bold">
        ARGO Validation
      </h1>

      <p className="mt-3 max-w-3xl text-slate-400">
        Compare OceanEmbed reconstructed subsurface
        temperatures with independent in-situ observations
        from ARGO floats.
      </p>

      {/* -------------------------------- */}
      {/* METRICS */}
      {/* -------------------------------- */}

      <div className="mt-10 grid gap-5 md:grid-cols-4">

        {/* MAE */}

        <div className="rounded-2xl border border-white/10 bg-slate-900 p-6">
          <p className="text-sm text-slate-400">
            MAE
          </p>

          <p className="mt-3 text-3xl font-bold text-cyan-400">
            {mae.toFixed(3)} °C
          </p>

          <p className="mt-2 text-xs text-slate-500">
            Mean Absolute Error
          </p>
        </div>

        {/* RMSE */}

        <div className="rounded-2xl border border-white/10 bg-slate-900 p-6">
          <p className="text-sm text-slate-400">
            RMSE
          </p>

          <p className="mt-3 text-3xl font-bold text-cyan-400">
            {rmse.toFixed(3)} °C
          </p>

          <p className="mt-2 text-xs text-slate-500">
            Root Mean Square Error
          </p>
        </div>

        {/* BIAS */}

        <div className="rounded-2xl border border-white/10 bg-slate-900 p-6">
          <p className="text-sm text-slate-400">
            Bias
          </p>

          <p className="mt-3 text-3xl font-bold text-cyan-400">
            {bias >= 0 ? "+" : ""}
            {bias.toFixed(3)} °C
          </p>

          <p className="mt-2 text-xs text-slate-500">
            Mean Prediction Bias
          </p>
        </div>

        {/* OBSERVATIONS */}

        <div className="rounded-2xl border border-white/10 bg-slate-900 p-6">
          <p className="text-sm text-slate-400">
            Observations
          </p>

          <p className="mt-3 text-3xl font-bold text-cyan-400">
            {data.length}
          </p>

          <p className="mt-2 text-xs text-slate-500">
            Matched depth observations
          </p>
        </div>

      </div>

      {/* -------------------------------- */}
      {/* VALIDATION STATUS */}
      {/* -------------------------------- */}

      <section className="mt-8 rounded-2xl border border-cyan-500/20 bg-cyan-500/5 p-6">

        <div className="flex items-center gap-3">

          <div className="h-3 w-3 rounded-full bg-cyan-400" />

          <h2 className="text-lg font-semibold">
            Independent ARGO Validation
          </h2>

        </div>

        <p className="mt-3 text-sm leading-6 text-slate-400">
          OceanEmbed predictions are evaluated against
          independent ARGO float observations. This provides
          an external check of reconstructed subsurface
          temperature rather than evaluating only against
          the training dataset.
        </p>

      </section>

      {/* -------------------------------- */}
      {/* MAIN TEMPERATURE PROFILE */}
      {/* -------------------------------- */}

      <section className="mt-8 rounded-2xl border border-white/10 bg-slate-900 p-6">

        <h2 className="text-xl font-semibold">
          📊 ARGO vs OceanEmbed Temperature
        </h2>

        <p className="mt-2 text-sm text-slate-400">
          Depth-binned comparison of independent ARGO
          measurements and OceanEmbed reconstructed
          temperature.
        </p>

        <p className="mt-2 text-xs text-slate-500">
          Observations are grouped into 25 m depth bins to
          create a clean representative thermal profile.
        </p>

        <div className="mt-8 h-[500px]">

          {loading ? (

            <div className="flex h-full items-center justify-center text-slate-400">
              Loading validation data...
            </div>

          ) : profileData.length === 0 ? (

            <div className="flex h-full items-center justify-center text-red-400">
              No validation data available.
            </div>

          ) : (

            <ResponsiveContainer
              width="100%"
              height="100%"
            >

              <LineChart
                data={profileData}
                margin={{
                  top: 20,
                  right: 30,
                  left: 10,
                  bottom: 30,
                }}
              >

                <CartesianGrid
                  strokeDasharray="3 3"
                />

                <XAxis
                  dataKey="depth"
                  type="number"
                  domain={[
                    "dataMin",
                    "dataMax",
                  ]}
                  label={{
                    value: "Depth (m)",
                    position: "insideBottom",
                    offset: -15,
                  }}
                />

                <YAxis
                  label={{
                    value: "Temperature (°C)",
                    angle: -90,
                    position: "insideLeft",
                  }}
                />

                <Tooltip
                  formatter={(value) =>
                    `${Number(value).toFixed(2)} °C`
                  }
                  labelFormatter={(value) =>
                    `Depth: ${Number(value).toFixed(1)} m`
                  }
                />

                <Legend />

                {/* ARGO */}

                <Line
                  type="monotone"
                  dataKey="argo_temperature"
                  name="ARGO"
                  dot
                  strokeWidth={3}
                />

                {/* OceanEmbed */}

                <Line
                  type="monotone"
                  dataKey="oceanembed_temperature"
                  name="OceanEmbed"
                  dot
                  strokeWidth={3}
                />

              </LineChart>

            </ResponsiveContainer>

          )}

        </div>

      </section>

      {/* -------------------------------- */}
      {/* ERROR GRAPH */}
      {/* -------------------------------- */}

      <section className="mt-8 rounded-2xl border border-white/10 bg-slate-900 p-6">

        <h2 className="text-xl font-semibold">
          Depth-wise Prediction Error
        </h2>

        <p className="mt-2 text-sm text-slate-400">
          Larger errors indicate depths where the current
          prototype has greater reconstruction uncertainty.
        </p>

        <div className="mt-8 h-[350px]">

          {loading ? (

            <div className="flex h-full items-center justify-center text-slate-400">
              Loading error data...
            </div>

          ) : (

            <ResponsiveContainer
              width="100%"
              height="100%"
            >

              <LineChart
                data={data}
                margin={{
                  top: 20,
                  right: 30,
                  left: 10,
                  bottom: 30,
                }}
              >

                <CartesianGrid
                  strokeDasharray="3 3"
                />

                <XAxis
                  dataKey="argo_depth"
                  type="number"
                  domain={[
                    "dataMin",
                    "dataMax",
                  ]}
                  label={{
                    value: "Depth (m)",
                    position: "insideBottom",
                    offset: -15,
                  }}
                />

                <YAxis
                  label={{
                    value: "Error (°C)",
                    angle: -90,
                    position: "insideLeft",
                  }}
                />

                <Tooltip
                  formatter={(value) =>
                    `${Number(value).toFixed(3)} °C`
                  }
                  labelFormatter={(value) =>
                    `Depth: ${Number(value).toFixed(1)} m`
                  }
                />

                <Line
                  type="monotone"
                  dataKey="absolute_error"
                  name="Absolute Error"
                  dot={false}
                  strokeWidth={3}
                />

              </LineChart>

            </ResponsiveContainer>

          )}

        </div>

      </section>

      {/* -------------------------------- */}
      {/* VALIDATION TABLE */}
      {/* -------------------------------- */}

      <section className="mt-8 rounded-2xl border border-white/10 bg-slate-900 p-6">

        <h2 className="text-xl font-semibold">
          Validation Samples
        </h2>

        <p className="mt-2 text-sm text-slate-400">
          Individual ARGO measurements compared with
          OceanEmbed reconstructed temperatures.
        </p>

        <div className="mt-6 overflow-x-auto rounded-xl border border-white/10">

          <table className="w-full text-left">

            <thead className="bg-slate-800">

              <tr>

                <th className="p-4">
                  Depth
                </th>

                <th className="p-4">
                  OceanEmbed
                </th>

                <th className="p-4">
                  ARGO
                </th>

                <th className="p-4">
                  Error
                </th>

              </tr>

            </thead>

            <tbody>

              {data
                .slice(0, 15)
                .map((row, index) => (

                  <tr
                    key={index}
                    className="border-t border-white/10"
                  >

                    <td className="p-4">
                      {row.argo_depth.toFixed(1)} m
                    </td>

                    <td className="p-4 text-cyan-400">
                      {row.oceanembed_temperature.toFixed(3)} °C
                    </td>

                    <td className="p-4">
                      {row.argo_temperature.toFixed(3)} °C
                    </td>

                    <td
                      className={`p-4 ${
                        Math.abs(row.error) > 1
                          ? "text-red-400"
                          : "text-green-400"
                      }`}
                    >

                      {row.error >= 0 ? "+" : ""}
                      {row.error.toFixed(3)} °C

                    </td>

                  </tr>

                ))}

            </tbody>

          </table>

        </div>

      </section>

      {/* -------------------------------- */}
      {/* SCIENTIFIC INTERPRETATION */}
      {/* -------------------------------- */}

      <section className="mt-8 grid gap-5 md:grid-cols-2">

        {/* Interpretation */}

        <div className="rounded-2xl border border-white/10 bg-slate-900 p-6">

          <h2 className="text-lg font-semibold">
            🔬 Validation Interpretation
          </h2>

          <ul className="mt-4 space-y-3 text-sm text-slate-400">

            <li>
              • Independent ARGO observations are used
              for evaluation.
            </li>

            <li>
              • The depth-binned profile shows the overall
              agreement between observed and reconstructed
              temperature.
            </li>

            <li>
              • Depth-wise error reveals where the current
              reconstruction is less reliable.
            </li>

            <li>
              • Higher errors around the thermocline region
              motivate uncertainty-aware monitoring.
            </li>

          </ul>

        </div>

        {/* Prototype Note */}

        <div className="rounded-2xl border border-white/10 bg-slate-900 p-6">

          <h2 className="text-lg font-semibold">
            Prototype Validation Note
          </h2>

          <p className="mt-4 text-sm leading-6 text-slate-400">
            The current validation represents a research
            prototype evaluated on a matched ARGO subset.
            It should not be interpreted as full operational
            validation for the entire North Indian Ocean.
          </p>

          <div className="mt-5 rounded-xl bg-slate-800 p-4">

            <p className="text-xs uppercase tracking-wide text-slate-500">
              Current validation result
            </p>

            <p className="mt-2 text-2xl font-bold text-cyan-400">
              {mae.toFixed(3)} °C MAE
            </p>

            <p className="mt-1 text-xs text-slate-500">
              Based on {data.length} matched depth observations
            </p>

          </div>

        </div>

      </section>

    </main>
  );
}