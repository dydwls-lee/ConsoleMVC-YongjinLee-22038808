"""Pure console text formatters.

Every function here takes plain data (dict/list/primitives) supplied by
a Controller and returns a display string. No business logic (status
transitions, stock/production calculations, storage access) lives
here — the View only formats what it is given.
"""

from __future__ import annotations

MAIN_MENU_OPTIONS = [
    (1, "시료 관리"),
    (2, "시료 주문"),
    (3, "주문 승인/거절"),
    (4, "모니터링"),
    (5, "생산라인 조회"),
    (6, "출고 처리"),
    (0, "종료"),
]


def render_main_menu(summary: dict) -> str:
    lines = [
        "=== 반도체 시료 생산주문관리 시스템 ===",
        f"등록 시료 수: {summary['sampleCount']}  |  총 재고: {summary['totalStock']}  |  "
        f"전체 주문 수: {summary['totalOrderCount']}  |  생산라인 대기: {summary['productionQueueLength']}",
        "-" * 40,
    ]
    lines += [f"{num}. {label}" for num, label in MAIN_MENU_OPTIONS]
    return "\n".join(lines)


def render_samples(samples: list[dict]) -> str:
    if not samples:
        return "등록된 시료가 없습니다."
    lines = ["ID       이름                 평균생산시간  수율   재고"]
    for s in samples:
        lines.append(
            f"{s['id']:<8} {s['name']:<20} {s['avgProductionTime']:<12} {s['yield']:<6} {s['stock']}"
        )
    return "\n".join(lines)


def render_orders(orders: list[dict]) -> str:
    if not orders:
        return "표시할 주문이 없습니다."
    lines = ["주문번호               시료ID  고객명       수량   상태        접수시각"]
    for o in orders:
        lines.append(
            f"{o['orderId']:<22} {o['sampleId']:<7} {o['customerName']:<12} "
            f"{o['quantity']:<6} {o['status']:<10} {o['createdAt']}"
        )
    return "\n".join(lines)


def render_status_counts(counts: dict) -> str:
    lines = ["=== 상태별 주문 수 (REJECTED 제외) ==="]
    lines += [f"{status}: {count}" for status, count in counts.items()]
    return "\n".join(lines)


def render_stock_status(rows: list[dict]) -> str:
    if not rows:
        return "등록된 시료가 없습니다."
    lines = ["ID       이름                 재고    수요     상태"]
    for r in rows:
        lines.append(f"{r['id']:<8} {r['name']:<20} {r['stock']:<7} {r['demand']:<8} {r['status']}")
    return "\n".join(lines)


def render_production_queue(current: dict | None, pending: list[dict]) -> str:
    lines = ["=== 생산 라인 현황 ==="]
    if current is None:
        lines.append("현재 생산 중인 작업이 없습니다.")
    else:
        lines.append(
            f"[생산중] 주문 {current['orderId']} / 시료 {current['sampleId']} / "
            f"실생산량 {current['actualQuantity']} / 총생산시간 {current['totalTime']}분"
        )
    lines.append(f"대기 큐 ({len(pending)}건):")
    for job in pending:
        lines.append(
            f"  - 주문 {job['orderId']} / 시료 {job['sampleId']} / "
            f"실생산량 {job['actualQuantity']} / 총생산시간 {job['totalTime']}분"
        )
    return "\n".join(lines)
