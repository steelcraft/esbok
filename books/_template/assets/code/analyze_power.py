#!/usr/bin/env python3
"""
Пример скрипта для расчёта энергопотребления embedded-устройства.
Используется в книге как иллюстрация автоматизации инженерных задач.
"""

# tag::power_calc[]
def estimate_power(voltage_v: float, current_ma: float) -> float:
    """Оценка потребляемой мощности в милливаттах."""
    return voltage_v * current_ma


def battery_lifetime(capacity_mah: float, current_ma: float) -> float:
    """Оценка времени работы от батареи в часах."""
    if current_ma <= 0:
        raise ValueError("Ток должен быть положительным")
    return capacity_mah / current_ma
# end::power_calc[]


# tag::usage_example[]
if __name__ == "__main__":
    V_CC = 3.3          # напряжение питания, В
    I_ACTIVE = 12.0     # ток в активном режиме, мА
    I_SLEEP = 0.005     # ток в режиме сна, мА
    CAPACITY = 250.0    # ёмкость батареи, мА·ч

    p_active = estimate_power(V_CC, I_ACTIVE)
    t_active = battery_lifetime(CAPACITY, I_ACTIVE)

    print(f"Мощность в активном режиме: {p_active:.2f} мВт")
    print(f"Время работы от батареи:    {t_active:.1f} ч")
# end::usage_example[]
