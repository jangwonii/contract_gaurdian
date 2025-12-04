from __future__ import annotations

from datetime import datetime
from typing import Iterable

from backend.domain.models import AnalysisResult, Clause


def _badge(level: str) -> str:
    if level == "high":
        return "위험"
    if level == "medium":
        return "주의"
    return "낮음"


def render_report_md(result: AnalysisResult) -> str:
    lines: list[str] = []
    created = result.created_at if isinstance(result.created_at, datetime) else datetime.utcnow()
    lines.append(f"# Contract Guardian Report")
    lines.append("")
    lines.append(f"- 문서 ID: `{result.document_id}`")
    lines.append(f"- 계약 유형: `{result.contract_type}`")
    lines.append(f"- 생성 시각: {created.isoformat()} UTC")
    lines.append(f"- 전체 위험 점수: **{round(result.overall_risk_score)}**")
    lines.append("")
    lines.append("## 조항별 요약")
    lines.append("| 순번 | 위험 | 카테고리 | 요약 | 점수 | 설명 |")
    lines.append("| --- | --- | --- | --- | --- | --- |")
    for idx, clause in enumerate(result.clauses, start=1):
        level = _badge(clause.risk.level if clause.risk else "low")
        category = clause.category or "general"
        summary = (clause.summary or "").replace("\n", " ")
        explanation = (clause.risk.explanation if clause.risk else "").replace("\n", " ")
        score = clause.risk.score if clause.risk else 0
        lines.append(f"| {idx} | {level} | {category} | {summary} | {score} | {explanation} |")
    lines.append("")
    return "\n".join(lines)


def render_report_html(result: AnalysisResult) -> str:
    created = result.created_at if isinstance(result.created_at, datetime) else datetime.utcnow()
    rows: Iterable[str] = []
    row_list = []
    for idx, clause in enumerate(result.clauses, start=1):
        level = _badge(clause.risk.level if clause.risk else "low")
        category = clause.category or "general"
        summary = clause.summary or ""
        explanation = clause.risk.explanation if clause.risk else ""
        score = clause.risk.score if clause.risk else 0
        row_list.append(
            f"<tr><td>{idx}</td><td>{level}</td><td>{category}</td>"
            f"<td>{summary}</td><td>{score}</td><td>{explanation}</td></tr>"
        )
    rows = "\n".join(row_list)
    return f"""
<!doctype html>
<html lang="ko">
  <head>
    <meta charset="UTF-8" />
    <style>
      body {{ font-family: 'Noto Sans KR', 'Inter', sans-serif; padding: 24px; color: #0f172a; }}
      h1, h2 {{ margin-bottom: 8px; }}
      table {{ width: 100%; border-collapse: collapse; margin-top: 12px; }}
      th, td {{ border: 1px solid #e2e8f0; padding: 8px; font-size: 13px; }}
      th {{ background: #f8fafc; text-align: left; }}
      .meta {{ margin: 0 0 4px 0; color: #475569; }}
      .score {{ font-weight: 700; }}
    </style>
  </head>
  <body>
    <h1>Contract Guardian Report</h1>
    <p class="meta">문서 ID: <code>{result.document_id}</code></p>
    <p class="meta">계약 유형: <code>{result.contract_type}</code></p>
    <p class="meta">생성 시각: {created.isoformat()} UTC</p>
    <p class="meta score">전체 위험 점수: {round(result.overall_risk_score)}</p>
    <h2>조항별 요약</h2>
    <table>
      <thead>
        <tr><th>순번</th><th>위험</th><th>카테고리</th><th>요약</th><th>점수</th><th>설명</th></tr>
      </thead>
      <tbody>
        {rows}
      </tbody>
    </table>
  </body>
</html>
"""
