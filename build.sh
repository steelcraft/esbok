#!/usr/bin/env bash
set -euo pipefail

# Название книги (первый аргумент или embedded-basics по умолчанию)
BOOK="${1:-embedded-basics}"
BOOK_DIR="books/$BOOK"
DIST_DIR="dist/$BOOK"

# Проверка существования книги
if [ ! -f "$BOOK_DIR/book.adoc" ]; then
    echo "❌ Ошибка: файл $BOOK_DIR/book.adoc не найден"
    echo "   Доступные книги:"
    ls books/ | grep -v _template | sed 's/^/     /'
    exit 1
fi

echo "📦 Сборка книги: $BOOK"

# Создание директории вывода
mkdir -p "$DIST_DIR"

# Сборка HTML
echo "🌐 Сборка HTML..."
cd "$BOOK_DIR"
asciidoctor -b html5 -d book -o "../../$DIST_DIR/index.html" book.adoc
cd - > /dev/null
echo "   ✅ $DIST_DIR/index.html"

# Сборка PDF
echo "📄 Сборка PDF..."
cd "$BOOK_DIR"
asciidoctor-pdf -o "../../$DIST_DIR/book.pdf" book.adoc
cd - > /dev/null
echo "   ✅ $DIST_DIR/book.pdf"

echo ""
echo "🎉 Готово!"
echo "   HTML: $DIST_DIR/index.html"
echo "   PDF:  $DIST_DIR/book.pdf"