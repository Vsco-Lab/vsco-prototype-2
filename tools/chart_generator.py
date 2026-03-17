"""보고서용 시각화 차트 자동 생성"""
import os
import matplotlib.pyplot as plt
import matplotlib
import numpy as np

matplotlib.rcParams['font.family'] = 'AppleGothic'
matplotlib.rcParams['axes.unicode_minus'] = False

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "outputs", "charts")
os.makedirs(OUTPUT_DIR, exist_ok=True)


def generate_all_charts() -> list:
    """보고서에 삽입할 전체 차트 생성, 파일 경로 리스트 반환"""
    paths = []
    paths.append(chart_ev_sales_trend())
    paths.append(chart_ess_market_growth())
    paths.append(chart_market_share_comparison())
    paths.append(chart_financial_comparison())
    paths.append(chart_swot_matrix_lg())
    paths.append(chart_swot_matrix_catl())
    paths.append(chart_swot_radar())
    return paths


def chart_ev_sales_trend() -> str:
    """글로벌 전기차 판매량 추이"""
    fig, ax = plt.subplots(figsize=(9, 5))
    years = ["2023", "2024", "2025", "2026(E)"]
    sales = [1400, 1700, 2100, 2429]
    growth = [None, 21, 24, 15]

    bars = ax.bar(years, sales, color=["#0077b6", "#0077b6", "#0077b6", "#90caf9"],
                  width=0.45, edgecolor="white", linewidth=1.5)
    for bar, val in zip(bars, sales):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 50,
                f"{val:,}만 대", ha="center", fontweight="bold", fontsize=10)

    ax2 = ax.twinx()
    valid_idx = [i for i, g in enumerate(growth) if g is not None]
    valid_years = [years[i] for i in valid_idx]
    valid_growth = [growth[i] for i in valid_idx]
    ax2.plot(valid_years, valid_growth, color="#e85d04", marker="o",
             linewidth=2.5, markersize=9, zorder=5)
    for yr, g in zip(valid_years, valid_growth):
        ax2.annotate(f"+{g}%", (yr, g), textcoords="offset points",
                    xytext=(0, 14), ha="center", color="#e85d04",
                    fontweight="bold", fontsize=10)

    ax.set_title("글로벌 전기차 판매량 추이", fontsize=15, fontweight="bold", pad=18)
    ax.set_ylabel("판매량 (만 대)", fontsize=11)
    ax2.set_ylabel("전년 대비 성장률 (%)", color="#e85d04", fontsize=11)
    ax.set_ylim(0, 3200)
    ax2.set_ylim(0, 40)
    ax.grid(axis="y", alpha=0.2)
    ax.legend(["판매량"], loc="upper left")
    ax2.legend(["성장률"], loc="upper right")

    path = os.path.join(OUTPUT_DIR, "ev_sales_trend.png")
    plt.tight_layout()
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    return path


def chart_ess_market_growth() -> str:
    """ESS 시장 규모 성장 전망"""
    fig, ax = plt.subplots(figsize=(8, 4.5))
    years = ["2024", "2025", "2026(E)", "2030(E)"]
    gwh = [235, 290, 359, 750]

    bars = ax.bar(years, gwh, color=["#2d6a4f", "#2d6a4f", "#2d6a4f", "#a7d8a0"],
                  width=0.5, edgecolor="white", linewidth=1.5)
    for bar, val in zip(bars, gwh):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 10,
                f"{val} GWh", ha="center", fontweight="bold", fontsize=11)

    ax.set_title("글로벌 ESS 시장 규모 전망", fontsize=14, fontweight="bold", pad=15)
    ax.set_ylabel("설치 용량 (GWh)")
    ax.set_ylim(0, 900)
    ax.grid(axis="y", alpha=0.3)

    path = os.path.join(OUTPUT_DIR, "ess_market_growth.png")
    plt.tight_layout()
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    return path


def chart_market_share_comparison() -> str:
    """LG에너지솔루션 vs CATL 시장점유율 비교"""
    fig, ax = plt.subplots(figsize=(8, 4.5))
    years = ["2023", "2024", "2025"]
    catl = [36.8, 38.0, 39.2]
    lg = [15, 14, 13]

    x = np.arange(len(years))
    width = 0.3
    bars1 = ax.bar(x - width/2, catl, width, label="CATL", color="#e85d04")
    bars2 = ax.bar(x + width/2, lg, width, label="LG에너지솔루션", color="#0077b6")

    for bar, val in zip(bars1, catl):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
                f"{val}%", ha="center", fontweight="bold", fontsize=10, color="#e85d04")
    for bar, val in zip(bars2, lg):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
                f"{val}%", ha="center", fontweight="bold", fontsize=10, color="#0077b6")

    ax.set_title("글로벌 EV 배터리 시장점유율 비교", fontsize=14, fontweight="bold", pad=15)
    ax.set_ylabel("점유율 (%)")
    ax.set_xticks(x)
    ax.set_xticklabels(years)
    ax.set_ylim(0, 50)
    ax.legend()
    ax.grid(axis="y", alpha=0.3)

    path = os.path.join(OUTPUT_DIR, "market_share_comparison.png")
    plt.tight_layout()
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    return path


