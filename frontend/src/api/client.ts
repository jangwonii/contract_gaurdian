import type { AnalysisResult } from "../types";

const API_BASE = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

export async function uploadDocument(file: File): Promise<{ documentId: string }> {
  const formData = new FormData();
  formData.append("file", file);

  const res = await fetch(`${API_BASE}/api/documents`, {
    method: "POST",
    body: formData,
  });

  if (!res.ok) {
    throw new Error("업로드 실패");
  }

  return res.json();
}

export async function triggerAnalysis(documentId: string): Promise<AnalysisResult> {
  const res = await fetch(`${API_BASE}/api/documents/${documentId}/analyze`, {
    method: "POST",
  });
  if (!res.ok) {
    throw new Error("분석 요청 실패");
  }
  return res.json();
}

export async function fetchResult(documentId: string): Promise<AnalysisResult> {
  const res = await fetch(`${API_BASE}/api/documents/${documentId}/result`);
  if (!res.ok) {
    throw new Error("결과 조회 실패");
  }
  return res.json();
}
