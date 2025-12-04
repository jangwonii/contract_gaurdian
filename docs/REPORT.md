# Contract Guardian 보고서 (Draft)

## 1. 문제 정의
- 개인 사용자가 계약서(근로/임대/프리랜스 등)에서 위험 조항을 빠르게 파악하기 어렵다.
- 법률 자문이 아닌 **위험 신호 및 설명**을 제공하는 LLM 기반 에이전트 앱을 목표로 한다.

## 2. 시스템 개요
- 입력: PDF/이미지 계약서 업로드
- 처리 파이프라인: OCR → 조항 분리 → LLM 요약/분류/위험 힌트 → RiskPolicy 점수화 → 결과 저장
- 출력: 전체 위험 점수, 조항별 요약/카테고리/위험 설명

## 3. 아키텍처
- Frontend: Vite + React (한국어 UI), 업로드 화면 + 결과 대시보드
- Backend: FastAPI
  - Domain: `Document`, `Clause`, `ClauseRisk`, `AnalysisResult`, `User`
  - Application: `AnalysisFacade`, `OCRService`, `ClauseExtractor`, `LLMAgent`, `RiskAnalyzer`
  - Infrastructure: `TesseractOCRAdapter`, `DummyLLMProvider`/`OpenAILLMProvider`, `InMemoryRepository`
- 디자인 패턴: Facade(파이프라인 단일 진입점), Strategy(LLM Provider, RiskPolicy), Adapter(OCR/LLM/Storage)

## 4. 구현 상태 (2025-12-02)
- Backend: 엔드포인트 스켈레톤, DummyLLMProvider, 단순 조항 분리/점수화, InMemory 저장소
- Frontend: 업로드/분석/결과 화면 기본 UI, API 래퍼
- Config: `.env.example`, 기본 requirements
- Docs: ROADMAP 초안 작성

## 5. 실험/검증 계획
- DummyLLMProvider 기반 샘플 계약서로 end-to-end 실행
- 조항 분리/점수화 단위 테스트
- OpenAI Provider 연결 후 실제 모델 응답 검증 (비밀키는 .env 사용)

## 6. 한계 및 향후 계획
- OCR: PDF 페이지 처리, 한글 정확도 개선 필요
- LLM: 프롬프트 설계/출력 스키마 고정, 비용 제어 및 캐싱 필요
- RiskPolicy: 계약 유형별 정책 확장, 설명/점수 근거 명시
- 보안/프라이버시: 업로드 파일 보관 기간 설정, 익명화 가이드 제공

## 7. 사용 시 유의 사항
- 본 서비스는 법률 자문이 아니며, 위험 신호만 제공합니다.
- 개인정보를 포함한 민감한 계약서는 업로드 전 마스킹을 권장합니다.
