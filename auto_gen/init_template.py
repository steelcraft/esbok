#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт создания директории books/_template/ со стандартным содержимым.
Запуск из корня репозитория: python3 init_template.py
"""
import os
import stat

TEMPLATE_DIR = "books/_template"

FILES = {
    "book.adoc": """\
= Название книги
Автор Имя Фамилия
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
// include::chapters/ch02.adoc[]
""",

    "docinfo.html": """\
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<script src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>
<script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
<script>mermaid.initialize({ startOnLoad: true, theme: 'neutral' });</script>
<link rel="stylesheet" href="../../shared/themes/web.css">
""",

    "Gemfile": """\
source 'https://rubygems.org'
gem 'asciidoctor'
gem 'asciidoctor-pdf'
gem 'asciidoctor-diagram'
gem 'rouge'
""",

    "chapters/ch01.adoc": """\
[[ch01]]
== Первая глава

Описание первой главы.

.Пример кода
[source,c]
----
int main(void) {
    return 0;
}
----

NOTE: Замените этот текст содержимым вашей главы.
""",

    "assets/.gitkeep": "",
    "assets/images/.gitkeep": "",
    "assets/code/.gitkeep": "",
}


def create_template():
    if not os.path.isdir("books"):
        print("❌ Ошибка: скрипт нужно запускать из корня репозитория esbok/")
        print("   Ожидается структура: esbok/books/")
        return

    if os.path.exists(TEMPLATE_DIR):
        print(f"⚠️ Директория '{TEMPLATE_DIR}' уже существует.")
        answer = input("   Перезаписать файлы шаблона? [y/N]: ").strip().lower()
        if answer != "y":
            print("Отменено.")
            return

    created = 0
    for rel_path, content in FILES.items():
        full_path = os.path.join(TEMPLATE_DIR, rel_path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(content)
        created += 1

    # Права на директории
    for root, dirs, _ in os.walk(TEMPLATE_DIR):
        for d in dirs:
            os.chmod(os.path.join(root, d), 0o755)

    print(f"✅ Создана директория '{TEMPLATE_DIR}/' ({created} файлов)")
    print()
    print("📋 Следующие шаги:")
    print(f"   1. Скопируйте шаблон для новой книги:")
    print(f"      cp -r {TEMPLATE_DIR} books/<название-книги>")
    print(f"   2. Или используйте make-цель:")
    print(f"      make init-book")
    print(f"   3. Отредактируйте books/<название-книги>/book.adoc")
    print(f"   4. Добавьте книгу в .github/workflows/ci-build.yml (matrix.book)")


if __name__ == "__main__":
    create_template()
