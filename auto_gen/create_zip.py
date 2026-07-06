#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import zipfile
import stat

TEMPLATE_DIR = "embedded-bok-template"
ZIP_NAME = "embedded-bok-template.zip"

files = {
    # 1. Тема для PDF с кириллическими шрифтами
    "shared/themes/pdf-theme.yml": """\
font:
  catalog:
    PT Serif:
      normal: PT Serif Regular.ttf
      bold: PT Serif Bold.ttf
      italic: PT Serif Italic.ttf
      bold_italic: PT Serif Bold Italic.ttf
    Fira Code:
      normal: FiraCode-Regular.ttf
      bold: FiraCode-Bold.ttf
    fallbacks:
      - Noto Sans
      - Noto Serif
base:
  font_family: PT Serif
  font_size: 11
  line_height_length: 17
code:
  font_family: Fira Code
  font_size: 9
  line_height: 1.4
heading:
  font_family: PT Serif
  font_style: bold
caption:
  font_family: PT Serif
  font_style: italic
footer:
  font_size: 8
  border_color: CCCCCC
  recto:
    right:
      content: '{page-number}'
  verso:
    left:
      content: '{page-number}'
""",

    # 2. Стили для Web (адаптивные)
    "shared/themes/web.css": """\
:root {
  --bg: #ffffff;
  --text: #1a1a1a;
  --code-bg: #f6f8fa;
  --accent: #0969da;
  --note-bg: #f0f4f8;
  --note-border: #2196f3;
}
body {
  font-family: 'PT Serif', 'Linux Libertine', Georgia, serif;
  color: var(--text);
  line-height: 1.6;
  max-width: 900px;
  margin: 0 auto;
  padding: 1.5rem;
}
h1, h2, h3 { color: #111; }
a { color: var(--accent); text-decoration: none; }
a:hover { text-decoration: underline; }

pre { background: var(--code-bg); padding: 1rem; border-radius: 6px; overflow-x: auto; }
code { font-family: 'Fira Code', 'Consolas', monospace; font-size: 0.9em; }

table { border-collapse: collapse; width: 100%; margin: 1.2rem 0; }
th, td { border: 1px solid #ddd; padding: 0.5rem; text-align: left; }
th { background: #f9fafb; }

.admonitionblock {
  margin: 1.2rem 0; padding: 1rem 1rem 1rem 1.5rem;
  border-left: 4px solid var(--note-border); background: var(--note-bg);
  border-radius: 0 6px 6px 0;
}
.admonitionblock .title { font-weight: 600; margin-bottom: 0.3rem; }

.mermaid { text-align: center; margin: 1.5rem 0; }

@media (max-width: 768px) {
  #toc { display: none; }
  body { padding: 0.8rem; }
}
""",

    # 3. Скрипт локального сервера с live-reload
    "scripts/local_server.sh": """\
#!/usr/bin/env bash
set -euo pipefail

PORT="${1:-8080}"
BOOK_DIR="${2:-books/embedded-basics}"
OUTPUT_DIR="${BOOK_DIR}/dist"

echo "🚀 Запуск локального сервера предпросмотра..."
echo "📖 Мониторинг изменений в: ${BOOK_DIR}/**"
echo "🌐 Открыть: http://localhost:${PORT}"

# Установка зависимостей, если нет entr
if ! command -v entr &> /dev/null; then
  echo "⚠️ Для live-reload требуется entr. Установите:"
  echo "   macOS: brew install entr"
  echo "   Ubuntu/Debian: sudo apt install entr"
  echo "   Fedora: sudo dnf install entr"
  exit 1
fi

mkdir -p "$OUTPUT_DIR"

build() {
  echo "📦 Пересборка HTML..."
  cd "$BOOK_DIR"
  bundle exec asciidoctor -b html5 -d book -o dist/index.html book.adoc 2>/dev/null || echo "⚠️ Ошибка сборки (проверьте синтаксис .adoc)"
  cd - > /dev/null
}

# Начальная сборка
build

# Запуск HTTP-сервера в фоне
python3 -m http.server "$PORT" --directory "$OUTPUT_DIR" &
SERVER_PID=$!

# Мониторинг файлов
echo "👀 Ожидание изменений... (Ctrl+C для остановки)"
find "$BOOK_DIR" -name '*.adoc' -o -name '*.css' -o -name '*.svg' | entr -d -c build &
WATCHER_PID=$!

trap "kill $SERVER_PID $WATCHER_PID 2>/dev/null; echo '🛑 Сервер остановлен'; exit" INT TERM
wait
""",

    # 4. Точка входа книги
    "books/embedded-basics/book.adoc": """\
= Учебник по Embedded-системам: основы
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
:pdf-fontsdir: {docdir}/../../shared/assets/fonts
:diagram-format: svg

ifdef::env-github[]
:toc: macro
endif::[]

include::chapters/ch01.adoc[]
""",

    # 5. Мета-информация для Web
    "books/embedded-basics/docinfo.html": """\
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<script src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>
<script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
<script>mermaid.initialize({ startOnLoad: true, theme: 'default' });</script>
<link rel="stylesheet" href="../../shared/themes/web.css">
""",

    # 6. Зависимости Ruby (добавлен asciidoctor-diagram)
    "books/embedded-basics/Gemfile": """\
source 'https://rubygems.org'
gem 'asciidoctor'
gem 'asciidoctor-pdf'
gem 'asciidoctor-diagram'
gem 'rouge'
""",

    # 7. Пример главы с Mermaid
    "books/embedded-basics/chapters/ch01.adoc": """\
[[intro]]
== Введение в микроконтроллеры

Embedded-системы — это комбинация аппаратного и программного обеспечения, спроектированная для выполнения специфических задач в реальном времени.

[[fig:mcu]]
.Схема подключения микроконтроллера к периферии
image::mcu-schematic.svg["Схема подключения", align="center", width=70%]

Как показано на <<fig:mcu>>, вывод `PB5` управляет светодиодом через токоограничивающий резистор.

.Базовая инициализация GPIO на C
[source,c]
----
#include <avr/io.h>

int main(void) {
    DDRB |= (1 << PB5); // PB5 как выход
    while (1) {
        PORTB ^= (1 << PB5); // Инверсия состояния
    }
    return 0;
}
----

.Расчёт тока через резистор
[latexmath]
++++
I = \\frac{V_{CC} - V_{LED}}{R} = \\frac{5\\,\\text{В} - 2\\,\\text{В}}{330\\,\\Omega} \\approx 9.1\\,\\text{мА}
++++

[[diag:mcu-states]]
.Диаграмма состояний микроконтроллера
[mermaid, fig:mcu-states, title="Жизненный цикл обработки событий"]
....
stateDiagram-v2
    [*] --> Init : Включение питания
    Init --> Idle : Инициализация завершена
    Idle --> Processing : Прерывание / Событие
    Processing --> Idle : Задача выполнена
    Processing --> Error : Таймаут / Ошибка шины
    Error --> Idle : Сброс / Восстановление
    Error --> [*] : Критическая авария
....

|===
| Параметр | Мин. | Тип. | Макс. | Ед. изм.
| Напряжение питания | 1.8 | 3.3 | 5.0 | В
| Ток потребления | - | 12 | 25 | мА
| Рабочая температура | -40 | 25 | 85 | °C
|===

NOTE: При проектировании учтите допуск резисторов ±5% и температурный дрейф параметров транзисторов.

Это примечание с подстрочной ссылкой.footnote:[Подробности см. в даташите ATmega328P, раздел 18.2 "Electrical Characteristics".]
""",

    # 8. CI/CD Workflow
    ".github/workflows/build.yml": """\
name: Build & Deploy Book

on:
  push:
    branches: [main]
  workflow_dispatch:

permissions:
  contents: read
  pages: write
  id-token: write

concurrency:
  group: pages
  cancel-in-progress: true

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: ruby/setup-ruby@v1
        with:
          ruby-version: '3.3'
          bundler-cache: true
      - run: cd books/embedded-basics && bundle install

      - name: Build Web HTML
        run: |
          mkdir -p dist/embedded-basics
          cd books/embedded-basics
          bundle exec asciidoctor -b html5 -d book -o ../../dist/embedded-basics/index.html book.adoc

      - name: Build PDF
        run: |
          mkdir -p dist/embedded-basics
          cd books/embedded-basics
          bundle exec asciidoctor-pdf -o ../../dist/embedded-basics/book.pdf book.adoc

      - name: Upload Pages artifact
        uses: actions/upload-pages-artifact@v3
        with:
          path: dist/embedded-basics

      - name: Upload PDF Artifact
        uses: actions/upload-artifact@v4
        with:
          name: embedded-basics-pdf
          path: dist/embedded-basics/book.pdf

  deploy:
    needs: build
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to GitHub Pages
        id: deployment
        uses: actions/deploy-pages@v4
"""
}

