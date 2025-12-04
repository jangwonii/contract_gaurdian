import { useEffect, useState } from "react";
import ClauseList from "../components/ClauseList";
import { fetchResult } from "../api/client";
import type { AnalysisResult } from "../types";

type Props = {
  documentId: string | null;
  initialResult?: AnalysisResult | null;
};

const riskLabel = (score: number) => {
  if (score >= 75) return "위험";
  if (score >= 50) return "주의";
  return "낮음";
};

const riskTone = (score: number) => {
  if (score >= 75) return "badge danger";
  if (score >= 50) return "badge warning";
  return "badge safe";
};

const ResultPage = ({ documentId, initialResult = null }: Props) => {
  const [result, setResult] = useState<AnalysisResult | null>(initialResult);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!documentId) return;
    setLoading(true);
    setError(null);
    fetchResult(documentId)
      .then(setResult)
      .catch(() => setError("결과를 불러오지 못했습니다. 잠시 후 다시 시도하세요."))
      .finally(() => setLoading(false));
  }, [documentId]);

  if (!documentId) {
    return (
      <section className="card result-card placeholder">
        <h2>2. 분석 결과</h2>
        <p className="muted">업로드 후 결과가 여기에 표시됩니다.</p>
      </section>
    );
  }

  if (loading && !result) {
    return (
      <section className="card result-card">
        <h2>2. 분석 결과</h2>
        <p className="muted">분석 중입니다...</p>
      </section>
    );
  }

  if (error) {
    return (
      <section className="card result-card">
        <h2>2. 분석 결과</h2>
        <p className="error-chip">{error}</p>
      </section>
    );
  }

  if (!result) {
    return null;
  }

  const score = Math.round(result.overall_risk_score ?? 0);

  return (
    <section className="card result-card">
      <div className="card-header">
        <p className="eyebrow">2. 분석 결과</p>
        <h2>위험도 요약</h2>
        <p className="muted">조항별 요약과 위험 점수를 한눈에 확인하세요.</p>
      </div>

      <div className="summary-panel">
        <div>
          <p className="label">전체 위험 점수</p>
          <div className="score-row">
            <span className="score">{score}</span>
            <span className={riskTone(score)}>{riskLabel(score)}</span>
          </div>
          <div className="meter">
            <div className="bar" style={{ width: `${score}%` }} />
          </div>
        </div>
        <div>
          <p className="label">조항 개수</p>
          <h3>{result.clauses?.length ?? 0}개</h3>
        </div>
      </div>

      <ClauseList clauses={result.clauses ?? []} />
    </section>
  );
};

export default ResultPage;
