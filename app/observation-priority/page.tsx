"use client";

import { useEffect, useMemo, useState } from "react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from "recharts";

type PriorityRow = {
  depth_min_m: number;
  depth_max_m: number;
  uncertainty_score: number;
  error_score: number;
  sample_bonus: number;
  reliability_bonus: number;
  priority_score: number;
  observation_priority: string;
};

export default function ObservationPriority() {
  const [data, setData] = useState<PriorityRow[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    fetch("/api/observation-priority")
      .then((res) => res.json())
      .then((result) => {
        if (result.success) {
          setData(result.data);
        } else {
          setError(result.error || "Unable to load priority data");
        }
      })
      .catch(() => {
        setError("Unable to connect to the observation priority API");
      })
      .finally(() => {
        setLoading(false);
      });
  }, []);

  const highestPriority = useMemo(() => {
    if (!data.length) return null;

    return [...data].sort(
      (a, b) => b.priority_score - a.priority_score
    )[0];
  }, [data]);

  const mediumCount = data.filter(
    (row) => row.observation_priority === "MEDIUM"
  ).length;

  const lowCount = data.filter(
    (row) => row.observation_priority === "LOW"
  ).length;

  if (loading) {
    return (
      <main className="min-h-screen bg-slate-950 text-white p-8">
        <p className="text-cyan-400">Loading observation priority...</p>
      </main>
    );
  }

  if (error) {
    return (
      <main className="min-h-screen bg-slate-950 text-white p-8">
        <p className="text-red-400">{error}</p>
      </main>
    );
  }

  return (
    <main className="min-h-screen bg-slate-950 text-white p-6 md:p-8">
      <div className="max-w-7xl mx-auto">
        <p className="text-cyan-400 text-sm font-semibold tracking-wider">
          OCEANEMBED INTELLIGENCE
        </p>

        <h1 className="mt-2 text-4xl font-bold">
          Observation Priority
        </h1>

        <p className="mt-3 max-w-3xl text-slate-400">
          Identify depth regions where additional in-situ observations
          could provide the greatest value for improving OceanEmbed
          reconstruction reliability.
        </p>

        <div className="grid gap-4 md:grid-cols-4 mt-8">
          <div className="rounded-2xl border border-slate-800 bg-slate-900 p-5">
            <p className="text-sm text-slate-400">
              Highest Priority Zone
            </p>

            <p className="mt-2 text-2xl font-bold text-cyan-400">
              {highestPriority
                ? `${highestPriority.depth_min_m}–${highestPriority.depth_max_m} m`
                : "—"}
            </p>

            <p className="mt-1 text-sm text-slate-500">
              Recommended observation region
            </p>
          </div>

          <div className="rounded-2xl border border-slate-800 bg-slate-900 p-5">
            <p className="text-sm text-slate-400">
              Priority Score
            </p>

            <p className="mt-2 text-2xl font-bold">
              {highestPriority
                ? highestPriority.priority_score.toFixed(2)
                : "—"}
            </p>

            <p className="mt-1 text-sm text-slate-500">
              Highest calculated score
            </p>
          </div>

          <div className="rounded-2xl border border-slate-800 bg-slate-900 p-5">
            <p className="text-sm text-slate-400">
              Medium Priority Zones
            </p>

            <p className="mt-2 text-2xl font-bold text-yellow-400">
              {mediumCount}
            </p>

            <p className="mt-1 text-sm text-slate-500">
              Depth regions requiring attention
            </p>
          </div>

          <div className="rounded-2xl border border-slate-800 bg-slate-900 p-5">
            <p className="text-sm text-slate-400">
              Low Priority Zones
            </p>

            <p className="mt-2 text-2xl font-bold text-green-400">
              {lowCount}
            </p>

            <p className="mt-1 text-sm text-slate-500">
              Lower observation urgency
            </p>
          </div>
        </div>

        <div className="mt-8 rounded-2xl border border-slate-800 bg-slate-900 p-6">
          <h2 className="text-xl font-semibold">
            How Observation Priority Works
          </h2>

          <div className="grid gap-4 md:grid-cols-5 mt-6">
            {[
              ["01", "Prediction", "Generate subsurface temperature"],
              ["02", "Uncertainty", "Estimate prediction reliability"],
              ["03", "Error", "Measure validation error"],
              ["04", "Priority", "Combine evidence into a score"],
              ["05", "Observation", "Recommend where data is valuable"],
            ].map(([number, title, description]) => (
              <div
                key={number}
                className="rounded-xl border border-slate-800 bg-slate-950 p-4"
              >
                <p className="text-cyan-400 text-sm font-bold">
                  {number}
                </p>

                <h3 className="mt-2 font-semibold">
                  {title}
                </h3>

                <p className="mt-1 text-xs text-slate-500">
                  {description}
                </p>
              </div>
            ))}
          </div>
        </div>

        <div className="mt-8 rounded-2xl border border-cyan-900 bg-cyan-950/20 p-6">
          <p className="text-cyan-400 text-sm font-semibold">
            KEY OBSERVATION
          </p>

          <h2 className="mt-2 text-2xl font-bold">
            The 50–125 m layer needs the most attention
          </h2>

          <p className="mt-3 text-slate-300 max-w-4xl">
            The current prototype assigns Medium observation priority
            to the 50–75 m, 75–100 m, and 100–125 m depth ranges.
            These regions combine higher uncertainty and validation
            error, indicating that additional in-situ observations
            could be particularly useful for improving reconstruction
            reliability.
          </p>
        </div>

        <div className="mt-8 rounded-2xl border border-slate-800 bg-slate-900 p-6">
          <h2 className="text-xl font-semibold">
            Depth-wise Observation Priority
          </h2>

          <p className="mt-2 text-sm text-slate-500">
            Higher scores indicate greater potential value from
            additional observations.
          </p>

          <div className="mt-6 h-[420px]">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart
                data={data}
                margin={{
                  top: 10,
                  right: 20,
                  left: 10,
                  bottom: 50,
                }}
              >
                <CartesianGrid
                  strokeDasharray="3 3"
                  stroke="#334155"
                />

                <XAxis
                  dataKey="depth_min_m"
                  stroke="#94a3b8"
                  tickFormatter={(value) => `${value}m`}
                  label={{
                    value: "Depth range start (m)",
                    position: "insideBottom",
                    offset: -30,
                    fill: "#94a3b8",
                  }}
                />

                <YAxis
                  stroke="#94a3b8"
                  domain={[0, 100]}
                  label={{
                    value: "Priority Score",
                    angle: -90,
                    position: "insideLeft",
                    fill: "#94a3b8",
                  }}
                />

                <Tooltip
                  contentStyle={{
                    backgroundColor: "#0f172a",
                    border: "1px solid #334155",
                    borderRadius: "10px",
                    color: "#fff",
                  }}
                  formatter={(value) => [
                    Number(value ?? 0).toFixed(2),
                    "Priority Score",
                  ]}
                  labelFormatter={(value) => `Depth: ${value} m`}
                />

                <Bar dataKey="priority_score">
                  {data.map((entry, index) => (
                    <Cell
                      key={`cell-${index}`}
                      fill={
                        entry.observation_priority === "MEDIUM"
                          ? "#facc15"
                          : "#22c55e"
                      }
                    />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="mt-8 rounded-2xl border border-slate-800 bg-slate-900 p-6">
          <h2 className="text-xl font-semibold">
            Priority Analysis by Depth
          </h2>

          <div className="mt-5 overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-slate-800 text-slate-400">
                  <th className="text-left py-3 px-3">
                    Depth Range
                  </th>

                  <th className="text-right py-3 px-3">
                    Uncertainty
                  </th>

                  <th className="text-right py-3 px-3">
                    Error
                  </th>

                  <th className="text-right py-3 px-3">
                    Priority Score
                  </th>

                  <th className="text-center py-3 px-3">
                    Priority
                  </th>
                </tr>
              </thead>

              <tbody>
                {data.map((row) => (
                  <tr
                    key={`${row.depth_min_m}-${row.depth_max_m}`}
                    className="border-b border-slate-800/70"
                  >
                    <td className="py-3 px-3">
                      {row.depth_min_m}–{row.depth_max_m} m
                    </td>

                    <td className="py-3 px-3 text-right">
                      {row.uncertainty_score.toFixed(2)}
                    </td>

                    <td className="py-3 px-3 text-right">
                      {row.error_score.toFixed(2)}
                    </td>

                    <td className="py-3 px-3 text-right font-semibold">
                      {row.priority_score.toFixed(2)}
                    </td>

                    <td className="py-3 px-3 text-center">
                      <span
                        className={
                          row.observation_priority === "MEDIUM"
                            ? "inline-flex rounded-full px-3 py-1 text-xs font-semibold bg-yellow-500/20 text-yellow-300"
                            : "inline-flex rounded-full px-3 py-1 text-xs font-semibold bg-green-500/20 text-green-300"
                        }
                      >
                        {row.observation_priority}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        <div className="mt-8 grid gap-6 md:grid-cols-2">
          <div className="rounded-2xl border border-slate-800 bg-slate-900 p-6">
            <h2 className="text-xl font-semibold">
              Recommended Strategy
            </h2>

            <ul className="mt-4 space-y-3 text-slate-300 text-sm">
              <li>
                • Prioritize additional observations between{" "}
                <strong>50–125 m</strong>.
              </li>

              <li>
                • Focus validation efforts where uncertainty and
                prediction error are higher.
              </li>

              <li>
                • Use new observations to identify and correct
                model weaknesses.
              </li>

              <li>
                • Feed improved observations back into future
                model development.
              </li>
            </ul>
          </div>

          <div className="rounded-2xl border border-slate-800 bg-slate-900 p-6">
            <h2 className="text-xl font-semibold">
              Why This Matters
            </h2>

            <p className="mt-4 text-sm leading-6 text-slate-400">
              OceanEmbed does not simply produce a temperature
              prediction. It also identifies where that prediction
              is less reliable and helps guide future observations.
              This creates a feedback loop between AI prediction,
              uncertainty estimation and ocean observations.
            </p>

            <div className="mt-5 rounded-xl bg-slate-950 p-4">
              <p className="text-sm text-cyan-400 font-medium">
                AI → Prediction → Uncertainty → Priority →
                Observation → Improved Validation
              </p>
            </div>
          </div>
        </div>

        <div className="mt-8 mb-10 rounded-xl border border-slate-800 bg-slate-900/60 p-5">
          <p className="text-xs leading-5 text-slate-500">
            Research prototype: observation priority is calculated
            from the current validation-calibrated uncertainty and
            error profile. The present result is based on the
            available prototype validation dataset and should not
            be interpreted as an operational deployment recommendation.
          </p>
        </div>
      </div>
    </main>
  );
}