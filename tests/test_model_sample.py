import pytest

from model.sample import Sample


def test_creates_valid_sample():
    sample = Sample(
        id="S-001",
        name="실리콘 웨이퍼-8인치",
        avg_production_time=0.5,
        yield_rate=0.92,
        stock=480,
    )

    assert sample.id == "S-001"
    assert sample.name == "실리콘 웨이퍼-8인치"
    assert sample.avg_production_time == 0.5
    assert sample.yield_rate == 0.92
    assert sample.stock == 480


@pytest.mark.parametrize(
    "field, value",
    [
        ("id", ""),
        ("name", ""),
        ("avg_production_time", 0),
        ("avg_production_time", -1),
        ("yield_rate", 0),
        ("yield_rate", 1.5),
        ("yield_rate", -0.1),
        ("stock", -1),
    ],
)
def test_rejects_invalid_fields(field, value):
    kwargs = dict(
        id="S-001",
        name="시료",
        avg_production_time=0.5,
        yield_rate=0.92,
        stock=10,
    )
    kwargs[field] = value

    with pytest.raises(ValueError):
        Sample(**kwargs)


def test_to_dict_uses_schema_field_names():
    sample = Sample(
        id="S-001",
        name="시료",
        avg_production_time=0.5,
        yield_rate=0.92,
        stock=10,
    )

    assert sample.to_dict() == {
        "id": "S-001",
        "name": "시료",
        "avgProductionTime": 0.5,
        "yield": 0.92,
        "stock": 10,
    }


def test_from_dict_round_trip():
    data = {
        "id": "S-002",
        "name": "시료2",
        "avgProductionTime": 1.2,
        "yield": 0.8,
        "stock": 5,
    }

    sample = Sample.from_dict(data)

    assert sample.to_dict() == data
