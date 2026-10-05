
export default function Home() {
  return (
    <main className="min-h-screen bg-slate-950 text-white">
      {/* Navigation */}
      <nav className="flex items-center justify-between border-b border-white/10 px-8 py-5">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-cyan-500/20 text-2xl">
            🌊
          </div>

          <span className="text-xl font-bold tracking-wide">
            OceanEmbed
          </span>
        </div>

        <div className="hidden gap-8 text-sm text-slate-300 md:flex">
          <a href="/" className="transition hover:text-cyan-400">
            Home
          </a>

          <a href="/dashboard" className="transition hover:text-cyan-400">
            Dashboard
          </a>

          <a href="/map" className="transition hover:text-cyan-400">
            Ocean Map
          </a>

          <a href="/prediction" className="transition hover:text-cyan-400">
            Prediction
          </a>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="relative flex min-h-[calc(100vh-81px)] items-center justify-center overflow-hidden px-6 py-20">
        {/* Background glow */}
        <div className="absolute left-1/2 top-1/2 h-[500px] w-[500px] -translate-x-1/2 -translate-y-1/2 rounded-full bg-cyan-500/10 blur-3xl" />

        <div className="relative z-10 mx-auto max-w-5xl text-center">
          {/* Small label */}
          <div className="mb-6 inline-flex items-center gap-2 rounded-full border border-cyan-400/20 bg-cyan-400/10 px-5 py-2 text-sm text-cyan-300">
            🛰️ AI-Powered Ocean Intelligence
          </div>

          {/* Main title */}
          <h1 className="text-5xl font-extrabold tracking-tight sm:text-6xl md:text-7xl">
            <span className="text-white">🌊 Ocean</span>
            <span className="text-cyan-400">Embed</span>
          </h1>

          {/* Subtitle */}
          <h2 className="mx-auto mt-6 max-w-3xl text-xl font-medium leading-relaxed text-slate-200 sm:text-2xl">
            Satellite Embedding-Based Deep Learning Framework
            <br />
            for Reconstruction of Subsurface Ocean Temperature
          </h2>

          {/* Description */}
          <p className="mx-auto mt-6 max-w-2xl text-base leading-7 text-slate-400 sm:text-lg">
            Reconstruct subsurface ocean temperature from surface satellite
            observations using multimodal deep learning and provide
            uncertainty-aware ocean intelligence.
          </p>

          {/* Workflow */}
          <div className="mx-auto mt-12 flex max-w-4xl flex-col items-center justify-center gap-4 sm:flex-row">
            {/* Step 1 */}
            <div className="w-56 rounded-2xl border border-white/10 bg-white/5 p-5 backdrop-blur">
              <div className="text-4xl">🛰️</div>
              <h3 className="mt-3 font-semibold text-white">
                Surface Observations
              </h3>
              <p className="mt-2 text-xs leading-5 text-slate-400">
                SST • SSS • SSH • Currents • Wind
              </p>
            </div>

            {/* Arrow */}
            <div className="text-2xl text-cyan-400">→</div>

            {/* Step 2 */}
            <div className="w-56 rounded-2xl border border-cyan-400/30 bg-cyan-400/10 p-5 backdrop-blur">
              <div className="text-4xl">🤖</div>
              <h3 className="mt-3 font-semibold text-cyan-300">
                OceanEmbed AI
              </h3>
              <p className="mt-2 text-xs leading-5 text-slate-400">
                Multimodal deep learning
              </p>
            </div>

            {/* Arrow */}
            <div className="text-2xl text-cyan-400">→</div>

            {/* Step 3 */}
            <div className="w-56 rounded-2xl border border-white/10 bg-white/5 p-5 backdrop-blur">
              <div className="text-4xl">🌊</div>
              <h3 className="mt-3 font-semibold text-white">
                Ocean Profile
              </h3>
              <p className="mt-2 text-xs leading-5 text-slate-400">
                Subsurface temperature
              </p>
            </div>
          </div>

          {/* Buttons */}
          <div className="mt-12 flex flex-col items-center justify-center gap-4 sm:flex-row">
            <a
              href="/dashboard"
              className="rounded-xl bg-cyan-500 px-8 py-4 font-semibold text-slate-950 shadow-lg shadow-cyan-500/20 transition hover:scale-105 hover:bg-cyan-400"
            >
              Explore Dashboard →
            </a>

            <a
              href="/prediction"
              className="rounded-xl border border-white/20 bg-white/5 px-8 py-4 font-semibold text-white backdrop-blur transition hover:border-cyan-400/50 hover:bg-cyan-400/10"
            >
              Run Prediction
            </a>
          </div>

          {/* Region */}
          <p className="mt-10 text-sm text-slate-500">
            North Indian Ocean • 5°N–30°N • 45°E–105°E
          </p>
        </div>
      </section>
    </main>
  );
}