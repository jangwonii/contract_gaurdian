export interface ClauseRisk {
  score: number;
  level: "low" | "medium" | "high" | string;
  explanation: string;
}

export interface Clause {
  id: string;
  raw_text: string;
  summary?: string;
  category?: string;
  reasoning?: string;
  risk: ClauseRisk;
}

export interface AnalysisResult {
  document_id: string;
  clauses: Clause[];
  overall_risk_score: number;
  overall_risk_level?: string;
  contract_type?: string;
  auto_contract_type?: string;
  created_at?: string;
}

export interface DocumentStatus {
  document_id: string;
  stage: string;
  progress: number;
  message: string;
}

export interface ClauseImprovement {
  clauseId: string;
  suggestion: string;
  rationale: string;
  risk_delta?: number;
}
