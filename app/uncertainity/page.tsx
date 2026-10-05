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

type UncertaintyRow = {
  depth_min_m: number;
  depth_max_m: number;
  uncertainty_90_c: number;
  confidence: string;
  mean_error?: number;
  mae?: number;
  error_std?: number;
  p90_absolute_error?: number;
};

export default function Uncertainty() {
  const [data, setData] = useState<UncertaintyRow[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch("/api/uncertainty")
      .then((res) => res.json())
      .then((result) => {
        setData(result.data || []);
        setLoading(false);
      })
      .catch((error) => {
        console.error("Uncertainty loading error:", error);
        setLoading(false);
      });
  }, []);

  // --------------------------------
  // SUMMARY VALUES
  // --------------------------------

  const averageUncertainty =
    data.length > 0
      ? data.reduce(
          (sum, row) => sum + Number(row.uncertainty_90_c || 0),
          0
        ) / data.length
      : 0;

  const maximumUncertainty =
    data.length > 0
      ? Math.max(
          ...data.map((row) =>
            Number(row.uncertainty_90_c || 0)
          )
        )
      : 0;

  const highConfidence = data.filter(
    (row) => row.confidence === "HIGH"
  ).length;

  const mediumConfidence = data.filter(
    (row) => row.confidence === "MEDIUM"
  ).length;

  const lowConfidence = data.filter(
    (row) => row.confidence === "LOW"
  ).length;

  const highestUncertaintyDepth =
    data.length > 0
      ? data.reduce((previous, current) =>
          Number(current.uncertainty_90_c) >
          Number(previous.uncertainty_90_c)
            ? current
            : previous
        )
      : null;

  // --------------------------------
  // GRAPH DATA
  // --------------------------------

  const chartData = data.map((row) => ({
    depth: `${row.depth_min_m}-${row.depth_max_m}`,
    depthValue:
      (Number(row.depth_min_m) +
        Number(row.depth_max_m)) /
      2,
    uncertainty: Number(row.uncertainty_90_c),
    mae:
      row.mae !== undefined
        ? Number(row.mae)
        : null,
  }));

  return (
    <main className="min-h-screen bg-slate-950 text-white p-8">

      {/* -------------------------------- */}
      {/* HEADER */}
      {/* -------------------------------- */}

      <p className="text-cyan-400 text-sm font-medium">
        OCEANEMBED AI
      </p>

      <h1 className="mt-2 text-4xl font-bold">
        Uncertainty & Confidence
      </h1>

      <p className="mt-3 max-w-3xl text-slate-400">
        Identify where the OceanEmbed prediction is reliable
        and where additional observations may be required.
      </p>

      {/* -------------------------------- */}
      {/* MAIN SUMMARY */}
      {/* -------------------------------- */}

      <div className="mt-10 rounded-2xl border border-cyan-400/20 bg-cyan-400/5 p-8">

        <div className="grid gap-8 md:grid-cols-3">

          {/* Average uncertainty */}

          <div>
            <p className="text-sm text-slate-400">
              Average 90% Uncertainty
            </p>

            <p className="mt-3 text-3xl font-bold text-cyan-400">
              {loading
                ? "--"
                : `±${averageUncertainty.toFixed(3)} °C`}
            </p>

            <p className="mt-2 text-xs text-slate-500">
              Validation-calibrated uncertainty
            </p>
          </div>

          {/* Maximum uncertainty */}

          <div>
            <p className="text-sm text-slate-400">
              Maximum Uncertainty
            </p>

            <p className="mt-3 text-3xl font-bold text-cyan-400">
              {loading
                ? "--"
                : `±${maximumUncertainty.toFixed(3)} °C`}
            </p>

            <p className="mt-2 text-xs text-slate-500">
              Highest uncertainty depth region
            </p>
          </div>

          {/* Highest uncertainty depth */}

          <div>
            <p className="text-sm text-slate-400">
              Priority Depth
            </p>

            <p className="mt-3 text-3xl font-bold text-cyan-400">
              {loading || !highestUncertaintyDepth
                ? "--"
                : `${highestUncertaintyDepth.depth_min_m}-${highestUncertaintyDepth.depth_max_m} m`}
            </p>

            <p className="mt-2 text-xs text-slate-500">
              Highest reconstruction uncertainty
            </p>
          </div>

        </div>

      </div>

      {/* -------------------------------- */}
      {/* CONFIDENCE CARDS */}
      {/* -------------------------------- */}

      <div className="mt-8 grid gap-6 md:grid-cols-3">

        {/* HIGH */}

        <div className="rounded-2xl border border-green-400/20 bg-slate-900 p-6">

          <div className="text-3xl">
            {"\uD83D\uDFE2"}
          </div>

          <h2 className="mt-4 font-semibold text-green-400">
            High Confidence
          </h2>

          <p className="mt-2 text-sm text-slate-400">
            Model prediction is relatively reliable based
            on validation performance.
          </p>

          <p className="mt-4 text-2xl font-bold text-white">
            {highConfidence}
          </p>

          <p className="text-xs text-slate-500">
            depth regions
          </p>

        </div>

        {/* MEDIUM */}

        <div className="rounded-2xl border border-yellow-400/20 bg-slate-900 p-6">

          <div className="text-3xl">
            {"\uD83D\uDFE1"}
          </div>

          <h2 className="mt-4 font-semibold text-yellow-400">
            Moderate Confidence
          </h2>

          <p className="mt-2 text-sm text-slate-400">
            Prediction should be interpreted with additional
            caution.
          </p>

          <p className="mt-4 text-2xl font-bold text-white">
            {mediumConfidence}
          </p>

          <p className="text-xs text-slate-500">
            depth regions
          </p>

        </div>

        {/* LOW */}

        <div className="rounded-2xl border border-red-400/20 bg-slate-900 p-6">

          <div className="text-3xl">
            {"\uD83D\uDD34"}
          </div>

          <h2 className="mt-4 font-semibold text-red-400">
            Low Confidence
          </h2>

          <p className="mt-2 text-sm text-slate-400">
            Additional observations may be useful for
            validation and correction.
          </p>

          <p className="mt-4 text-2xl font-bold text-white">
            {lowConfidence}
          </p>

          <p className="text-xs text-slate-500">
            depth regions
          </p>

        </div>

      </div>

      {/* -------------------------------- */}
      {/* UNCERTAINTY GRAPH */}
      {/* -------------------------------- */}

      <section className="mt-8 rounded-2xl border border-white/10 bg-slate-900 p-6">

        <h2 className="text-xl font-semibold">
          Depth-wise Uncertainty
        </h2>

        <p className="mt-2 text-sm text-slate-400">
          Validation-calibrated 90% uncertainty across
          different ocean depth ranges.
        </p>

        <div className="mt-8 h-[450px]">

          {loading ? (

            <div className="flex h-full items-center justify-center text-slate-400">
              Loading uncertainty data...
            </div>

          ) : chartData.length === 0 ? (

            <div className="flex h-full items-center justify-center text-red-400">
              No uncertainty data available.
            </div>

          ) : (

            <ResponsiveContainer
              width="100%"
              height="100%"
            >

              <LineChart
                data={chartData}
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
                  dataKey="depthValue"
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
                    value: "90% Uncertainty (°C)",
                    angle: -90,
                    position: "insideLeft",
                  }}
                />

                <Tooltip
                  formatter={(value) =>
                    `±${Number(value).toFixed(3)} °C`
                  }
                  labelFormatter={(value) =>
                    `Depth: ${Number(value).toFixed(1)} m`
                  }
                />

                <Legend />

                <Line
                  type="monotone"
                  dataKey="uncertainty"
                  name="90% Uncertainty"
                  dot
                  strokeWidth={3}
                />

              </LineChart>

            </ResponsiveContainer>

          )}

        </div>

      </section>

      {/* -------------------------------- */}
      {/* HIGHEST UNCERTAINTY */}
      {/* -------------------------------- */}

      {highestUncertaintyDepth && (
        <section className="mt-8 rounded-2xl border border-yellow-400/20 bg-yellow-400/5 p-6">

          <h2 className="text-xl font-semibold">
            Observation Attention Zone
          </h2>

          <p className="mt-3 text-sm leading-6 text-slate-400">
            The highest uncertainty occurs around{" "}
            <span className="font-semibold text-white">
              {highestUncertaintyDepth.depth_min_m}–
              {highestUncertaintyDepth.depth_max_m} m
            </span>
            , where the estimated 90% uncertainty reaches{" "}
            <span className="font-semibold text-yellow-400">
              ±
              {Number(
                highestUncertaintyDepth.uncertainty_90_c
              ).toFixed(3)} °C
            </span>
            .
          </p>

          <p className="mt-3 text-sm leading-6 text-slate-400">
            These regions can be prioritized for additional
            in-situ observations such as ARGO profiles,
            helping the system identify where satellite-only
            reconstruction is less reliable.
          </p>

        </section>
      )}

      {/* -------------------------------- */}
      {/* HOW UNCERTAINTY IS CALCULATED */}
      {/* -------------------------------- */}

      <section className="mt-8 grid gap-6 md:grid-cols-2">

        <div className="rounded-2xl border border-white/10 bg-slate-900 p-6">

          <h2 className="text-lg font-semibold">
            How OceanEmbed Estimates Uncertainty
          </h2>

          <div className="mt-4 space-y-3 text-sm text-slate-400">

            <p>
              <span className="text-cyan-400">
                1.
              </span>{" "}
              OceanEmbed generates a subsurface temperature
              prediction.
            </p>

            <p>
              <span className="text-cyan-400">
                2.
              </span>{" "}
              Predictions are compared against independent
              ARGO observations.
            </p>

            <p>
              <span className="text-cyan-400">
                3.
              </span>{" "}
              Prediction errors are grouped by depth.
            </p>

            <p>
              <span className="text-cyan-400">
                4.
              </span>{" "}
              The resulting error distribution is converted
              into a validation-calibrated uncertainty range.
            </p>

          </div>

        </div>

        <div className="rounded-2xl border border-white/10 bg-slate-900 p-6">

          <h2 className="text-lg font-semibold">
            Why This Matters
          </h2>

          <p className="mt-4 text-sm leading-6 text-slate-400">
            Satellite observations provide excellent surface
            coverage but cannot directly observe the complete
            subsurface temperature structure. OceanEmbed
            therefore reports uncertainty alongside each
            reconstructed depth.
          </p>

          <p className="mt-4 text-sm leading-6 text-slate-400">
            This allows the system to distinguish between
            regions where AI reconstruction is reliable and
            regions where additional observations should be
            considered.
          </p>

        </div>

      </section>

      {/* -------------------------------- */}
      {/* RESEARCH PROTOTYPE NOTE */}
      {/* -------------------------------- */}

      <section className="mt-8 rounded-2xl border border-white/10 bg-slate-900 p-6">

        <p className="text-xs uppercase tracking-wide text-slate-500">
          Research Prototype
        </p>

        <h2 className="mt-2 text-lg font-semibold">
          Validation-Calibrated Uncertainty
        </h2>

        <p className="mt-3 text-sm leading-6 text-slate-400">
          OceanEmbed provides uncertainty estimates derived
          from independent ARGO residuals. The current
          uncertainty profile is intended for prototype
          evaluation and observation-priority analysis, not
          as a certified operational uncertainty product.
        </p>

      </section>

    </main>
  );
}