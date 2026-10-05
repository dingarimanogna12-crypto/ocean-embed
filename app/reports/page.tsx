"use client";

import { useEffect, useState } from "react";

type ReportData = {
  success: boolean;
  summary: {
    validation_samples: number;
    mae: number;
    rmse: number;
    bias: number;
  };
  highest_priority: {
    depth_min_m: number;
    depth_max_m: number;
    priority_score: number;
    priority: string;
  };
  medium_priority_zones: number;
  message: string;
};

export default function Reports() {
  const [report, setReport] = useState<ReportData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    fetch("/api/reports")
      .then((res) => res.json())
      .then((data) => {
        if (data.success) {
          setReport(data);
        } else {
          setError(data.error || "Unable to load report");
        }
      })
      .catch(() => {
        setError("Unable to connect to the Reports API");
      })
      .finally(() => {
        setLoading(false);
      });
  }, []);

  if (loading) {
    return (
      <main className="min-h-screen bg-slate-950 text-white p-8">
        <p className="text-cyan-400">Generating OceanEmbed report...</p>
      </main>
    );
  }

  if (error || !report) {
    return (
      <main className="min-h-screen bg-slate-950 text-white p-8">
        <p className="text-red-400">
          {error || "Report unavailable"}
        </p>
      </main>
    );
  }

  const { summary, highest_priority } = report;

  return (
    <main className="min-h-screen bg-slate-950 text-white p-6 md:p-8">
      <div className="max-w-7xl mx-auto">

        {/* Header */}
        <div className="flex flex-col md:flex-row md:items-end md:justify-between gap-4">
          <div>
            <p className="text-cyan-400 text-sm font-semibold tracking-wider">
              OCEANEMBED INTELLIGENCE
            </p>

            <h1 className="mt-2 text-4xl font-bold">
              Ocean Intelligence Report
            </h1>

            <p className="mt-3 max-w-3xl text-slate-400">
              Integrated summary of OceanEmbed predictions,
              independent ARGO validation, uncertainty analysis and
              observation-priority results.
            </p>
          </div>

          <div className="rounded-xl border border-slate-700 bg-slate-900 px-5 py-3">
            <p className="text-xs text-slate-500">
              STATUS
            </p>
            <p className="mt-1 text-sm font-semibold text-cyan-400">
              RESEARCH PROTOTYPE
            </p>
          </div>
        </div>

        {/* Executive Summary */}
        <section className="mt-8 rounded-2xl border border-cyan-900 bg-cyan-950/20 p-6">
          <p className="text-cyan-400 text-sm font-semibold">
            EXECUTIVE SUMMARY
          </p>

          <h2 className="mt-2 text-2xl font-bold">
            AI-powered subsurface ocean intelligence
          </h2>

          <p className="mt-4 max-w-5xl text-slate-300 leading-7">
            {report.message}
          </p>
        </section>

        {/* Metrics */}
        <section className="mt-8">
          <h2 className="text-xl font-semibold">
            Validation Performance
          </h2>

          <div className="grid gap-4 md:grid-cols-4 mt-5">

            <MetricCard
              title="Validation Samples"
              value={summary.validation_samples.toString()}
              description="Independent ARGO matched observations"
            />

            <MetricCard
              title="MAE"
              value={`${summary.mae.toFixed(3)} °C`}
              description="Mean Absolute Error"
            />

            <MetricCard
              title="RMSE"
              value={`${summary.rmse.toFixed(3)} °C`}
              description="Root Mean Square Error"
            />

            <MetricCard
              title="Bias"
              value={`${summary.bias >= 0 ? "+" : ""}${summary.bias.toFixed(3)} °C`}
              description="Mean prediction error"
            />

          </div>
        </section>

        {/* Interpretation */}
        <section className="mt-8 grid gap-6 md:grid-cols-2">

          <div className="rounded-2xl border border-slate-800 bg-slate-900 p-6">
            <p className="text-sm text-slate-500">
              VALIDATION INTERPRETATION
            </p>

            <h2 className="mt-2 text-xl font-semibold">
              Independent ARGO evaluation
            </h2>

            <p className="mt-4 text-sm leading-6 text-slate-400">
              OceanEmbed was evaluated against matched ARGO
              observations from the prototype validation dataset.
              The current validation result provides an independent
              check of the reconstructed subsurface temperature.
            </p>

            <div className="mt-5 rounded-xl bg-slate-950 p-4">
              <p className="text-sm text-slate-300">
                Current MAE:
                <span className="ml-2 font-bold text-cyan-400">
                  {summary.mae.toFixed(3)} °C
                </span>
              </p>

              <p className="mt-2 text-sm text-slate-300">
                Current RMSE:
                <span className="ml-2 font-bold text-cyan-400">
                  {summary.rmse.toFixed(3)} °C
                </span>
              </p>
            </div>
          </div>

          <div className="rounded-2xl border border-slate-800 bg-slate-900 p-6">
            <p className="text-sm text-slate-500">
              MODEL DIAGNOSTICS
            </p>

            <h2 className="mt-2 text-xl font-semibold">
              Where should attention be focused?
            </h2>

            <p className="mt-4 text-sm leading-6 text-slate-400">
              OceanEmbed combines uncertainty and validation error
              to identify depth regions where additional
              observations may provide the greatest value.
            </p>

            <div className="mt-5 rounded-xl border border-yellow-900 bg-yellow-950/20 p-4">
              <p className="text-xs text-yellow-400">
                HIGHEST PRIORITY REGION
              </p>

              <p className="mt-1 text-2xl font-bold text-yellow-300">
                {highest_priority.depth_min_m}–
                {highest_priority.depth_max_m} m
              </p>

              <p className="mt-1 text-sm text-slate-400">
                Priority score:{" "}
                {highest_priority.priority_score.toFixed(2)}
                {" · "}
                {highest_priority.priority}
              </p>
            </div>
          </div>

        </section>

        {/* End-to-End Workflow */}
        <section className="mt-8 rounded-2xl border border-slate-800 bg-slate-900 p-6">

          <h2 className="text-xl font-semibold">
            OceanEmbed End-to-End Workflow
          </h2>

          <div className="grid gap-4 md:grid-cols-6 mt-6">

            {[
              ["01", "Satellite", "Surface observations"],
              ["02", "Embedding", "Multimodal features"],
              ["03", "Prediction", "Subsurface temperature"],
              ["04", "Validation", "ARGO comparison"],
              ["05", "Uncertainty", "Reliability estimation"],
              ["06", "Priority", "Guide observations"],
            ].map(([number, title, description]) => (
              <div
                key={number}
                className="rounded-xl border border-slate-800 bg-slate-950 p-4"
              >
                <p className="text-cyan-400 text-xs font-bold">
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
        </section>

        {/* Key Findings */}
        <section className="mt-8">
          <h2 className="text-xl font-semibold">
            Key Findings
          </h2>

          <div className="grid gap-4 md:grid-cols-3 mt-5">

            <Finding
              number="01"
              title="Subsurface reconstruction"
              text="Surface ocean observations can be transformed into a depth-resolved temperature profile using the trained OceanEmbed model."
            />

            <Finding
              number="02"
              title="Independent validation"
              text="ARGO observations provide an independent reference for evaluating reconstructed subsurface temperatures."
            />

            <Finding
              number="03"
              title="Adaptive observation"
              text="Uncertainty and validation error can be converted into observation-priority scores to guide future measurements."
            />

          </div>
        </section>

        {/* Impact */}
        <section className="mt-8 rounded-2xl border border-slate-800 bg-slate-900 p-6">

          <h2 className="text-xl font-semibold">
            Potential Applications
          </h2>

          <div className="grid gap-3 md:grid-cols-2 mt-5">

            {[
              "Marine heatwave monitoring",
              "Ocean climate research",
              "Fisheries and ecosystem assessment",
              "Ocean forecasting and data assimilation",
              "ARGO observation planning",
              "Regional ocean monitoring",
            ].map((item) => (
              <div
                key={item}
                className="rounded-xl bg-slate-950 border border-slate-800 p-4 text-sm text-slate-300"
              >
                {item}
              </div>
            ))}

          </div>
        </section>

        {/* Research Note */}
        <section className="mt-8 mb-10 rounded-2xl border border-slate-800 bg-slate-900/60 p-6">

          <h2 className="text-lg font-semibold">
            Research & Prototype Note
          </h2>

          <p className="mt-3 text-sm leading-6 text-slate-500">
            The current OceanEmbed implementation is a research
            prototype. Validation results are based on the available
            prototype ARGO matching dataset and should not be
            interpreted as operational accuracy for the entire North
            Indian Ocean. Further spatial, temporal and independent
            validation is required before operational deployment.
          </p>

        </section>

      </div>
    </main>
  );
}

function MetricCard({
  title,
  value,
  description,
}: {
  title: string;
  value: string;
  description: string;
}) {
  return (
    <div className="rounded-2xl border border-slate-800 bg-slate-900 p-5">
      <p className="text-sm text-slate-400">
        {title}
      </p>

      <p className="mt-2 text-2xl font-bold text-cyan-400">
        {value}
      </p>

      <p className="mt-1 text-xs text-slate-500">
        {description}
      </p>
    </div>
  );
}

function Finding({
  number,
  title,
  text,
}: {
  number: string;
  title: string;
  text: string;
}) {
  return (
    <div className="rounded-2xl border border-slate-800 bg-slate-900 p-6">
      <p className="text-cyan-400 text-sm font-bold">
        {number}
      </p>

      <h3 className="mt-2 text-lg font-semibold">
        {title}
      </h3>

      <p className="mt-3 text-sm leading-6 text-slate-400">
        {text}
      </p>
    </div>
  );
}