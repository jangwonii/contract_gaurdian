# Contract Guardian 로드맵 (초안)

## 0. 초기 세팅
- [x] 프로젝트 구조 생성 (backend/frontend/docs/config/data)
- [x] AGENTS.md 기준 기본 스캐폴드 작성

## 1. Backend (FastAPI)
- [ ] 파일 업로드 엔드포인트 검증 & 에러 처리 강화
- [ ] OCR 실제 연동(pytesseract 설치, PDF → 이미지 변환)
- [ ] 조항 분리 로직 개선(번호 패턴/머리말 학습)
- [ ] LLM Provider 실제 호출(OpenAI) + Prompt 템플릿 정교화
- [ ] RiskPolicy 전략 패턴으로 계약 유형별 점수화
- [ ] 간단한 저장소를 DB/파일 혼합 구조로 확장

## 2. Frontend (Vite + React)
- [ ] API 상태 로딩/에러 UI 개선, 토스트 추가
- [ ] 업로드 진행률/분석 단계별 뱃지 표시
- [ ] 결과 필터/정렬, 검색(카테고리/위험도)
- [ ] 모바일 대응 세부 튜닝
- [ ] PDF 리포트 다운로드 버튼 추가

## 3. 통합/운영
- [ ] .env 템플릿 정리 및 설정 가이드 추가
- [ ] docker-compose 또는 devcontainer 초안
- [ ] 샘플 계약서 및 e2e 실행 스크립트 작성

## 4. 리포트/테스트
- [ ] 간단한 단위 테스트 (조항 분리, 리스크 스코어러)
- [ ] DummyLLMProvider 기반 통합 테스트
- [ ] REPORT.md에 구조/제약/한계/향후 계획 정리
