from datetime import datetime

from app.main import App
from model.order import OrderStatus
from view.console_io import ConsoleIO


def run_with_inputs(app, inputs):
    responses = iter(inputs)
    printed = []
    app.io = ConsoleIO(print_func=printed.append, input_func=lambda _prompt: next(responses))
    app.run()
    return printed


def make_app():
    return App(clock=lambda: datetime(2026, 4, 16, 9, 0, 0))


def test_full_flow_register_order_approve_and_release_with_sufficient_stock():
    app = make_app()

    # 1) 시료 등록 (등록 메뉴는 재고를 입력받지 않으므로 신규 시료는 항상 재고 0으로 시작한다)
    run_with_inputs(
        app,
        ["1", "1", "S-001", "웨이퍼", "0.5", "0.9", "0", "0"],
    )

    # data-persistence 연동 이전 단계이므로, 기존 재고가 있는 상황을 시뮬레이션하기 위해
    # 저장소에 직접 재고를 반영한다 (실제로는 dummy-data-generator/기존 데이터가 채워줄 값).
    sample = app.sample_repo.get("S-001")
    sample.stock = 50
    app.sample_repo.update(sample)

    # 2) 주문 접수 -> 승인(재고충분 -> CONFIRMED) -> 출고(RELEASE)
    printed = run_with_inputs(
        app,
        [
            "2", "1", "S-001", "삼성전자", "10", "0",
            "3", "2", "ORD-20260416-0001", "0",
            "6", "2", "ORD-20260416-0001", "0",
            "0",
        ],
    )

    order = app.order_repo.get("ORD-20260416-0001")
    assert order.status == OrderStatus.RELEASE
    assert app.sample_repo.get("S-001").stock == 40  # 50 - 10
    assert any("종료" in line for line in printed)


def test_insufficient_stock_routes_order_to_producing_queue():
    app = make_app()

    run_with_inputs(app, ["1", "1", "S-001", "웨이퍼", "2.0", "0.5", "0", "0"])

    printed = run_with_inputs(
        app,
        [
            "2", "1", "S-001", "고객사", "10", "0",  # 재고 0 -> 전량 부족분
            "3", "2", "ORD-20260416-0001", "Y", "0",  # 부족분 안내 -> Y로 재확인
            "5", "1", "0",
            "0",
        ],
    )

    order = app.order_repo.get("ORD-20260416-0001")
    assert order.status == OrderStatus.PRODUCING
    assert len(app.production_queue) == 1
    assert any("ORD-20260416-0001" in line for line in printed)
    # shortage=10, yield=0.5 -> actual_quantity=20, total_time=2.0*20=40.0
    assert any("부족분 10" in line and "실생산량 20" in line and "40.0" in line for line in printed)


def test_insufficient_stock_approval_declined_rejects_order_instead():
    """When the operator answers N to the shortage confirmation, the order
    must be REJECTED, not silently left RESERVED or forced to PRODUCING.
    """
    app = make_app()

    run_with_inputs(app, ["1", "1", "S-001", "웨이퍼", "2.0", "0.5", "0", "0"])

    printed = run_with_inputs(
        app,
        [
            "2", "1", "S-001", "고객사", "10", "0",
            "3", "2", "ORD-20260416-0001", "N", "0",
            "0",
        ],
    )

    order = app.order_repo.get("ORD-20260416-0001")
    assert order.status == OrderStatus.REJECTED
    assert len(app.production_queue) == 0
    assert any("거절 처리 완료" in line for line in printed)


def test_sufficient_stock_approval_skips_confirmation_prompt():
    """The shortage confirmation step only applies to the PRODUCING branch
    — when stock is sufficient, approval must remain a single-step action
    (no extra Y/N prompt), matching the existing sufficient-stock test's
    input sequence.
    """
    app = make_app()

    run_with_inputs(app, ["1", "1", "S-001", "웨이퍼", "0.5", "0.9", "0", "0"])
    sample = app.sample_repo.get("S-001")
    sample.stock = 50
    app.sample_repo.update(sample)

    printed = run_with_inputs(
        app,
        [
            "2", "1", "S-001", "고객사", "10", "0",
            "3", "2", "ORD-20260416-0001", "0",
            "0",
        ],
    )

    order = app.order_repo.get("ORD-20260416-0001")
    assert order.status == OrderStatus.CONFIRMED
    assert any("승인 처리 완료: CONFIRMED" in line for line in printed)


def test_invalid_menu_choice_shows_error_and_does_not_crash():
    app = make_app()

    printed = run_with_inputs(app, ["9", "0"])

    assert any("[오류]" in line for line in printed)


def test_reject_order_sets_rejected_status():
    app = make_app()

    printed = run_with_inputs(
        app,
        [
            "1", "1", "S-001", "웨이퍼", "0.5", "0.9", "0",
            "2", "1", "S-001", "고객사", "3", "0",
            "3", "3", "ORD-20260416-0001", "0",
            "0",
        ],
    )

    order = app.order_repo.get("ORD-20260416-0001")
    assert order.status == OrderStatus.REJECTED
    assert any("거절 처리 완료" in line for line in printed)


def test_history_menu_shows_rejected_orders_unlike_monitor_menu():
    app = make_app()

    # 시료 등록 -> 주문 -> 거절 (REJECTED)
    run_with_inputs(
        app,
        [
            "1", "1", "S-001", "웨이퍼", "0.5", "0.9", "0",
            "2", "1", "S-001", "고객사", "3", "0",
            "3", "3", "ORD-20260416-0001", "0",
            "0",
        ],
    )

    # 모니터링 메뉴(상태별 집계)는 REJECTED를 제외해야 한다
    monitor_printed = run_with_inputs(app, ["4", "1", "0", "0"])
    assert not any("REJECTED: 1" in line for line in monitor_printed)

    # 시료 주문 메뉴의 "전체 주문 조회"는 REJECTED 주문도 그대로 보여줘야 한다
    history_printed = run_with_inputs(app, ["2", "2", "0", "0"])
    assert any("ORD-20260416-0001" in line and "REJECTED" in line for line in history_printed)
