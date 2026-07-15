"""Pure console text formatters.

Every function here takes plain data (dict/list/primitives) supplied by
a Controller and returns a display string. No business logic (status
transitions, stock/production calculations, storage access) lives
here — the View only formats what it is given.
"""

from __future__ import annotations

import unicodedata

MAIN_MENU_OPTIONS = [
    (1, "시료 관리"),
    (2, "시료 주문"),
    (3, "주문 승인/거절"),
    (4, "모니터링"),
    (5, "생산라인 조회"),
    (6, "출고 처리"),
    (0, "종료"),
]


def _display_width(text: str) -> int:
    """Terminal column width of `text`, counting East Asian Wide/Fullwidth
    characters (e.g. Korean) as 2 columns instead of Python's default 1.
    """
    return sum(2 if unicodedata.east_asian_width(ch) in ("W", "F") else 1 for ch in text)


def _pad(text: str, width: int) -> str:
    """Left-justify `text` to `width` terminal columns (not `len(text)`
    characters), so columns stay aligned even when Korean and ASCII text
    are mixed within the same table.
    """
    return text + " " * max(width - _display_width(text), 0)


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
            f"{_pad(s['id'], 8)} {_pad(s['name'], 20)} "
            f"{_pad(str(s['avgProductionTime']), 12)} {_pad(str(s['yield']), 6)} {s['stock']}"
        )
    return "\n".join(lines)


def render_orders(orders: list[dict]) -> str:
    if not orders:
        return "표시할 주문이 없습니다."
    lines = ["주문번호               시료ID  고객명       수량   상태        접수시각"]
    for o in orders:
        lines.append(
            f"{_pad(o['orderId'], 22)} {_pad(o['sampleId'], 7)} {_pad(o['customerName'], 12)} "
            f"{_pad(str(o['quantity']), 6)} {_pad(o['status'], 10)} {o['createdAt']}"
        )
    return "\n".join(lines)


def render_status_counts(counts: dict) -> str:
    lines = ["=== 상태별 주문 수 (REJECTED 제외) ==="]
    lines += [f"{status}: {count}" for status, count in counts.items()]
    return "\n".join(lines)


def render_stock_status(rows: list[dict]) -> str:
    if not rows:
        return "등록된 시료가 없습니다."
    lines = [
        "(기준: 여유=재고>=수요 / 부족=0<재고<수요 / 고갈=재고=0, 수요=RESERVED+PRODUCING+CONFIRMED 주문 수량 합)",
        "ID       이름                 재고    수요     상태",
    ]
    for r in rows:
        lines.append(
            f"{_pad(r['id'], 8)} {_pad(r['name'], 20)} "
            f"{_pad(str(r['stock']), 7)} {_pad(str(r['demand']), 8)} {r['status']}"
        )
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
