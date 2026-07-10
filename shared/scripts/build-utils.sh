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
