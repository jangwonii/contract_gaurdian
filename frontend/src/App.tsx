import { useState } from "react";
import ResultPage from "./pages/ResultPage";
import UploadPage from "./pages/UploadPage";
import type { AnalysisResult } from "./types";

function App() {
  const [documentId, setDocumentId] = useState<string | null>(null);
  const [analysis, setAnalysis] = useState<AnalysisResult | null>(null);

  const handleAnalyzed = (docId: string, result: AnalysisResult) => {
    setDocumentId(docId);
    setAnalysis(result);
  };

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

      <main className="content-grid">
        <UploadPage onAnalyzed={handleAnalyzed} />
        <ResultPage documentId={documentId} initialResult={analysis} />
      </main>
    </div>
  );
}

export default App;
