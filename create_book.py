#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Интерактивное создание новой книги из шаблона _template/.
Запуск: python3 create_book.py
"""
import os
import re
import shutil
import sys

TEMPLATE = "books/_template"

def slugify(name: str) -> str:
    """Преобразует название в валидный идентификатор директории."""
    # Транслитерация кириллицы (упрощённая)
    translit = {
        'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e', 'ё': 'yo',
        'ж': 'zh', 'з': 'z', 'и': 'i', 'й': 'y', 'к': 'k', 'л': 'l', 'м': 'm',
        'н': 'n', 'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't', 'у': 'u',
        'ф': 'f', 'х': 'h', 'ц': 'ts', 'ч': 'ch', 'ш': 'sh', 'щ': 'sch',
        'ъ': '', 'ы': 'y', 'ь': '', 'э': 'e', 'ю': 'yu', 'я': 'ya'
    }
    name = name.lower()
    for ru, en in translit.items():
        name = name.replace(ru, en)
    return re.sub(r'[^a-z0-9-]', '-', name.strip()).strip('-')

def create_book():
    if not os.path.isdir(TEMPLATE):
        print(f"❌ Шаблон не найден: {TEMPLATE}")
        print("   Сначала запустите: python3 init_template.py")
        sys.exit(1)

    name = input("📖 Название новой книги: ").strip()
    if not name:
        print("❌ Название не может быть пустым")
        sys.exit(1)

    slug = slugify(name)
    if not slug:
        print("❌ Не удалось создать идентификатор из названия")
        sys.exit(1)

    target = f"books/{slug}"

    if os.path.exists(target):
        print(f"❌ Директория уже существует: {target}")
        sys.exit(1)

    shutil.copytree(TEMPLATE, target)
    print(f"\n✅ Книга создана: {target}/")

    # Обновляем заголовок в book.adoc
    book_adoc = os.path.join(target, "book.adoc")
    with open(book_adoc, "r", encoding="utf-8") as f:
        content = f.read()
    content = content.replace("= Название книги", f"= {name}", 1)
    with open(book_adoc, "w", encoding="utf-8") as f:
        f.write(content)

    print()
    print("📋 Следующие шаги:")
    print(f"   1. Отредактируйте {book_adoc}")
    print(f"   2. Напишите главы в {target}/chapters/")
    print(f"   3. Добавьте '{slug}' в matrix.book файла .github/workflows/ci-build.yml")
    print(f"   4. Проверьте локально: make build book={slug}")

if __name__ == "__main__":
    create_book()