def create_zip():
    os.makedirs(TEMPLATE_DIR, exist_ok=True)
    with zipfile.ZipFile(ZIP_NAME, 'w', zipfile.ZIP_DEFLATED) as zf:
        for filepath, content in files.items():
            full_path = os.path.join(TEMPLATE_DIR, filepath)
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            # Делаем local_server.sh исполняемым
            if filepath.endswith('.sh'):
                st = os.stat(full_path)
                os.chmod(full_path, st.st_mode | stat.S_IEXEC)
            
            zf.write(full_path)
            os.remove(full_path)
            
        # Очистка пустых директорий
        for dirpath, dirnames, filenames in os.walk(TEMPLATE_DIR, topdown=False):
            if not dirnames and not filenames:
                os.rmdir(dirpath)
        if os.path.isdir(TEMPLATE_DIR) and not os.listdir(TEMPLATE_DIR):
            os.rmdir(TEMPLATE_DIR)
            
    print(f"✅ Архив {ZIP_NAME} успешно создан!")
    print("\n📦 Инструкция по запуску:")
    print("1. unzip embedded-bok-template.zip && cd embedded-bok-template")
    print("2. Установите шрифты (Linux/WSL): sudo apt install fonts-pt-serif fonts-firacode")
    print("3. Установите watcher для live-reload: sudo apt install entr  (macOS: brew install entr)")
    print("4. Запустите сервер: bash scripts/local_server.sh")
    print("5. Откройте: http://localhost:8080")

if __name__ == "__main__":
    create_zip()
