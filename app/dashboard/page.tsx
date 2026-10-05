"use client";

import { useEffect, useState } from "react";
import { createClient } from "@/lib/supabase/client";

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
  wind_u: number | null;
  wind_v: number | null;
};

export default function Dashboard() {
  const [observation, setObservation] =
    useState<Observation | null>(null);

  const [loading, setLoading] = useState(true);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  useEffect(() => {
    async function loadObservation() {
      try {
        const supabase = createClient();

        const { data, error } = await supabase
          .from("observations")
          .select("*")
          .order("date", { ascending: false })
          .limit(1);

        console.log("OceanEmbed Supabase data:", data);
        console.log("OceanEmbed Supabase error:", error);

        if (error) {
          setErrorMessage(error.message);
          setLoading(false);
          return;
        }

        if (data && data.length > 0) {
          setObservation(data[0]);
        } else {
          setErrorMessage(
            "Supabase connected successfully, but returned 0 observations."
          );
        }

        setLoading(false);
      } catch (error) {
        console.error("Dashboard error:", error);

        setErrorMessage(
          error instanceof Error
            ? error.message
            : "Unknown Supabase connection error."
        );

        setLoading(false);
      }
    }

    loadObservation();
  }, []);

  return (
    <main className="min-h-screen bg-slate-950 p-8 text-white">

      <div>
        <p className="text-sm font-medium text-cyan-400">
          OCEANEMBED
        </p>

        <h1 className="mt-2 text-4xl font-bold">
          Ocean Intelligence Dashboard
        </h1>

        <p className="mt-3 text-slate-400">
          Surface ocean observations from Supabase.
        </p>
      </div>

      {loading && (
        <div className="mt-10 rounded-2xl border border-white/10 bg-slate-900 p-8">
          <p className="text-slate-400">
            Loading ocean observations...
          </p>
        </div>
      )}

      {!loading && errorMessage && (
        <div className="mt-10 rounded-2xl border border-yellow-400/20 bg-yellow-400/5 p-8">
          <p className="text-yellow-300 font-semibold">
            Supabase diagnostic
          </p>

          <p className="mt-3 text-slate-300">
            {errorMessage}
          </p>
        </div>
      )}

      {!loading && observation && (
        <>
          <div className="mt-10 rounded-2xl border border-cyan-400/20 bg-cyan-400/5 p-6">

            <p className="text-sm text-slate-400">
              Observation Location
            </p>

            <h2 className="mt-2 text-2xl font-bold">
              {observation.latitude}°N,{" "}
              {observation.longitude}°E
            </h2>

            <p className="mt-2 text-sm text-slate-500">
              Observation date: {observation.date}
            </p>

          </div>

          <div className="mt-8 grid gap-5 sm:grid-cols-2 lg:grid-cols-4">

            <div className="rounded-2xl border border-white/10 bg-slate-900 p-6">
              <p className="text-sm text-slate-400">
                🌡️ Sea Surface Temperature
              </p>

              <p className="mt-3 text-3xl font-bold text-cyan-400">
                {observation.sst}°C
              </p>
            </div>

            <div className="rounded-2xl border border-white/10 bg-slate-900 p-6">
              <p className="text-sm text-slate-400">
                🧂 Sea Surface Salinity
              </p>

              <p className="mt-3 text-3xl font-bold text-cyan-400">
                {observation.sss}
              </p>
            </div>

            <div className="rounded-2xl border border-white/10 bg-slate-900 p-6">
              <p className="text-sm text-slate-400">
                🌊 Sea Surface Height
              </p>

              <p className="mt-3 text-3xl font-bold text-cyan-400">
                {observation.ssh} m
              </p>
            </div>

            <div className="rounded-2xl border border-white/10 bg-slate-900 p-6">
              <p className="text-sm text-slate-400">
                🌀 Surface Current
              </p>

              <p className="mt-3 text-2xl font-bold text-cyan-400">
                U: {observation.current_u}
              </p>

              <p className="mt-2 text-xs text-slate-500">
                V: {observation.current_v}
              </p>
            </div>

          </div>

          <div className="mt-6 rounded-2xl border border-white/10 bg-slate-900 p-6">

            <h2 className="text-xl font-semibold">
              💨 Surface Wind
            </h2>

            <div className="mt-5 grid gap-5 md:grid-cols-2">

              <div className="rounded-xl bg-slate-800 p-5">
                <p className="text-sm text-slate-400">
                  Wind U
                </p>

                <p className="mt-2 text-2xl font-bold">
                  {observation.wind_u ?? "Not available"}
                </p>
              </div>

              <div className="rounded-xl bg-slate-800 p-5">
                <p className="text-sm text-slate-400">
                  Wind V
                </p>

                <p className="mt-2 text-2xl font-bold">
                  {observation.wind_v ?? "Not available"}
                </p>
              </div>

            </div>
          </div>

          <div className="mt-8 rounded-2xl border border-cyan-400/20 bg-cyan-400/5 p-6">

            <h2 className="text-xl font-semibold">
              🤖 OceanEmbed AI
            </h2>

            <p className="mt-2 text-slate-400">
              These surface observations will be provided
              to the OceanEmbed model to reconstruct
              subsurface ocean temperature.
            </p>

            <a
              href="/prediction"
              className="mt-5 inline-block rounded-xl bg-cyan-500 px-6 py-3 font-semibold text-slate-950 hover:bg-cyan-400"
            >
              Run Prediction →
            </a>

          </div>
        </>
      )}

    </main>
  );
}