import { useState } from "react";
import { suggestImprovement } from "../api/client";
import type { Clause, ClauseImprovement } from "../types";

type Props = {
  clauses: Clause[];
  sortByRisk?: "desc" | "asc";
  documentId?: string | null;
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

const ClauseList = ({ clauses, sortByRisk = "desc", documentId }: Props) => {
  if (!clauses.length) {
    return <p className="muted">분석된 조항이 없습니다.</p>;
  }

  const [suggestions, setSuggestions] = useState<Record<string, ClauseImprovement>>({});
  const [loadingId, setLoadingId] = useState<string | null>(null);
  const [errorId, setErrorId] = useState<string | null>(null);

  const handleSuggest = async (clause: Clause) => {
    if (!documentId) return;
    setLoadingId(clause.id);
    setErrorId(null);
    try {
      const data = await suggestImprovement(documentId, clause.id, clause.raw_text);
      setSuggestions((prev) => ({ ...prev, [clause.id]: data }));
    } catch (e) {
      setErrorId(clause.id);
    } finally {
      setLoadingId(null);
    }
  };

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
          {clause.reasoning && (
            <p className="muted">Agent 메모: {clause.reasoning}</p>
          )}
          <div className="clause-risk">
            <p className="label">위험 설명</p>
            <p>{clause.risk?.explanation ?? "정보 부족"}</p>
            <div className="meter">
              <div className={riskBarTone(clause.risk?.level)} style={{ width: `${clause.risk?.score ?? 0}%` }} />
              <span className="score">{clause.risk?.score ?? 0}</span>
            </div>
          </div>
          {documentId && (
            <div className="actions" style={{ justifyContent: "flex-end" }}>
              <button className="ghost-btn" onClick={() => handleSuggest(clause)} disabled={loadingId === clause.id}>
                {loadingId === clause.id ? "수정안 생성 중..." : "수정안 제안"}
              </button>
            </div>
          )}
          {suggestions[clause.id] && (
            <div className="suggestion-box">
              <p className="label">제안된 수정안</p>
              <p className="clause-body">{suggestions[clause.id].suggestion}</p>
              <p className="muted">이유: {suggestions[clause.id].rationale || "제공되지 않음"}</p>
            </div>
          )}
          {errorId === clause.id && <p className="error-chip">수정안 생성 실패</p>}
        </article>
      ))}
    </div>
  );
};

export default ClauseList;
