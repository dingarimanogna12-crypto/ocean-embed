"use client";

import MapPicker from "../../components/OceanMap/MapPicker";

export default function MapPage() {
  return (
    <main className="min-h-screen bg-slate-950 text-white">
      {/* HEADER */}
      <section className="px-6 py-8 border-b border-slate-800">
        <div className="max-w-7xl mx-auto">
          <div className="text-sm text-cyan-400 font-semibold tracking-wide">
            OCEANEMBED AI
          </div>

          <h1 className="text-3xl md:text-4xl font-bold mt-2">
            Ocean Intelligence Map
          </h1>

          <p className="text-slate-400 mt-2 max-w-3xl">
            Select a location in the North Indian Ocean to load real
            surface observations and reconstruct subsurface ocean
            temperature using OceanEmbed AI.
          </p>
        </div>
      </section>

      {/* MAP + PREDICTION */}
      <section className="px-6 py-8">
        <div className="max-w-7xl mx-auto">
          <MapPicker />
        </div>
      </section>

      {/* SCIENTIFIC NOTE */}
      <section className="px-6 pb-10">
        <div className="max-w-7xl mx-auto">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5">
            <div className="text-sm text-cyan-400 font-semibold mb-2">
              ABOUT THIS PREDICTION
            </div>

            <p className="text-sm text-slate-400 leading-6">
              OceanEmbed uses surface ocean observations such as sea
              surface temperature, salinity, sea surface height and
              surface currents to estimate subsurface temperature at
              multiple depths. Validation-calibrated uncertainty and
              observation-priority information are also provided to
              indicate where additional observations may be valuable.
            </p>
          </div>
        </div>
      </section>
    </main>
  );
}