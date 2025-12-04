import { useEffect, useState } from "react";
import ClauseList from "../components/ClauseList";
import { downloadReport, fetchResult, fetchStatus } from "../api/client";
import type { AnalysisResult, DocumentStatus } from "../types";

type Props = {
  documentId: string | null;
  initialResult?: AnalysisResult | null;
  isAnalyzing?: boolean;
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

const ResultPage = ({ documentId, initialResult = null, isAnalyzing = false }: Props) => {
  const [result, setResult] = useState<AnalysisResult | null>(initialResult);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [sortOrder, setSortOrder] = useState<"desc" | "asc">("desc");
  const [downloading, setDownloading] = useState(false);
  const [status, setStatus] = useState<DocumentStatus | null>(null);

  useEffect(() => {
    let timer: number | null = null;
    if (documentId && isAnalyzing) {
      const poll = () => {
        fetchStatus(documentId)
          .then((s) => setStatus(s))
          .catch(() => null);
      };
      poll();
      timer = window.setInterval(poll, 1200);
    }
    if (documentId && !isAnalyzing) {
      setLoading(true);
      setError(null);
      fetchResult(documentId)
        .then(setResult)
        .catch(() => setError("결과를 불러오지 못했습니다. 잠시 후 다시 시도하세요."))
        .finally(() => setLoading(false));
    }
    return () => {
      if (timer) window.clearInterval(timer);
    };
  }, [documentId, isAnalyzing]);

  if (!documentId) {
    return (
      <section className="card result-card placeholder">
        <h2>2. 분석 결과</h2>
        <p className="muted">업로드 후 결과가 여기에 표시됩니다.</p>
      </section>
    );
  }

  if (isAnalyzing) {
    return (
      <section className="card result-card">
        <h2>2. 분석 결과</h2>
        <p className="muted">분석 중입니다... 잠시만 기다려주세요.</p>
        <div className="stage-list">
          {[
            { key: "extract", label: "문서 텍스트 추출 중..." },
            { key: "split", label: "조항 구조 파악 중..." },
            { key: "llm", label: "위험 패턴 스캔 중..." },
            { key: "risk", label: "법적 관점에서 평가 중..." },
            { key: "done", label: "완료" },
          ].map((st) => {
            const active = status?.stage === st.key;
            return (
              <div key={st.key} className={`stage-item ${active ? "active" : ""}`}>
                <span className="dot" />
                <span>{active ? status?.message || st.label : st.label}</span>
              </div>
            );
          })}
        </div>
        <div className="spinner" aria-label="loading" />
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

  const handleDownload = async () => {
    if (!documentId) return;
    setDownloading(true);
    try {
      const { blob, filename } = await downloadReport(documentId, "pdf");
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = filename;
      a.click();
      window.URL.revokeObjectURL(url);
    } catch (e) {
      setError("보고서 다운로드에 실패했습니다.");
    } finally {
      setDownloading(false);
    }
  };

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
            <div className={riskTone(score).replace("badge ", "bar ")} style={{ width: `${score}%` }} />
          </div>
        </div>
        <div>
          <p className="label">조항 개수</p>
          <h3>{result.clauses?.length ?? 0}개</h3>
        </div>
        <div>
          <p className="label">유형 추론</p>
          <p className="muted">Agent 추론: {result.auto_contract_type ?? "미확인"} / 선택: {result.contract_type ?? "general"}</p>
        </div>
      </div>

      <div className="actions" style={{ justifyContent: "space-between" }}>
        <button className="ghost-btn" onClick={handleDownload} disabled={!documentId || downloading}>
          {downloading ? "보고서 생성 중..." : "PDF 다운로드"}
        </button>
        <select className="select" value={sortOrder} onChange={(e) => setSortOrder(e.target.value as "desc" | "asc")}>
          <option value="desc">위험 점수 높은 순</option>
          <option value="asc">위험 점수 낮은 순</option>
        </select>
      </div>

      <ClauseList clauses={result.clauses ?? []} sortByRisk={sortOrder} documentId={documentId} />
    </section>
  );
};

export default ResultPage;
