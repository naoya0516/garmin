from app.pace import calc_pace_min_per_km


def test_calc_pace_min_per_km_normal():
    # 5200m を 1710秒(28:30) で走った場合 -> 約5.48分/km
    result = calc_pace_min_per_km(5200.0, 1710.0)
    assert result is not None
    assert round(result, 2) == 5.48


def test_calc_pace_min_per_km_distance_none_returns_none():
    assert calc_pace_min_per_km(None, 1710.0) is None


def test_calc_pace_min_per_km_distance_zero_returns_none():
    # ゼロ割防止の境界値
    assert calc_pace_min_per_km(0, 1710.0) is None


def test_calc_pace_min_per_km_duration_none_returns_none():
    assert calc_pace_min_per_km(5200.0, None) is None
