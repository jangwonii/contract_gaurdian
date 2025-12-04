# Contract Guardian

LLM 기반 계약서 위험도 분석 에이전트 앱입니다. PDF/이미지를 업로드하면 OCR → 조항 분리 → LLM 요약/분류/위험 힌트 → RiskPolicy 점수화 → 결과 UI 및 보고서(PDF/Markdown) 다운로드까지 지원합니다.

## 구조
- `backend/` FastAPI: 파일 업로드, 분석 파이프라인, LLM Provider(OpenAI/HF/Dummy), OCR(EasyOCR/PDF 텍스트), RiskPolicy(일반/근로/임대), 보고서 생성.
- `frontend/` Vite + React: 업로드/분석 화면, 계약 유형 선택, 위험도 정렬, 보고서 다운로드 버튼.
- `data/` 업로드 파일 저장.
- `config/.env`(예상): 환경변수 템플릿 위치.

## 빠른 시작
1) 백엔드
```bash
cd backend
python -m venv .venv && .\.venv\Scripts\activate  # Windows 예시
pip install -r requirements.txt
# .env에 LLM 키 설정(또는 LLM_PROVIDER=dummy), OCR_LANGUAGE=ko+en 권장
uvicorn backend.main:app --reload --port 8000
```
2) 프론트엔드
```bash
cd frontend
npm install
npm run dev  # 기본 5173
```
3) 브라우저에서 파일 업로드 → 분석 결과와 보고서 다운로드 확인.

## 주요 엔드포인트
- `POST /api/documents` 파일 업로드
- `POST /api/documents/{id}/analyze` (body: `contract_type`) 분석 실행
- `GET /api/documents/{id}/result` 결과 조회
- `GET /api/documents/{id}/report?format=pdf|md` 보고서 다운로드

## 주의사항
- Windows에서 PDF 보고서 생성은 WeasyPrint 의존성(gtk/cairo/pango) 설치 필요. 실패 시 Markdown으로 폴백합니다.
- OCR 정확도를 위해 `OCR_LANGUAGE=ko+en` 설정과 EasyOCR 필수 패키지 설치가 필요합니다.
