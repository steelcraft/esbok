#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт наполнения директории books/_template/ примерами ресурсов.
Создаёт эталонные SVG-иллюстрации, C/Python-файлы с тегами и обновляет
первую главу для демонстрации include:: с тегами.

Запуск из корня репозитория: python3 populate_template.py
"""
import os
import stat

TEMPLATE_DIR = "books/_template"

FILES = {
    # ============================================================
    # 1. SVG-иллюстрация: блок-схема микроконтроллера
    # ============================================================
    "assets/images/mcu-block-diagram.svg": """\
<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 320" font-family="PT Serif, sans-serif">
  <defs>
    <marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5"
            markerWidth="6" markerHeight="6" orient="auto">
      <path d="M 0 0 L 10 5 L 0 10 z" fill="#333"/>
    </marker>
  </defs>

  <!-- Заголовок -->
  <text x="300" y="25" text-anchor="middle" font-size="16" font-weight="bold">
    Упрощённая архитектура микроконтроллера
  </text>

  <!-- CPU -->
  <rect x="230" y="60" width="140" height="70" rx="6"
        fill="#e3f2fd" stroke="#1976d2" stroke-width="2"/>
  <text x="300" y="95" text-anchor="middle" font-size="14" font-weight="bold">CPU Core</text>
  <text x="300" y="115" text-anchor="middle" font-size="11" fill="#555">ARM Cortex-M4</text>

  <!-- Шина AHB -->
  <rect x="80" y="160" width="440" height="30" rx="4"
        fill="#fff3e0" stroke="#f57c00" stroke-width="1.5"/>
  <text x="300" y="180" text-anchor="middle" font-size="12" font-weight="bold">
    Шина AHB (High-speed)
  </text>

  <!-- Соединение CPU → AHB -->
  <line x1="300" y1="130" x2="300" y2="160" stroke="#333" stroke-width="2"
        marker-end="url(#arrow)"/>

  <!-- Периферия -->
  <g font-size="11">
    <!-- Flash -->
    <rect x="40" y="220" width="100" height="60" rx="4"
          fill="#f3e5f5" stroke="#7b1fa2" stroke-width="1.5"/>
    <text x="90" y="245" text-anchor="middle" font-weight="bold">Flash</text>
    <text x="90" y="265" text-anchor="middle" fill="#555">512 KB</text>

    <!-- SRAM -->
    <rect x="160" y="220" width="100" height="60" rx="4"
          fill="#f3e5f5" stroke="#7b1fa2" stroke-width="1.5"/>
    <text x="210" y="245" text-anchor="middle" font-weight="bold">SRAM</text>
    <text x="210" y="265" text-anchor="middle" fill="#555">128 KB</text>

    <!-- GPIO -->
    <rect x="280" y="220" width="100" height="60" rx="4"
          fill="#e8f5e9" stroke="#388e3c" stroke-width="1.5"/>
    <text x="330" y="245" text-anchor="middle" font-weight="bold">GPIO</text>
    <text x="330" y="265" text-anchor="middle" fill="#555">8 портов</text>

    <!-- Peripherals -->
    <rect x="400" y="220" width="160" height="60" rx="4"
          fill="#fff8e1" stroke="#f9a825" stroke-width="1.5"/>
    <text x="480" y="245" text-anchor="middle" font-weight="bold">Периферия</text>
    <text x="480" y="265" text-anchor="middle" fill="#555">UART · SPI · I2C · ADC</text>
  </g>

  <!-- Соединения AHB → периферия -->
  <line x1="90" y1="190" x2="90" y2="220" stroke="#333" stroke-width="1.5"/>
  <line x1="210" y1="190" x2="210" y2="220" stroke="#333" stroke-width="1.5"/>
  <line x1="330" y1="190" x2="330" y2="220" stroke="#333" stroke-width="1.5"/>
  <line x1="480" y1="190" x2="480" y2="220" stroke="#333" stroke-width="1.5"/>

  <!-- Подпись -->
  <text x="300" y="310" text-anchor="middle" font-size="10" fill="#777" font-style="italic">
    Рис. 1. Блок-схема типичного 32-битного микроконтроллера
  </text>
</svg>
""",

    # ============================================================
    # 2. C-файл с тегами для include:: с tags=
    # ============================================================
    "assets/code/gpio_blinky.c": """\
