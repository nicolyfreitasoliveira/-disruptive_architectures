import pandas as pd
import pytest
from src.processing import normalize


def frame():
    # Fixtures de teste apenas; não são base de dados nem evidência acadêmica.
    return pd.DataFrame({"id": ["test"], "room_id/id": [" room "],
                         "noted_date": ["08-12-2018 09:30"], "temp": ["24"], "out/in": ["In"]})


def test_kaggle_mapping_and_day_first():
    result = normalize(frame())
    assert result.loc[0, "device_id"] == "room"
    assert result.loc[0, "recorded_at"] == pd.Timestamp("2018-12-08 09:30")
    assert result.loc[0, "temperature"] == 24
    assert result.loc[0, "location"] == "In"


@pytest.mark.parametrize("column,value", [("temp", "NaN"), ("temp", "inf"), ("temp", "bad"),
                                          ("noted_date", "31-02-2018 09:30"), ("room_id/id", " ")])
def test_invalid_readings_fail(column, value):
    data = frame()
    data.loc[0, column] = value
    with pytest.raises(ValueError, match="inválidas"):
        normalize(data)


def test_missing_columns():
    with pytest.raises(ValueError, match="ausentes"):
        normalize(frame().drop(columns="temp"))


def test_iso_and_negative_temperature():
    data = pd.DataFrame({"device_id": ["a"], "recorded_at": ["2020-01-02T03:04:00"], "temperature": ["-5"]})
    result = normalize(data)
    assert result.loc[0, "temperature"] == -5
    assert result.loc[0, "recorded_at"] == pd.Timestamp("2020-01-02 03:04")
