from view import formatters


def test_render_main_menu_shows_summary_and_options():
    summary = {"sampleCount": 3, "totalStock": 120, "totalOrderCount": 5, "productionQueueLength": 2}

    text = formatters.render_main_menu(summary)

    assert "등록 시료 수: 3" in text
    assert "총 재고: 120" in text
    assert "전체 주문 수: 5" in text
    assert "생산라인 대기: 2" in text
    assert "1. 시료 관리" in text
    assert "6. 출고 처리" in text
    assert "0. 종료" in text


def test_render_samples_lists_id_name_and_stock():
    samples = [
        {"id": "S-001", "name": "웨이퍼", "avgProductionTime": 0.5, "yield": 0.9, "stock": 100},
    ]

    text = formatters.render_samples(samples)

    assert "S-001" in text
    assert "웨이퍼" in text
    assert "100" in text


def test_render_samples_handles_empty_list():
    text = formatters.render_samples([])

    assert "없" in text  # e.g. "등록된 시료가 없습니다"


def test_render_orders_lists_order_fields():
    orders = [
        {
            "orderId": "ORD-20260416-0001",
            "sampleId": "S-001",
            "customerName": "삼성전자",
            "quantity": 10,
            "status": "RESERVED",
            "createdAt": "2026-04-16T09:00:00",
        }
    ]

    text = formatters.render_orders(orders)

    assert "ORD-20260416-0001" in text
    assert "삼성전자" in text
    assert "RESERVED" in text


def test_render_status_counts():
    counts = {"RESERVED": 1, "PRODUCING": 2, "CONFIRMED": 3, "RELEASE": 4}

    text = formatters.render_status_counts(counts)

    assert "RESERVED: 1" in text
    assert "PRODUCING: 2" in text
    assert "CONFIRMED: 3" in text
    assert "RELEASE: 4" in text
    assert "REJECTED:" not in text


def test_render_stock_status():
    rows = [{"id": "S-001", "name": "웨이퍼", "stock": 5, "demand": 20, "status": "부족"}]

    text = formatters.render_stock_status(rows)

    assert "S-001" in text
    assert "부족" in text


def _display_width(text: str) -> int:
    import unicodedata

    return sum(2 if unicodedata.east_asian_width(ch) in ("W", "F") else 1 for ch in text)


def test_render_stock_status_aligns_status_column_regardless_of_korean_name_length():
    """Regression test: Korean characters render as double-width in a
    terminal, but Python's str.ljust pads by character COUNT, not display
    width. Rows with a different mix of Korean/ASCII in the name column
    used to drift out of alignment as a result. Every row's "상태" column
    should now start at the same terminal COLUMN once padded (not
    necessarily the same character index, since Korean text is shorter in
    character count for the same display width).
    """
    rows = [
        {"id": "S-001", "name": "웨이퍼A", "stock": 90, "demand": 13, "status": "여유"},
        {"id": "S-002", "name": "W", "stock": 0, "demand": 10, "status": "고갈"},
    ]

    text = formatters.render_stock_status(rows)
    data_lines = text.splitlines()[1:]

    status_columns = {
        _display_width(line[: line.index(status)])
        for line, status in zip(data_lines, ("여유", "고갈"))
    }
    assert len(status_columns) == 1


def test_render_production_queue_shows_current_and_pending():
    current = {"orderId": "ORD-1", "sampleId": "S-001", "actualQuantity": 30, "totalTime": 60.0}
    pending = [{"orderId": "ORD-2", "sampleId": "S-002", "actualQuantity": 10, "totalTime": 20.0}]

    text = formatters.render_production_queue(current, pending)

    assert "ORD-1" in text
    assert "ORD-2" in text


def test_render_production_queue_handles_no_current_job():
    text = formatters.render_production_queue(None, [])

    assert "없" in text
