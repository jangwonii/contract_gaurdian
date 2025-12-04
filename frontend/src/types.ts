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
  risk: ClauseRisk;
}

export interface AnalysisResult {
  document_id: string;
  clauses: Clause[];
  overall_risk_score: number;
  overall_risk_level?: string;
  contract_type?: string;
  created_at?: string;
}
