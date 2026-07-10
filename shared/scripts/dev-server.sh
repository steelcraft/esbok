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
find "$BOOK_DIR" shared/themes -name '*.adoc' -o -name '*.css' -o -name '*.yml' | \
  entr -d -c build &
WATCHER_PID=$!

wait
