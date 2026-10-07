# 💄 BeautyAlpha

Early Beauty Trend & Investment Signal

크리에이터 언급 → 대중 확산 → 해외 확산 → 검색 관심 → 제품 경쟁력 → 관련 기업까지 연결해 초기 뷰티 트렌드를 탐색하는 Streamlit 대시보드입니다.

## 설치

```bash
pip install -r requirements.txt
```

## API 키 설정

두 개의 키가 필요합니다.

- `YOUTUBE_API_KEY`
- `OPENAI_API_KEY`

프로젝트 루트의 `.env` 파일에 넣거나, Streamlit을 쓰는 경우 `.streamlit/secrets.toml`에 넣습니다. 두 파일 모두 `.gitignore`에 포함되어 있으므로 커밋되지 않습니다.

```
YOUTUBE_API_KEY=...
OPENAI_API_KEY=...
```

## 실행

대시보드 실행:

```bash
py -m streamlit run app.py
```

전체 데이터 업데이트:

```bash
py run_pipeline.py
```

## 파이프라인

`run_pipeline.py`는 아래 스크립트를 순서대로 실행하며, 한 단계가 실패하면 중단합니다.

| 단계 | 스크립트 | 내용 | 주요 출력 |
| --- | --- | --- | --- |
| 1 | `all_creator_products.py` | YouTube 신규 영상 수집 + 제품 추출 | `all_product_results_60d.json` |
| 2 | `momentum_signal.py` | Momentum Signal 계산 | `momentum_signal.json` |
| 3 | `beauty_alpha_score.py` | Beauty Alpha Score 계산 | `beauty_alpha_top10.json` |
| 4 | `google_trends_global.py` | Google Trends 글로벌 분석 | `google_trends_global.json` |
| 5 | `company_exposure_score.py` | Company Exposure 계산 | `company_exposure_score.json` |
| 6 | `manufacturer_signal.py` | Manufacturer Signal 계산 | `manufacturer_signal.json` |
| 7 | `ai_research_commentary.py` | AI Research Commentary 업데이트 | `ai_research_commentary.json` |

파이프라인이 끝난 뒤 Streamlit 앱을 새로고침하면 최신 결과가 반영됩니다.
