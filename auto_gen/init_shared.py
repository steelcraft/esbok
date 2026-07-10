#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт создания директории shared/ с общими ресурсами моно-репо ESBOK.
Запуск из корня репозитория: python3 init_shared.py
"""
import os
import stat

SHARED_DIR = "shared"

FILES = {
    "themes/pdf-theme.yml": """\
font:
  catalog:
    PT Serif:
      normal: PT_Serif-Regular.ttf
      bold: PT_Serif-Bold.ttf
      italic: PT_Serif-Italic.ttf
      bold_italic: PT_Serif-BoldItalic.ttf
    Fira Code:
      normal: FiraCode-Regular.ttf
      bold: FiraCode-Bold.ttf
base:
  font_family: PT Serif
  font_size: 11
  line_height_length: 17
heading:
  font_family: PT Serif
  font_style: bold
  margin_top: 1.2 * @base_line_height_length
  margin_bottom: 0.5 * @base_line_height_length
code:
  font_family: Fira Code
  font_size: 9
  line_height: 1.4
  background_color: F5F5F5
  border_color: E0E0E0
  border_radius: 4
table:
  border_color: D0D0D0
  stripe_background_color: F9F9F9
  head:
    font_style: bold
footer:
  border_color: CCCCCC
  recto:
    right:
      content: '{page-number} | {section-title}'
  verso:
    left:
      content: '{section-title} | {page-number}'
""",

    "themes/web.css": """\
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
h1, h2, h3 { color: #111; margin-top: 1.5rem; }
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

.mermaid {
  text-align: center; margin: 1.5rem 0;
  background: #fff; padding: 1rem;
  border: 1px solid #eee; border-radius: 8px;
}

@media (max-width: 768px) {
  #toc { display: none; }
  body { padding: 0.8rem; }
  pre { padding: 0.6rem; }
}
""",

    "scripts/dev-server.sh": """\
#!/usr/bin/env bash
set -euo pipefail

PORT="${1:-8080}"
BOOK_DIR="${2:-books/embedded-basics}"
OUTPUT_DIR="dist/$(basename "$BOOK_DIR")"

echo "🚀 Запуск live-сервера для $(basename "$BOOK_DIR")..."
mkdir -p "$OUTPUT_DIR"

build() {
  echo "📦 Пересборка..."
  make build book="$(basename "$BOOK_DIR")" 2>/dev/null || echo "⚠️ Ошибка сборки"
}

build
python3 -m http.server "$PORT" --directory "$OUTPUT_DIR" &
SERVER_PID=$!

trap "kill $SERVER_PID 2>/dev/null; echo '🛑 Остановлено'; exit" INT TERM

echo "👀 Мониторинг изменений... (Ctrl+C для выхода)"
find "$BOOK_DIR" shared/themes -name '*.adoc' -o -name '*.css' -o -name '*.yml' | \\
  entr -d -c build &
WATCHER_PID=$!

wait
""",

    "scripts/build-utils.sh": """\
#!/usr/bin/env bash
# Вспомогательные функции сборки
set -euo pipefail

check_fonts() {
  if [ ! -d "shared/fonts/pt-serif" ] || [ ! -d "shared/fonts/fira-code" ]; then
    echo "⚠️ Шрифты не найдены в shared/fonts/"
    echo "📥 Скачайте PT Serif и Fira Code в соответствующие папки."
    exit 1
  fi
  echo "✅ Шрифты найдены."
}

clean_dist() {
  echo "🧹 Очистка dist/..."
  rm -rf dist/*
}
""",

    # .gitkeep в пустых директориях
    "fonts/pt-serif/.gitkeep": "",
    "fonts/fira-code/.gitkeep": "",
    "diagrams/.gitkeep": "",
    "vendor/.gitkeep": "",
}


def create_shared():
    if not os.path.isdir("books"):
        print("❌ Ошибка: скрипт нужно запускать из корня репозитория esbok/")
        print("   Ожидается, что рядом есть директория books/")
        return

    if os.path.exists(SHARED_DIR):
        print(f"⚠️ Директория '{SHARED_DIR}/' уже существует.")
        answer = input("   Перезаписать файлы? [y/N]: ").strip().lower()
        if answer != "y":
            print("Отменено.")
            return

    created = 0
    for rel_path, content in FILES.items():
        full_path = os.path.join(SHARED_DIR, rel_path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(content)

        # Права на выполнение для .sh
        if rel_path.endswith(".sh"):
            st = os.stat(full_path)
            os.chmod(full_path, st.st_mode | stat.S_IEXEC | stat.S_IXGRP | stat.S_IXOTH)

        created += 1

    # Права на директории
    for root, dirs, _ in os.walk(SHARED_DIR):
        for d in dirs:
            os.chmod(os.path.join(root, d), 0o755)

    print(f"✅ Создана директория '{SHARED_DIR}/' ({created} файлов)")
    print()
    print("📋 Следующие шаги:")
    print("   1. Положите шрифты PT Serif в shared/fonts/pt-serif/")
    print("      Файлы: PT_Serif-Regular.ttf, PT_Serif-Bold.ttf,")
    print("             PT_Serif-Italic.ttf, PT_Serif-BoldItalic.ttf")
    print("   2. Положите шрифты Fira Code в shared/fonts/fira-code/")
    print("      Файлы: FiraCode-Regular.ttf, FiraCode-Bold.ttf")
    print("   3. Скачайте шрифты:")
    print("      • PT Serif:    https://google-webfonts.txt/")
    print("      • Fira Code:   https://github.com/tonsky/FiraCode/releases")
    print("   4. Проверьте сборку: make build book=embedded-basics")


if __name__ == "__main__":
    create_shared()