def chart_financial_comparison() -> str:
    """양사 주요 재무 지표 비교"""
    fig, axes = plt.subplots(1, 2, figsize=(10, 4.5))

    # 매출 비교
    ax = axes[0]
    names = ["LG에너지솔루션", "CATL"]
    revenue = [23.7, 80]  # 조원
    bars = ax.bar(names, revenue, color=["#0077b6", "#e85d04"], width=0.4)
    for bar, val in zip(bars, revenue):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
                f"{val}조원", ha="center", fontweight="bold", fontsize=11)
    ax.set_title("2025 매출", fontsize=13, fontweight="bold")
    ax.set_ylabel("매출 (조원)")
    ax.set_ylim(0, 100)
    ax.grid(axis="y", alpha=0.3)

    # R&D 비교
    ax = axes[1]
    rnd = [1.3, 4.8]
    bars = ax.bar(names, rnd, color=["#0077b6", "#e85d04"], width=0.4)
    for bar, val in zip(bars, rnd):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1,
                f"{val}조원", ha="center", fontweight="bold", fontsize=11)
    ax.set_title("R&D 투자", fontsize=13, fontweight="bold")
    ax.set_ylabel("투자액 (조원)")
    ax.set_ylim(0, 6)
    ax.grid(axis="y", alpha=0.3)

    fig.suptitle("양사 주요 재무 지표 비교 (2025)", fontsize=14, fontweight="bold", y=1.02)
    path = os.path.join(OUTPUT_DIR, "financial_comparison.png")
    plt.tight_layout()
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    return path


def _draw_swot_matrix(title, s_items, w_items, o_items, t_items, filename):
    """SWOT 2x2 매트릭스 시각화 — 깔끔한 카드 스타일"""
    fig = plt.figure(figsize=(12, 9))
    fig.patch.set_facecolor("white")

    # 타이틀
    fig.text(0.5, 0.96, f"{title}의 SWOT 분석", ha="center", va="top",
             fontsize=18, fontweight="bold", color="#1a1a2e")

    # 내부/외부 구분 라벨
    fig.text(0.5, 0.915, "내 부 요 인", ha="center", va="top",
             fontsize=10, color="#999999", fontweight="bold")
    fig.text(0.5, 0.46, "외 부 요 인", ha="center", va="top",
             fontsize=10, color="#999999", fontweight="bold")

    quadrants = [
        # (position, letter, label, items, bg_color, accent_color, icon)
        ([0.05, 0.50, 0.43, 0.40], "S", "강점 Strength", s_items, "#e8f5e9", "#2e7d32"),
        ([0.52, 0.50, 0.43, 0.40], "W", "약점 Weakness", w_items, "#fce4ec", "#c62828"),
        ([0.05, 0.06, 0.43, 0.40], "O", "기회 Opportunity", o_items, "#e3f2fd", "#1565c0"),
        ([0.52, 0.06, 0.43, 0.40], "T", "위협 Threat", t_items, "#fff3e0", "#e65100"),
    ]

    for pos, letter, label, items, bg_color, accent in quadrants:
        ax = fig.add_axes(pos)
        ax.set_facecolor(bg_color)
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.set_xticks([])
        ax.set_yticks([])

        # 왼쪽 악센트 바
        ax.axvline(x=0, color=accent, linewidth=6)

        # 큰 글자 + 라벨
        ax.text(0.06, 0.90, letter, fontsize=28, fontweight="bold",
                color=accent, alpha=0.3, transform=ax.transAxes, va="top")
        ax.text(0.14, 0.92, label, fontsize=12, fontweight="bold",
                color=accent, transform=ax.transAxes, va="top")

        # 구분선
        ax.plot([0.05, 0.95], [0.82, 0.82], color=accent, alpha=0.3,
                linewidth=1, transform=ax.transAxes)

        # 항목들
        for i, item in enumerate(items):
            y = 0.72 - i * 0.18
            ax.text(0.08, y, "-", fontsize=10, color=accent,
                    transform=ax.transAxes, va="top")
            ax.text(0.14, y, item, fontsize=10, color="#333333",
                    transform=ax.transAxes, va="top")

        # 외곽선
        for spine in ax.spines.values():
            spine.set_visible(False)
        ax.patch.set_linewidth(0)

        # 둥근 사각형 효과 (테두리)
        from matplotlib.patches import FancyBboxPatch
        border = FancyBboxPatch((0.002, 0.002), 0.996, 0.996,
                                boxstyle="round,pad=0.02",
                                facecolor="none", edgecolor="#dee2e6",
                                linewidth=1.5, transform=ax.transAxes)
        ax.add_patch(border)

    path = os.path.join(OUTPUT_DIR, filename)
    plt.savefig(path, dpi=150, bbox_inches="tight", facecolor="white")
    plt.close()
    return path


