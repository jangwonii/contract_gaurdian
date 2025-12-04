import type { Clause } from "../types";

type Props = {
  clauses: Clause[];
  sortByRisk?: "desc" | "asc";
};

const riskTone = (level?: string) => {
  if (!level) return "badge neutral";
  if (level === "high") return "badge danger";
  if (level === "medium") return "badge warning";
  return "badge safe";
};

const riskLabel = (level?: string) => {
  if (!level) return "낮음";
  if (level === "high") return "위험";
  if (level === "medium") return "주의";
  return "낮음";
};

const riskBarTone = (level?: string) => {
  if (level === "high") return "bar danger";
  if (level === "medium") return "bar warning";
  if (level === "low") return "bar safe";
  return "bar";
};

const ClauseList = ({ clauses, sortByRisk = "desc" }: Props) => {
  if (!clauses.length) {
    return <p className="muted">분석된 조항이 없습니다.</p>;
  }

  const sorted = [...clauses].sort((a, b) => {
    const left = a.risk?.score ?? 0;
    const right = b.risk?.score ?? 0;
    return sortByRisk === "desc" ? right - left : left - right;
  });

  return (
    <div className="clause-grid">
      {sorted.map((clause) => (
        <article key={clause.id} className="clause-card">
          <div className="clause-head">
            <span className={riskTone(clause.risk?.level)}>{riskLabel(clause.risk?.level)}</span>
            <span className="pill outline">{clause.category ?? "미분류"}</span>
          </div>
          <p className="clause-title">{clause.summary ?? "요약이 없습니다."}</p>
          <p className="clause-body">{clause.raw_text}</p>
          <div className="clause-risk">
            <p className="label">위험 설명</p>
            <p>{clause.risk?.explanation ?? "정보 부족"}</p>
            <div className="meter">
              <div className={riskBarTone(clause.risk?.level)} style={{ width: `${clause.risk?.score ?? 0}%` }} />
              <span className="score">{clause.risk?.score ?? 0}</span>
            </div>
          </div>
        </article>
      ))}
    </div>
  );
};

export default ClauseList;