/**
 * @file gpio_blinky.c
 * @brief Пример мигания светодиодом на STM32 (HAL)
 *
 * Демонстрация использования тегов для выборочного включения
 * фрагментов кода в AsciiDoc через include::...[tags=...]
 */

#include <stm32f4xx.h>

/* tag::init_block[] */
void GPIO_Init_LED(void) {
    /* Включаем тактирование порта A */
    RCC->AHB1ENR |= RCC_AHB1ENR_GPIOAEN;

    /* Настраиваем PA5 как выход (push-pull) */
    GPIOA->MODER  &= ~(0x3U << (5 * 2));  /* сброс */
    GPIOA->MODER  |=  (0x1U << (5 * 2));  /* режим output */
    GPIOA->OTYPER &= ~(1U << 5);          /* push-pull */
    GPIOA->OSPEEDR &= ~(0x3U << (5 * 2)); /* low speed */
}
/* end::init_block[] */

/* tag::toggle_block[] */
void GPIO_Toggle_LED(void) {
    GPIOA->ODR ^= (1U << 5);
}
/* end::toggle_block[] */

/* tag::delay_block[] */
void delay_ms(uint32_t ms) {
    /* Простейшая задержка (зависит от частоты ядра) */
    volatile uint32_t count = ms * (SystemCoreClock / 4000U);
    while (count--) { __NOP(); }
}
/* end::delay_block[] */

/* tag::main_block[] */
int main(void) {
    SystemCoreClockUpdate();
    GPIO_Init_LED();

    while (1) {
        GPIO_Toggle_LED();
        delay_ms(500);
    }
    return 0;
}
/* end::main_block[] */
""",

    # ============================================================
    # 3. Python-скрипт для анализа/тестирования
    # ============================================================
    "assets/code/analyze_power.py": """\
#!/usr/bin/env python3
\"\"\"
Пример скрипта для расчёта энергопотребления embedded-устройства.
Используется в книге как иллюстрация автоматизации инженерных задач.
\"\"\"

# tag::power_calc[]
def estimate_power(voltage_v: float, current_ma: float) -> float:
    \"\"\"Оценка потребляемой мощности в милливаттах.\"\"\"
    return voltage_v * current_ma


def battery_lifetime(capacity_mah: float, current_ma: float) -> float:
    \"\"\"Оценка времени работы от батареи в часах.\"\"\"
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
""",

    # ============================================================
    # 4. README для assets/ с описанием best practices
    # ============================================================
    "assets/README.adoc": """\
= Ресурсы книги

Эта директория содержит ресурсы, специфичные для данной книги.

== Структура

* `images/` — векторные (SVG) и растровые (PNG) иллюстрации
* `code/` — исходные файлы примеров кода (.c, .py, .S и т.п.)

== Best practices

=== Изображения
* Предпочитайте **SVG** для схем и диаграмм (масштабируются, версионируются как текст).
* Используйте **PNG** только для скриншотов и растровых данных.
* Именуйте файлы в kebab-case: `mcu-block-diagram.svg`.

=== Исходный код
* Размечайте фрагменты тегами для выборочного включения в текст:
+
[source,c]
----
// tag::init_block[]
void init(void) { /* ... */ }
// end::init_block[]
----
+
* Подключайте в `.adoc` через:
+
[source,asciidoc]
----
include::{docdir}/assets/code/gpio_blinky.c[tags=init_block]
----
* Храните код компилируемым/исполняемым — это гарантия его корректности.
""",

    # ============================================================
    # 5. Обновлённая первая глава с использованием include::
    # ============================================================
    "chapters/ch01.adoc": """\
[[ch01]]
== Архитектура микроконтроллеров

В этой главе мы рассмотрим базовую архитектуру современного микроконтроллера
и научимся настраивать порты ввода-вывода (GPIO).

=== Блок-схема МК

На <<fig:mcu_arch>> показана упрощённая архитектура типичного 32-битного
микроконтроллера на ядре ARM Cortex-M.

[[fig:mcu_arch]]
.Упрощённая архитектура микроконтроллера
image::mcu-block-diagram.svg["Блок-схема МК", align="center", width=85%]

Центральный процессор (CPU) взаимодействует с памятью и периферией через
систему шин. Шина AHB обеспечивает высокоскоростной доступ к Flash, SRAM
и основным модулям периферии.

=== Пример: мигание светодиодом

Рассмотрим классический пример — мигание светодиодом, подключённым к пину PA5.
Полный исходный код доступен в файле `assets/code/gpio_blinky.c`.

