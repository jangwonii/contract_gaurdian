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

export async function triggerAnalysis(documentId: string, contractType: string = "general"): Promise<AnalysisResult> {
  const res = await fetch(`${API_BASE}/api/documents/${documentId}/analyze`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ contract_type: contractType }),
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

export async function downloadReport(
  documentId: string,
  format: "pdf" | "md" = "pdf",
): Promise<{ blob: Blob; filename: string; contentType: string }> {
  const res = await fetch(`${API_BASE}/api/documents/${documentId}/report?format=${format}`);
  if (!res.ok) {
    throw new Error("보고서 다운로드 실패");
  }
  const contentType = res.headers.get("content-type") || "";
  const blob = await res.blob();
  const filename = contentType.includes("pdf") ? "report.pdf" : "report.md";
  return { blob, filename, contentType };
}
