# =============================================================================
# ESBOK — Embedded Systems Body of Knowledge
# Главный Makefile для управления серией книг
# =============================================================================

# Корень репозитория (абсолютный путь)
ROOT := $(CURDIR)

# Текущая книга (по умолчанию)
BOOK ?= embedded-basics

# Все директории книг (кроме _template)
BOOKS := $(filter-out books/_template,$(wildcard books/*))

# Директория вывода для текущей книги
DIST_DIR := dist/$(BOOK)

# Путь к book.adoc текущей книги
BOOK_ADOC := books/$(BOOK)/book.adoc

# Общие зависимости для всех книг
SHARED_DEPS := shared/themes/web.css shared/themes/pdf-theme.yml

# =============================================================================
# Цели по умолчанию
# =============================================================================
.PHONY: help dev build clean lint all init-book check list-books

help: ## Показать справку
	@echo "📚 ESBOK — управление серией книг"
	@echo ""
	@echo "Основные цели:"
	@echo "  make dev book=<name>         — live-сервер с автопересборкой"
	@echo "  make build book=<name>       — сборка HTML + PDF"
	@echo "  make build all               — сборка всех книг"
	@echo "  make clean                   — удалить dist/"
	@echo "  make lint                    — проверка синтаксиса и ссылок"
	@echo "  make init-book               — создать новую книгу из шаблона"
	@echo "  make list-books              — список всех книг"
	@echo "  make check                   — проверка окружения"
	@echo ""
	@echo "Пример:"
	@echo "  make dev book=embedded-basics"
	@echo "  make build book=power-management"

# =============================================================================
# Разработка (live-reload)
# =============================================================================
dev: ## Запустить live-сервер для книги
	@bash shared/scripts/dev-server.sh "books/$(BOOK)" 8080

# =============================================================================
# Сборка
# =============================================================================
build: $(DIST_DIR)/index.html ## Собрать HTML и PDF для книги

$(DIST_DIR)/index.html: $(BOOK_ADOC) $(SHARED_DEPS)
	@echo "📦 Сборка книги: $(BOOK)"
	@mkdir -p $(DIST_DIR)
	@mkdir -p $(DIST_DIR)/../../shared/themes
	@mkdir -p $(DIST_DIR)/../../shared/fonts
	@cp -r shared/themes/* $(DIST_DIR)/../../shared/themes/ 2>/dev/null || true
	@cp -r shared/fonts/* $(DIST_DIR)/../../shared/fonts/ 2>/dev/null || true
	@cp -r shared/vendor/* $(DIST_DIR)/../../shared/vendor/ 2>/dev/null || true
	@cd books/$(BOOK) && bundle install --quiet 2>/dev/null || bundle install
	@cd books/$(BOOK) && bundle exec asciidoctor \
		-b html5 -d book \
		-o ../../$(DIST_DIR)/index.html book.adoc
	@cd books/$(BOOK) && bundle exec asciidoctor-pdf \
		-o ../../$(DIST_DIR)/book.pdf book.adoc
	@echo "✅ Готово: $(DIST_DIR)/index.html + book.pdf"

# =============================================================================
# Очистка
# =============================================================================
clean: ## Удалить все артефакты сборки
	@echo "🧹 Очистка dist/..."
	@rm -rf dist/*
	@echo "✅ Очищено"

# =============================================================================
# Проверка качества
# =============================================================================
lint: ## Проверить синтаксис и ссылки
	@echo "🔍 Линтинг книги: $(BOOK)"
	@bash tools/validate-syntax.sh
	@bash tools/check-links.sh $(DIST_DIR)

# =============================================================================
# Сборка всех книг
# =============================================================================
all: ## Собрать все книги
	@echo "📚 Сборка всех книг..."
	@for b in $(BOOKS); do \
		if [ -f "$$b/book.adoc" ] && [ -f "$$b/Gemfile" ]; then \
			name=$$(basename $$b); \
			echo ""; \
			$(MAKE) build BOOK=$$name; \
		fi \
	done
	@echo ""
	@echo "🎉 Все книги собраны в dist/"

# =============================================================================
# Создание новой книги из шаблона
# =============================================================================
init-book: ## Создать новую книгу из _template (интерактивно)
	@read -p "📖 Название новой книги: " NAME; \
	SLUG=$$(echo "$$NAME" | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9]/-/g' | sed 's/--*/-/g' | sed 's/^-//' | sed 's/-$//'); \
	if [ -z "$$SLUG" ]; then \
		echo "❌ Ошибка: не удалось создать идентификатор"; \
		exit 1; \
	fi; \
	if [ -d "books/$$SLUG" ]; then \
		echo "❌ Директория books/$$SLUG уже существует"; \
		exit 1; \
	fi; \
	cp -r books/_template "books/$$SLUG"; \
	sed -i "s/= Название книги/= $$NAME/" "books/$$SLUG/book.adoc"; \
	echo ""; \
	echo "✅ Создана книга: books/$$SLUG/"; \
	echo ""; \
	echo "📋 Следующие шаги:"; \
	echo "   1. Отредактируйте books/$$SLUG/book.adoc"; \
	echo "   2. Напишите главы в books/$$SLUG/chapters/"; \
	echo "   3. Добавьте '$$SLUG' в matrix.book файла .github/workflows/ci-build.yml"; \
	echo "   4. Проверьте: make build book=$$SLUG"

# =============================================================================
# Вспомогательные цели
# =============================================================================
list-books: ## Показать список всех книг
	@echo "📚 Книги в репозитории:"
	@for b in $(BOOKS); do \
		if [ -f "$$b/book.adoc" ]; then \
			name=$$(basename $$b); \
			title=$$(grep -m1 "^= " "$$b/book.adoc" | sed 's/^= //'); \
			echo "  • $$name — $$title"; \
		fi \
	done

check: ## Проверить окружение
	@echo "🔍 Проверка окружения ESBOK..."
	@echo ""
	@for cmd in ruby python3 git make entr asciidoctor bundle node npm; do \
		if command -v $$cmd >/dev/null 2>&1; then \
			ver=$$($$cmd --version 2>&1 | head -1); \
			echo "  ✅ $$cmd: $$ver"; \
		else \
			echo "  ❌ $$cmd: не установлен"; \
		fi \
	done
	@echo ""
	@echo "🔤 Проверка шрифтов:"
	@if command -v fc-list >/dev/null 2>&1; then \
		count=$$(fc-list | grep -ciE "PT Serif|Fira Code" || true); \
		if [ "$$count" -gt 0 ]; then \
			echo "  ✅ Найдено семейств шрифтов: $$count"; \
		else \
			echo "  ⚠️  Шрифты PT Serif / Fira Code не найдены"; \
			echo "     Установите: sudo apt install fonts-pt-serif fonts-firacode"; \
		fi; \
	else \
		echo "  ⚠️  fc-list не найден — проверка шрифтов пропущена"; \
	fi

# =============================================================================
# Цели для CI/CD (используются в GitHub Actions)
# =============================================================================
ci-build: ## Сборка для CI (без копирования shared в dist)
	@mkdir -p $(DIST_DIR)
	@cd books/$(BOOK) && bundle install --quiet
	@cd books/$(BOOK) && bundle exec asciidoctor \
		-b html5 -d book \
		-o ../../$(DIST_DIR)/index.html book.adoc
	@cd books/$(BOOK) && bundle exec asciidoctor-pdf \
		-o ../../$(DIST_DIR)/book.pdf book.adoc

# =============================================================================
# Алиас для совместимости
# =============================================================================
.DEFAULT_GOAL := help