.Инициализация GPIO
[source,c]
----
include::{docdir}/assets/code/gpio_blinky.c[tags=init_block]
----

.Функция переключения состояния пина
[source,c]
----
include::{docdir}/assets/code/gpio_blinky.c[tags=toggle_block]
----

.Главный цикл программы
[source,c]
----
include::{docdir}/assets/code/gpio_blinky.c[tags=main_block]
----

=== Автоматизация расчётов

Для оценки энергопотребления устройства удобно использовать скрипты.
Ниже приведён пример на Python, который рассчитывает мощность и время
работы от батареи.

.Расчёт энергопотребления
[source,python]
----
include::{docdir}/assets/code/analyze_power.py[tags=power_calc]
----

.Пример использования
[source,python]
----
include::{docdir}/assets/code/analyze_power.py[tags=usage_example]
----

NOTE: Все примеры кода в этой книге являются компилируемыми/исполняемыми.
Их исходники хранятся в `assets/code/` и подключаются через механизм `include::`
с использованием тегов `tag::`/`end::`.

TIP: Для детального раздачи настройки тактирования и регистров см. главу
<<ch02>> (если она добавлена в `book.adoc`).
"""
}


def populate_template():
    if not os.path.isdir("books"):
        print("❌ Ошибка: скрипт нужно запускать из корня репозитория esbok/")
        print("   Ожидается структура: esbok/books/")
        return

    # Создаём _template, если его нет
    if not os.path.isdir(TEMPLATE_DIR):
        print(f"ℹ️  Директория '{TEMPLATE_DIR}/' не найдена — будет создана базовая структура.")
        os.makedirs(TEMPLATE_DIR, exist_ok=True)
        # Базовый book.adoc, если его нет
        book_adoc = os.path.join(TEMPLATE_DIR, "book.adoc")
        if not os.path.exists(book_adoc):
            with open(book_adoc, "w", encoding="utf-8") as f:
                f.write("""\
= Название книги
:doctype: book
:toc: left
:toclevels: 3
:sectnums:
:icons: font
:source-highlighter: rouge
:stem: latexmath
:lang: ru
:docinfo: shared
:imagesdir: {docdir}/assets/images
:stylesdir: {docdir}/../../shared/themes
:pdf-theme: {stylesdir}/pdf-theme.yml
:pdf-fontsdir: {docdir}/../../shared/fonts
:diagram-format: svg

ifdef::env-github[]
:toc: macro
endif::[]

include::chapters/ch01.adoc[]
""")

    created, updated = 0, 0
    for rel_path, content in FILES.items():
        full_path = os.path.join(TEMPLATE_DIR, rel_path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)

        existed = os.path.exists(full_path)
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(content)

        if existed:
            updated += 1
        else:
            created += 1

        # Делаем Python-скрипт исполняемым
        if rel_path.endswith(".py"):
            st = os.stat(full_path)
            os.chmod(full_path, st.st_mode | stat.S_IEXEC | stat.S_IXGRP | stat.S_IXOTH)

    # Удаляем .gitkeep в директориях, которые теперь содержат реальные файлы
    for gitkeep in ["assets/.gitkeep", "assets/images/.gitkeep", "assets/code/.gitkeep"]:
        p = os.path.join(TEMPLATE_DIR, gitkeep)
        if os.path.exists(p):
            os.remove(p)

    print(f"✅ Директория '{TEMPLATE_DIR}/' наполнена примерами:")
    print(f"   • создано файлов: {created}")
    print(f"   • обновлено файлов: {updated}")
    print()
    print("📁 Что было добавлено:")
    print("   📄 assets/images/mcu-block-diagram.svg — SVG-схема архитектуры МК")
    print("   📄 assets/code/gpio_blinky.c           — C-пример с тегами tag::/end::")
    print("   📄 assets/code/analyze_power.py        — Python-пример с тегами")
    print("   📄 assets/README.adoc                  — best practices по ресурсам")
    print("   📄 chapters/ch01.adoc                  — глава с include:: и тегами")
    print()
    print("🚀 Проверка:")
    print(f"   make build book=_template")
    print(f"   make dev book=_template")
    print()
    print("💡 Теперь при создании новой книги (make init-book) все эти примеры")
    print("   будут скопированы как эталонный образец организации ресурсов.")


if __name__ == "__main__":
    populate_template()
