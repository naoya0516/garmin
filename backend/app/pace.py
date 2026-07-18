"""距離・時間からペースを算出する純粋関数のみを持つモジュール。

DBアクセス・Garmin通信は行わない（docs/08_詳細設計.md `pace.py` 節）。
"""

from __future__ import annotations


def calc_pace_min_per_km(
    distance_m: float | None, duration_s: float | None
) -> float | None:
    """平均ペース（分/km）を算出する。

    - distance_m が None または 0以下の場合は None を返す（ゼロ割防止）
    - duration_s が None の場合は None を返す
    - 計算式: (duration_s / 60) / (distance_m / 1000)
    """
    if distance_m is None or distance_m <= 0:
        return None
    if duration_s is None:
        return None
    return (duration_s / 60) / (distance_m / 1000)
