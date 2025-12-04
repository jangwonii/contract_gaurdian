import { ChangeEvent, useRef, useState } from "react";
import { fetchResult, triggerAnalysis, uploadDocument } from "../api/client";
import type { AnalysisResult } from "../types";

type Props = {
  onAnalyzed: (documentId: string, result: AnalysisResult) => void;
};

const UploadPage = ({ onAnalyzed }: Props) => {
  const fileInputRef = useRef<HTMLInputElement | null>(null);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [status, setStatus] = useState<"idle" | "uploading" | "analyzing" | "done">("idle");
  const [error, setError] = useState<string | null>(null);
  const [lastDocumentId, setLastDocumentId] = useState<string | null>(null);

  const handleSelect = (event: ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      setSelectedFile(file);
      setError(null);
    }
  };

  const handleUpload = async () => {
    if (!selectedFile) {
      setError("파일을 선택해주세요.");
      return;
    }
    setStatus("uploading");
    setError(null);
    try {
      const { documentId } = await uploadDocument(selectedFile);
      setLastDocumentId(documentId);
      setStatus("analyzing");
      const result = await triggerAnalysis(documentId);
      onAnalyzed(documentId, result);
      setStatus("done");
    } catch (err) {
      console.error(err);
      setError("업로드 또는 분석에 실패했습니다.");
      setStatus("idle");
    }
  };

  const handleReFetch = async () => {
    if (!lastDocumentId) return;
    try {
      setStatus("analyzing");
      const latest = await fetchResult(lastDocumentId);
      onAnalyzed(lastDocumentId, latest);
      setStatus("done");
    } catch {
      // ignore refresh errors
      setStatus("idle");
    }
  };

  return (
    <section className="card upload-card">
      <div className="card-header">
        <p className="eyebrow">1. 업로드</p>
        <h2>계약서 파일 올리기</h2>
        <p className="muted">계약서 PDF 또는 이미지(JPG/PNG)를 올리면 위험도 분석을 진행합니다.</p>
      </div>

      <div
        className="dropzone"
        onClick={() => fileInputRef.current?.click()}
        role="button"
        tabIndex={0}
      >
        <input ref={fileInputRef} type="file" accept=".pdf,.png,.jpg,.jpeg" onChange={handleSelect} hidden />
        {selectedFile ? (
          <div>
            <p className="label">선택된 파일</p>
            <p className="filename">{selectedFile.name}</p>
          </div>
        ) : (
          <div>
            <p className="label">파일을 드래그하거나 클릭해 선택</p>
            <p className="muted">최대 20MB, 개인정보는 가급적 제거해주세요.</p>
          </div>
        )}
      </div>

      {error && <div className="error-chip">{error}</div>}

      <div className="actions">
        <button className="primary-btn" onClick={handleUpload} disabled={status === "uploading" || status === "analyzing"}>
          {status === "uploading" && "업로드 중..."}
          {status === "analyzing" && "분석 중..."}
          {status === "done" && "다시 분석하기"}
          {status === "idle" && "업로드 후 분석 시작"}
        </button>
        <button className="ghost-btn" onClick={handleReFetch} disabled={!selectedFile}>
          최신 결과 다시 불러오기
        </button>
      </div>

      <div className="status-line">
        <div className={`status-dot ${status}`} />
        <span>
          {status === "idle" && "대기 중"}
          {status === "uploading" && "서버로 파일을 전송 중..."}
          {status === "analyzing" && "OCR/LLM 분석을 실행 중..."}
          {status === "done" && "분석 완료"}
        </span>
      </div>
    </section>
  );
};

export default UploadPage;
