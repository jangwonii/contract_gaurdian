import { useState } from "react";
import ResultPage from "./pages/ResultPage";
import UploadPage from "./pages/UploadPage";
import type { AnalysisResult } from "./types";

function App() {
  const [documentId, setDocumentId] = useState<string | null>(null);
  const [analysis, setAnalysis] = useState<AnalysisResult | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [view, setView] = useState<"upload" | "result">("upload");

  const handleAnalyzed = (docId: string, result: AnalysisResult) => {
    setDocumentId(docId);
    setAnalysis(result);
    setIsAnalyzing(false);
    setView("result");
  };

  const handleAnalyzing = (docId: string) => {
    setDocumentId(docId);
    setAnalysis(null);
    setIsAnalyzing(true);
    setView("result");
  };

  const goToUpload = () => setView("upload");
  const goToResult = () => setView("result");

  return (
    <div className="app-shell">
      <header className="hero">
        <div>
          <p className="eyebrow">Contract Guardian</p>
          <h1>계약서 위험도 분석 에이전트</h1>
          <p className="lede">
            PDF/이미지를 업로드하면 조항 요약, 분류, 위험도를 자동으로 계산합니다. 법률 자문이 아니라 위험 신호를 제공하는 도구입니다.
          </p>
        </div>
        <div className="hero-pill">
          <span className="dot pulse" />
          <span>LLM 기반 자동 분석</span>
        </div>
      </header>

      <div className="nav-tabs">
        <button className={`tab-btn ${view === "upload" ? "active" : ""}`} onClick={goToUpload}>
          1. 업로드
        </button>
        <button className={`tab-btn ${view === "result" ? "active" : ""}`} onClick={goToResult} disabled={!documentId}>
          2. 분석 결과
        </button>
      </div>

      <main className="page-container">
        {view === "upload" && (
          <section className="page-panel show">
            <UploadPage onAnalyzed={handleAnalyzed} onAnalyzing={handleAnalyzing} />
          </section>
        )}
        {view === "result" && (
          <section className="page-panel show">
            <ResultPage documentId={documentId} initialResult={analysis} isAnalyzing={isAnalyzing} />
          </section>
        )}
      </main>
    </div>
  );
}

export default App;
