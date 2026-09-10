"use client";

export type GraphHypothesis = {
  id: string;
  name: string;
  probability: number;
};

type Props = {
  hypotheses: GraphHypothesis[];
  lang?: "en" | "ar";
};

const positions = [
  { left: "9%", top: "16%" },
  { right: "8%", top: "18%" },
  { left: "10%", bottom: "12%" },
  { right: "8%", bottom: "12%" },
];

export default function ModelGraph({ hypotheses, lang = "en" }: Props) {
  const top = hypotheses.slice(0, 4);

  return (
    <div className="model-graph" aria-label="mental model hypothesis map">
      <svg className="graph-lines" viewBox="0 0 500 300" preserveAspectRatio="none" aria-hidden="true">
        <line x1="250" y1="150" x2="90" y2="65" />
        <line x1="250" y1="150" x2="410" y2="70" />
        <line x1="250" y1="150" x2="95" y2="235" />
        <line x1="250" y1="150" x2="410" y2="232" />
      </svg>

      <div className="graph-core">
        <span>{lang === "ar" ? "النموذج الذهني" : "MENTAL MODEL"}</span>
        <b>{lang === "ar" ? "الطالب" : "STUDENT"}</b>
      </div>

      {top.map((h, index) => (
        <div
          key={h.id}
          className={`graph-node graph-node-${index + 1}`}
          style={{
            ...positions[index],
            opacity: Math.max(0.5, 0.42 + h.probability),
            transform: `scale(${0.9 + h.probability * 0.18})`,
          }}
        >
          <span>{h.name}</span>
          <strong>{Math.round(h.probability * 100)}%</strong>
        </div>
      ))}
    </div>
  );
}