def chart_swot_matrix_lg() -> str:
    """LG에너지솔루션 SWOT 매트릭스"""
    return _draw_swot_matrix(
        title="LG에너지솔루션",
        s_items=[
            "하이니켈 삼원계 기술 리더십",
            "북미 현지 생산 (IRA 수혜)",
            "글로벌 OEM 파트너십",
            "46시리즈 원통형 양산 개시",
        ],
        w_items=[
            "CATL 대비 규모 열위 (1/3~1/4)",
            "LFP 원가 경쟁력 부족",
            "나트륨이온 기술 후발",
            "북미 합작 이탈 → 가동률 부담",
        ],
        o_items=[
            "ESS 시장 고성장 (2030년 750GWh)",
            "AI 데이터센터용 ESS 수요 폭발",
            "로봇·UAM 신시장 성장",
            "중국 기업 미국 차단 반사 수혜",
        ],
        t_items=[
            "IRA 축소 시 수익성 5~6%p 하락",
            "중국 기업 글로벌 가격 공세",
            "LFP 확대 → 삼원계 수요 둔화",
            "전기차 캐즘 장기화",
        ],
        filename="swot_matrix_lg.png",
    )


def chart_swot_matrix_catl() -> str:
    """CATL SWOT 매트릭스"""
    return _draw_swot_matrix(
        title="CATL",
        s_items=[
            "글로벌 1위 (EV 39.2%, ESS 30.4%)",
            "압도적 규모 (772GWh 캐파)",
            "LFP·나트륨이온 원가 경쟁력",
            "R&D 투자 ~4.8조원 (업계 최대)",
        ],
        w_items=[
            "미국 시장 직접 진출 차단",
            "내수 의존도 높음 (69.4%)",
            "공급 과잉 리스크 (1,100GWh)",
            "중국 정부 정책 의존도",
        ],
        o_items=[
            "나트륨이온 2026 상용화 → 반값 EV",
            "유럽·동남아·아프리카 확장",
            "배터리스왑 BaaS 모델 선점",
            "응축물질 배터리 항공 시장",
        ],
        t_items=[
            "미중 기술 패권 경쟁 격화",
            "EU 중국산 EV 관세 (38.1%)",
            "기술 수출 통제 → 라이선싱 제약",
            "EU 탄소발자국 규제",
        ],
        filename="swot_matrix_catl.png",
    )


def chart_swot_radar() -> str:
    """양사 경쟁력 레이더 차트"""
    categories = ["규모", "원가\n경쟁력", "기술\n다양성", "북미\n접근성", "ESS\n점유율", "R&D\n투자"]
    n = len(categories)

    lg_scores = [3, 4, 5, 9, 5, 4]
    catl_scores = [9, 8, 8, 2, 9, 8]

    angles = np.linspace(0, 2 * np.pi, n, endpoint=False).tolist()
    angles += angles[:1]
    lg_scores += lg_scores[:1]
    catl_scores += catl_scores[:1]

    fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))
    ax.plot(angles, lg_scores, "o-", linewidth=2, label="LG에너지솔루션", color="#0077b6")
    ax.fill(angles, lg_scores, alpha=0.15, color="#0077b6")
    ax.plot(angles, catl_scores, "o-", linewidth=2, label="CATL", color="#e85d04")
    ax.fill(angles, catl_scores, alpha=0.15, color="#e85d04")

    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(categories, fontsize=10)
    ax.set_ylim(0, 10)
    ax.set_yticks([2, 4, 6, 8, 10])
    ax.set_yticklabels(["2", "4", "6", "8", "10"], fontsize=8)
    ax.legend(loc="upper right", bbox_to_anchor=(1.2, 1.1))
    ax.set_title("양사 경쟁력 비교", fontsize=14, fontweight="bold", pad=20)

    path = os.path.join(OUTPUT_DIR, "swot_radar.png")
    plt.tight_layout()
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    return path


if __name__ == "__main__":
    paths = generate_all_charts()
    for p in paths:
        print(f"생성: {p}")
