import pytest

from controller.sample_controller import SampleController
from model.repository import InMemorySampleRepository


@pytest.fixture
def controller():
    return SampleController(InMemorySampleRepository())


class TestRegister:
    def test_registers_new_sample(self, controller):
        result = controller.register(
            sample_id="S-001", name="웨이퍼", avg_production_time=0.5, yield_rate=0.9
        )

        assert result["id"] == "S-001"
        assert result["stock"] == 0

    def test_rejects_duplicate_id(self, controller):
        controller.register(sample_id="S-001", name="웨이퍼", avg_production_time=0.5, yield_rate=0.9)

        with pytest.raises(ValueError):
            controller.register(sample_id="S-001", name="다른시료", avg_production_time=1, yield_rate=0.5)

    def test_rejects_invalid_yield(self, controller):
        with pytest.raises(ValueError):
            controller.register(sample_id="S-002", name="웨이퍼", avg_production_time=0.5, yield_rate=1.5)

    def test_rejects_zero_yield(self, controller):
        # yield must be > 0 (docs/SCHEMA.md: 0 < yield <= 1)
        with pytest.raises(ValueError):
            controller.register(sample_id="S-002", name="웨이퍼", avg_production_time=0.5, yield_rate=0)

    def test_accepts_yield_of_exactly_one(self, controller):
        result = controller.register(
            sample_id="S-002", name="완벽수율시료", avg_production_time=0.5, yield_rate=1.0
        )

        assert result["yield"] == 1.0

    def test_rejects_non_positive_avg_production_time(self, controller):
        with pytest.raises(ValueError):
            controller.register(sample_id="S-003", name="웨이퍼", avg_production_time=0, yield_rate=0.9)


class TestListAndSearch:
    def test_list_all_includes_stock(self, controller):
        controller.register(sample_id="S-001", name="웨이퍼", avg_production_time=0.5, yield_rate=0.9)

        result = controller.list_all()

        assert result == [
            {"id": "S-001", "name": "웨이퍼", "avgProductionTime": 0.5, "yield": 0.9, "stock": 0}
        ]

    def test_search_by_name_matches_substring(self, controller):
        controller.register(sample_id="S-001", name="실리콘 웨이퍼", avg_production_time=0.5, yield_rate=0.9)
        controller.register(sample_id="S-002", name="포토레지스트", avg_production_time=0.5, yield_rate=0.9)

        result = controller.search_by_name("웨이퍼")

        assert [s["id"] for s in result] == ["S-001"]

    def test_search_by_name_returns_empty_list_when_no_match(self, controller):
        controller.register(sample_id="S-001", name="실리콘 웨이퍼", avg_production_time=0.5, yield_rate=0.9)

        result = controller.search_by_name("존재하지않는이름")

        assert result == []
