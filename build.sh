#!/usr/bin/env bash
set -euo pipefail

BOOK="${1:-c-for-emb}"
BOOK_DIR="books/$BOOK"
DIST_DIR="dist/$BOOK"

if [ ! -f "$BOOK_DIR/book.adoc" ]; then
    echo "❌ Ошибка: файл $BOOK_DIR/book.adoc не найден"
    exit 1
fi

echo "📦 Сборка книги: $BOOK"
mkdir -p "$DIST_DIR"

# Копирование ресурсов
if [ -d "$BOOK_DIR/assets" ]; then
    cp -r "$BOOK_DIR/assets" "$DIST_DIR/"
fi

# Очистка кэша диаграмм
rm -rf "$BOOK_DIR/.asciidoctor" 2>/dev/null || true
pwd
cd "$BOOK_DIR"

# Сборка PDF
echo "📄 Сборка PDF..."
pwd
cd "$BOOK_DIR"

# ВАЖНО: используйте именно asciidoctor-pdf (слитно), а не asciidoctor -pdf
asciidoctor-pdf \
    -a pdf-theme=../../shared/themes/pdf-theme.yml \
    -a pdf-fontsdir=../../shared/fonts/pt-serif;../../shared/fonts/fira-code \
    -o "../../$DIST_DIR/book.pdf" book.adoc

cd - > /dev/null
echo "   ✅ $DIST_DIR/book.pdf"

cd - > /dev/null

echo ""
echo "🎉 Готово!"
echo "   HTML: $DIST_DIR/index.html"
echo "   PDF:  $DIST_DIR/book.pdf"
