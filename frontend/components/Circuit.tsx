"use client";

type CircuitVariant = string;

type CircuitProps = {
  swapped?: boolean;
  running?: boolean;
  scanning?: boolean;
  variant?: CircuitVariant;
};

function SvgDefs() {
  return (
    <defs>
      <filter id="glow">
        <feGaussianBlur stdDeviation="5" result="blur" />
        <feMerge><feMergeNode in="blur" /><feMergeNode in="SourceGraphic" /></feMerge>
      </filter>
      <filter id="strongGlow">
        <feGaussianBlur stdDeviation="8" result="blur" />
        <feMerge><feMergeNode in="blur" /><feMergeNode in="SourceGraphic" /></feMerge>
      </filter>
    </defs>
  );
}

function Battery() {
  return <>
    <line x1="102" y1="143" x2="168" y2="143" className="battery-long" />
    <line x1="114" y1="187" x2="156" y2="187" className="battery-short" />
  </>;
}

function LiveElectrons({ path }: { path: string }) {
  return <>{[0, 0.18, 0.36, 0.54, 0.72].map((delay, i) => (
    <circle key={i} r="6" className="electron electron-live">
      <animateMotion dur="3.8s" begin={`${delay * -3.8}s`} repeatCount="indefinite" path={path} />
    </circle>
  ))}</>;
}

function SeriesBulbs({ swapped, running, ammeters = false }: { swapped: boolean; running: boolean; ammeters?: boolean }) {
  const left = swapped ? "B" : "A";
  const right = swapped ? "A" : "B";
  const path = "M135 258 H555 V78 H135 V258";
  return <svg viewBox="0 0 700 330" className="circuit" aria-label="series circuit with two identical bulbs">
    <SvgDefs />
    <path d="M135 78 H555 V258 H135 Z" className="wire" />
    <Battery />
    <line x1="135" y1="78" x2="135" y2="135" className="wire" />
    <line x1="135" y1="195" x2="135" y2="258" className="wire" />

    <g className="bulb-group bulb-left">
      <circle cx="285" cy="78" r="39" className="bulb-halo" />
      <circle cx="285" cy="78" r="34" className="bulb" />
      <path d="M270 78 q15 -28 30 0 q-15 28 -30 0" className="filament" />
      <text x="285" y="27" textAnchor="middle" className="bulb-label">{left}</text>
    </g>
    <g className="bulb-group bulb-right">
      <circle cx="445" cy="78" r="39" className="bulb-halo" />
      <circle cx="445" cy="78" r="34" className="bulb" />
      <path d="M430 78 q15 -28 30 0 q-15 28 -30 0" className="filament" />
      <text x="445" y="27" textAnchor="middle" className="bulb-label">{right}</text>
    </g>

    {ammeters && <>
      <g className="meter-node"><circle cx="205" cy="258" r="22" /><text x="205" y="264" textAnchor="middle">A1</text></g>
      <g className="meter-node"><circle cx="505" cy="258" r="22" /><text x="505" y="264" textAnchor="middle">A2</text></g>
    </>}

    {running ? <LiveElectrons path={path} /> : [250, 340, 430, 520].map((x) => <circle key={x} cx={x} cy={258} r="5" className="electron" />)}
  </svg>;
}

function ResistanceChange({ challenged, running }: { challenged: boolean; running: boolean }) {
  const path = "M135 258 H555 V78 H135 V258";
  return <svg viewBox="0 0 700 330" className="circuit" aria-label="series circuit showing a resistance change">
    <SvgDefs />
    <path d="M135 78 H555 V258 H135 Z" className="wire" />
    <Battery />
    <line x1="135" y1="78" x2="135" y2="135" className="wire" />
    <line x1="135" y1="195" x2="135" y2="258" className="wire" />
    <g className="resistor-node"><rect x="265" y="55" width="110" height="46" rx="10" /><text x="320" y="84" textAnchor="middle">15Ω</text></g>
    {challenged && <g className="resistor-node secondary-resistor"><rect x="410" y="55" width="110" height="46" rx="10" /><text x="465" y="84" textAnchor="middle">+15Ω</text></g>}
    {!challenged && <text x="465" y="84" textAnchor="middle" className="circuit-hint">experiment slot</text>}
    {running ? <LiveElectrons path={path} /> : [250, 340, 430, 520].map((x) => <circle key={x} cx={x} cy={258} r="5" className="electron" />)}
  </svg>;
}

