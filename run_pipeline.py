import os
import sys
import time
import subprocess
from datetime import datetime

try:
    sys.stdout.reconfigure(
        encoding="utf-8",
        errors="replace"
    )

    sys.stderr.reconfigure(
        encoding="utf-8",
        errors="replace"
    )

except Exception:
    pass

# =========================================================
# BeautyAlpha 전체 파이프라인
# =========================================================

PIPELINE = [

    {
        "step": 1,
        "title": "YouTube 신규 영상 수집 + 제품 추출",
        "file": "all_creator_products.py"
    },

    {
        "step": 2,
        "title": "Momentum Signal 계산",
        "file": "momentum_signal.py"
    },

    {
        "step": 3,
        "title": "Brand Signal 계산",
        "file": "brand_signal.py"
    },

    {
        "step": 4,
        "title": "Beauty Alpha Score 계산",
        "file": "beauty_alpha_score.py"
    },

    {
        "step": 5,
        "title": "Google Trends 글로벌 분석",
        "file": "google_trends_global.py"
    },

    {
        "step": 6,
        "title": "Factor Grades 계산 + 기록 저장",
        "file": "factor_grades.py"
    },

    {
        "step": 7,
        "title": "Company Exposure 계산",
        "file": "company_exposure_score.py"
    },

    {
        "step": 8,
        "title": "Manufacturer Signal 계산",
        "file": "manufacturer_signal.py"
    },

    {
        "step": 9,
        "title": "AI Research Commentary 업데이트",
        "file": "ai_research_commentary.py"
    }
]


# =========================================================
# 한 개 스크립트 실행
# =========================================================

def run_script(
    step,
    title,
    filename
):

    print()
    print("=" * 110)

    print(
        f"[{step}/{len(PIPELINE)}] "
        f"{title}"
    )

    print("=" * 110)

    print(
        f"실행 파일: {filename}"
    )

    print()


    # -----------------------------------------------------
    # 파일 존재 여부 확인
    # -----------------------------------------------------

    if not os.path.exists(
        filename
    ):

        print(
            f"❌ 파일을 찾을 수 없습니다: "
            f"{filename}"
        )

        return False


    start_time = time.time()


    # -----------------------------------------------------
    # 현재 Python 실행기로 실행
    # -----------------------------------------------------

    result = subprocess.run(
        [
            sys.executable,
            filename
        ]
    )


    elapsed = (
        time.time()
        - start_time
    )


    # -----------------------------------------------------
    # 실패
    # -----------------------------------------------------

    if result.returncode != 0:

        print()
        print("=" * 110)

        print(
            f"❌ STEP {step} 실패"
        )

        print(
            f"{title}"
        )

        print(
            f"종료 코드: "
            f"{result.returncode}"
        )

        print("=" * 110)

        return False


    # -----------------------------------------------------
    # 성공
    # -----------------------------------------------------

    print()
    print(
        f"✅ STEP {step} 완료"
    )

    print(
        f"소요 시간: "
        f"{elapsed:.1f}초"
    )


    return True


# =========================================================
# 전체 실행
# =========================================================

def main():

    pipeline_start = (
        time.time()
    )

    started_at = (
        datetime.now()
        .strftime(
            "%Y-%m-%d %H:%M:%S"
        )
    )


    print()
    print("=" * 110)

    print(
        "💄 BeautyAlpha Full Update Pipeline"
    )

    print("=" * 110)

    print(
        f"시작 시간: "
        f"{started_at}"
    )

    print()

    print(
        "BeautyAlpha 전체 데이터를 업데이트합니다."
    )

    print(
        "기존 분석 영상과 AI 코멘트는 "
        "가능한 경우 캐시를 재사용합니다."
    )


    completed_steps = []


    # =====================================================
    # Pipeline 순차 실행
    # =====================================================

    for task in PIPELINE:

        success = run_script(

            step=task[
                "step"
            ],

            title=task[
                "title"
            ],

            filename=task[
                "file"
            ]
        )


        if not success:

            print()
            print("=" * 110)

            print(
                "❌ BeautyAlpha 업데이트 중단"
            )

            print("=" * 110)

            print(
                f"실패 단계: "
                f"{task['step']} "
                f"- "
                f"{task['title']}"
            )

            print()

            print(
                "위 오류를 해결한 뒤 "
                "다시 py run_pipeline.py 를 실행하세요."
            )

            return


        completed_steps.append(
            task[
                "title"
            ]
        )


    # =====================================================
    # 최종 완료
    # =====================================================

    pipeline_elapsed = (
        time.time()
        - pipeline_start
    )


    finished_at = (
        datetime.now()
        .strftime(
            "%Y-%m-%d %H:%M:%S"
        )
    )


    print()
    print()
    print("=" * 110)

    print(
        "🎉 BeautyAlpha 전체 업데이트 완료"
    )

    print("=" * 110)

    print(
        f"완료 단계: "
        f"{len(completed_steps)}"
        f"/"
        f"{len(PIPELINE)}"
    )

    print(
        f"전체 소요 시간: "
        f"{pipeline_elapsed / 60:.1f}분"
    )

    print(
        f"완료 시간: "
        f"{finished_at}"
    )


    print()
    print(
        "업데이트된 주요 파일:"
    )

    print(
        "• all_product_results_60d.json"
    )

    print(
        "• momentum_signal.json"
    )

    print(
        "• brand_signal.json"
    )

    print(
        "• beauty_alpha_top10.json"
    )

    print(
        "• google_trends_global.json"
    )

    print(
        "• factor_grades.json"
    )

    print(
        "• beauty_alpha_history.json"
    )

    print(
        "• company_exposure_score.json"
    )

    print(
        "• manufacturer_signal.json"
    )

    print(
        "• ai_research_commentary.json"
    )


    print()
    print(
        "이제 Streamlit 앱을 새로고침하면 "
        "최신 결과가 반영됩니다."
    )

    print()

    print(
        "앱 실행:"
    )

    print(
        "py -m streamlit run app.py"
    )


# =========================================================
# 실행
# =========================================================

if __name__ == "__main__":

    main()