function ParallelBranches({ running }: { running: boolean }) {
  return <svg viewBox="0 0 700 330" className="circuit" aria-label="parallel circuit with unequal branches">
    <SvgDefs />
    <path d="M135 70 H555 V260 H135 Z" className="wire" />
    <Battery />
    <line x1="135" y1="70" x2="135" y2="135" className="wire" />
    <line x1="135" y1="195" x2="135" y2="260" className="wire" />
    <path d="M220 70 V260" className="wire branch-wire" />
    <path d="M470 70 V260" className="wire branch-wire" />
    <g className="resistor-node"><rect x="196" y="115" width="48" height="90" rx="10" /><text x="220" y="164" textAnchor="middle" transform="rotate(-90 220 164)">15Ω</text></g>
    <g className="resistor-node"><rect x="446" y="115" width="48" height="90" rx="10" /><text x="470" y="164" textAnchor="middle" transform="rotate(-90 470 164)">30Ω</text></g>
    <text x="220" y="44" textAnchor="middle" className="branch-label">A</text>
    <text x="470" y="44" textAnchor="middle" className="branch-label">B</text>
    {running && <>
      <LiveElectrons path="M135 260 H220 V70 H135 V260" />
      {[0, 0.33, 0.66].map((delay, i) => <circle key={`b${i}`} r="5" className="electron electron-live electron-slow"><animateMotion dur="5.4s" begin={`${delay * -5.4}s`} repeatCount="indefinite" path="M135 260 H470 V70 H135 V260" /></circle>)}
    </>}
  </svg>;
}

function StemScene({ variant, challenged, running }: { variant: string; challenged: boolean; running: boolean }) {
  const scenes: Record<string, { eyebrow: string; title: string; primary: string; secondary: string; chips: string[] }> = {
    code_trace: { eyebrow: "PROGRAM STATE", title: "Assignment timeline", primary: "x = 3  →  y = x  →  x = 5", secondary: challenged ? "STATE  { x: 5, y: 3 }" : "Does y follow x?", chips: ["SEQUENTIAL", "MEMORY", "TRACE"] },
    loop_trace: { eyebrow: "CONTROL FLOW", title: "Range boundary scanner", primary: "range(1, 4)", secondary: challenged ? "1  →  2  →  3  →  STOP" : "How many iterations?", chips: ["START 1", "STOP 4", "HALF-OPEN"] },
    database_query: { eyebrow: "QUERY ENGINE", title: "Boolean precedence", primary: "active AND premium OR trial", secondary: challenged ? "AND resolves before OR" : "Where do parentheses change the result?", chips: ["4 ROWS", "AND", "OR"] },
    ai_matrix: { eyebrow: "MODEL AUDIT", title: "Accuracy under imbalance", primary: "990 healthy · 10 sick", secondary: challenged ? "99% ACCURACY  ·  0% RECALL" : "Can one metric hide failure?", chips: ["TP 0", "TN 990", "FN 10"] },
    beam_reactions: { eyebrow: "STRUCTURAL MODEL", title: "Off-center point load", primary: "▲────↓──────▲", secondary: challenged ? "Rₗ 6.67 kN  ·  Rᵣ 3.33 kN" : "Which support reacts more?", chips: ["ΣF = 0", "ΣM = 0", "6 m"] },
    stress_compare: { eyebrow: "MATERIAL RESPONSE", title: "Equal force, unequal area", primary: "20 kN  →  ▯  vs  ▮", secondary: challenged ? "σthin 100  ·  σthick 50" : "Force is not stress", chips: ["σ = F/A", "200 mm²", "400 mm²"] },
    design_matrix: { eyebrow: "DESIGN REVIEW", title: "Criteria × constraints", primary: "A: 100 strength / 130 cost", secondary: challenged ? "B passes both hard constraints" : "B: 85 strength / 90 cost", chips: ["BUDGET 100", "MIN 80", "FEASIBLE"] },
    optimization: { eyebrow: "TRADE-OFF ENGINE", title: "Multi-objective optimizer", primary: "SPEED  ×  COST  ×  RELIABILITY", secondary: challenged ? "BALANCED B  ·  SCORE 0.83" : "Which objective should dominate?", chips: ["⅓ SPEED", "⅓ COST", "⅓ RELIABILITY"] },
    equation_balance: { eyebrow: "SYMBOLIC CHECK", title: "Preserve both sides", primary: "2(x + 3) = 14", secondary: challenged ? "x = 4  →  14 = 14" : "Distribute or divide—never teleport", chips: ["EQUALITY", "DISTRIBUTE", "SUBSTITUTE"] },
    function_map: { eyebrow: "MAPPING TEST", title: "One input, one output", primary: "2  →  5   and   2  →  7", secondary: challenged ? "CONFLICT DETECTED AT INPUT 2" : "Is this relation a function?", chips: ["4 PAIRS", "INPUT 2", "2 OUTPUTS"] },
    ratio_graph: { eyebrow: "RATIO SCANNER", title: "Constant ratio test", primary: "(1,3)  (2,5)  (3,7)", secondary: challenged ? "3.00  →  2.50  →  2.33" : "Increasing ≠ proportional", chips: ["y/x", "LINEAR", "NOT THROUGH 0"] },
    logic_test: { eyebrow: "LOGIC LAB", title: "Converse counterexample", primary: "4 | n  ⇒  n is even", secondary: challenged ? "n = 6  ·  EVEN  ·  NOT ÷4" : "Does even ⇒ divisible by 4?", chips: ["IF–THEN", "CONVERSE", "COUNTEREXAMPLE"] },
  };
  const scene = scenes[variant] || scenes.code_trace;
  return <div className={`stem-scene ${running ? "running" : ""}`}>
    <div className="stem-scene-grid" />
    <div className="stem-scene-orbit"><i /><i /><i /></div>
    <span className="stem-scene-eyebrow">{scene.eyebrow}</span>
    <h3>{scene.title}</h3>
    <strong>{scene.primary}</strong>
    <p>{scene.secondary}</p>
    <div>{scene.chips.map((chip) => <span key={chip}>{chip}</span>)}</div>
  </div>;
}

export default function Circuit({
  swapped = false,
  running = false,
  scanning = false,
  variant = "series_bulbs",
}: CircuitProps) {
  const challenged = swapped || running;
  const isPhysics = ["series_bulbs", "resistance_change", "parallel_branches", "ammeter_series"].includes(variant);
  const status = variant === "parallel_branches" ? "Parallel branch environment" : variant === "resistance_change" ? "Resistance intervention" : variant === "ammeter_series" ? "Dual ammeter environment" : swapped ? "Diagnostic counterexample" : "Baseline circuit";
  const mode = variant === "parallel_branches" ? "9V · PARALLEL" : "9V · SERIES";

  if (!isPhysics) return (
    <div className={`circuit-shell stem-shell ${running ? "running" : ""} ${swapped ? "swapped" : ""}`}>
      <div className="circuit-status-row"><span className="status-dot" /><span>{challenged ? "EVIDENCE ENGINE ACTIVE" : "DIAGNOSTIC ENVIRONMENT"}</span><b>DETERMINISTIC</b></div>
      <StemScene variant={variant} challenged={challenged} running={running} />
      {scanning && <div className="scan-overlay" aria-live="polite"><div className="scan-line" /><div className="scan-copy"><span>COGNITIVE TRACE ACTIVE</span><b>SCANNING MENTAL MODEL...</b></div></div>}
      <div className="circuit-caption"><span><b>Domain</b> STEM</span><span><b>AI role</b> reasoning</span><span><b>Truth</b> computed</span><span><b>Mode</b> explainable</span></div>
    </div>
  );

  return (
    <div className={`circuit-shell ${running ? "running" : ""} ${swapped ? "swapped" : ""}`}>
      <div className="circuit-status-row"><span className="status-dot" /><span>{status}</span><b>{mode}</b></div>
      {variant === "parallel_branches" ? <ParallelBranches running={running} /> : variant === "resistance_change" ? <ResistanceChange challenged={challenged} running={running} /> : <SeriesBulbs swapped={swapped && variant === "series_bulbs"} running={running} ammeters={variant === "ammeter_series"} />}

      {scanning && <div className="scan-overlay" aria-live="polite"><div className="scan-line" /><div className="scan-copy"><span>COGNITIVE TRACE ACTIVE</span><b>SCANNING MENTAL MODEL...</b></div></div>}

      <div className="circuit-caption">
        <span><b>Battery</b> 9V</span>
        {variant === "parallel_branches" ? <><span><b>Branch A</b> 15Ω</span><span><b>Branch B</b> 30Ω</span><span><b>Mode</b> parallel</span></> : variant === "resistance_change" ? <><span><b>R1</b> 15Ω</span><span><b>R2</b> {challenged ? "15Ω" : "—"}</span><span><b>Mode</b> series</span></> : variant === "ammeter_series" ? <><span><b>A1</b> before</span><span><b>A2</b> after</span><span><b>Mode</b> ideal series</span></> : <><span><b>Bulb A</b> 15Ω</span><span><b>Bulb B</b> 15Ω</span><span><b>Mode</b> ideal series</span></>}
      </div>
    </div>
  );
}
