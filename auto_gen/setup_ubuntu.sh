#!/usr/bin/env bash
#  =============================================================================
# ESBOK — Установка полного набора инструментов на Ubuntu/Debian
# =============================================================================
# Использование:
#   ./setup_ubuntu.sh              # Полная установка
#   ./setup_ubuntu.sh --minimal    # Только базовые инструменты (без Node.js)
#   ./setup_ubuntu.sh --check      # Только проверка установленных компонентов
# =============================================================================

set -euo pipefail

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Режим установки
MODE="full"
if [[ "${1:-}" == "--minimal" ]]; then
    MODE="minimal"
elif [[ "${1:-}" == "--check" ]]; then
    MODE="check"
fi

# Версия Ruby (рекомендуемая)
RUBY_VERSION="3.3"

# =============================================================================
# Вспомогательные функции
# =============================================================================

log_info()    { echo -e "${BLUE}[INFO]${NC} $*"; }
log_success() { echo -e "${GREEN}[OK]${NC} $*"; }
log_warn()    { echo -e "${YELLOW}[WARN]${NC} $*"; }
log_error()   { echo -e "${RED}[ERROR]${NC} $*"; }
log_header()  { echo -e "\n${CYAN}=== $* ===${NC}"; }

require_sudo() {
    if [[ $EUID -ne 0 ]]; then
        log_error "Скрипт требует права sudo. Запустите с sudo или как root."
        exit 1
    fi
}

check_os() {
    if [[ ! -f /etc/os-release ]]; then
        log_error "Не удалось определить операционную систему."
        exit 1
    fi
    
    . /etc/os-release
    if [[ "$ID" != "ubuntu" && "$ID" != "debian" && "$ID_LIKE" != *"debian"* ]]; then
        log_warn "Скрипт предназначен для Ubuntu/Debian. Ваша ОС: $ID"
        read -p "Продолжить? [y/N] " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
    
    log_success "ОС: $PRETTY_NAME"
}

# Проверка, установлен ли пакет
is_installed() {
    command -v "$1" >/dev/null 2>&1
}

# Установка системных пакетов (идемпотентно)
install_apt_packages() {
    local packages=("$@")
    local to_install=()
    
    for pkg in "${packages[@]}"; do
        if dpkg -l "$pkg" 2>/dev/null | grep -q "^ii"; then
            log_success "$pkg уже установлен"
        else
            to_install+=("$pkg")
        fi
    done
    
    if [[ ${#to_install[@]} -gt 0 ]]; then
        log_info "Установка: ${to_install[*]}"
        apt-get update -qq
        DEBIAN_FRONTEND=noninteractive apt-get install -y -qq "${to_install[@]}"
        log_success "Пакеты установлены"
    else
        log_info "Все системные пакеты уже установлены"
    fi
}

# =============================================================================
# Шаг 1: Проверка ОС и прав
# =============================================================================

check_os

if [[ "$MODE" == "check" ]]; then
    log_header "Проверка установленных компонентов"
else
    require_sudo
    log_header "Установка инструментов ESBOK (режим: $MODE)"
fi

# =============================================================================
# Шаг 2: Системные пакеты
# =============================================================================

log_header "Системные пакеты"

BASE_PACKAGES=(
    build-essential
    curl
    wget
    git
    make
    unzip
    dos2unix
    jq
)

FONT_PACKAGES=(
    fonts-paratype
    fonts-firacode
    fonts-noto
)

OPTIONAL_PACKAGES=(
    inkscape
    entr
    python3
    python3-pip
    python3-venv
    nodejs
    npm
)

install_apt_packages "${BASE_PACKAGES[@]}"
install_apt_packages "${FONT_PACKAGES[@]}"

if [[ "$MODE" == "full" ]]; then
    install_apt_packages "${OPTIONAL_PACKAGES[@]}"
else
    log_info "Режим minimal — пропускаем Node.js, Inkscape, entr"
fi

# =============================================================================
# Шаг 3: Ruby и gems
# =============================================================================

log_header "Ruby и gems"

if ! is_installed ruby; then
    log_info "Установка Ruby $RUBY_VERSION..."
    apt-get install -y -qq "ruby$RUBY_VERSION" "ruby$RUBY_VERSION-dev"
    update-alternatives --set ruby "/usr/bin/ruby$RUBY_VERSION" 2>/dev/null || true
    log_success "Ruby установлен"
else
    log_success "Ruby уже установлен: $(ruby --version)"
fi

if ! is_installed gem; then
    log_error "gem не найден. Установите ruby-dev."
    exit 1
fi

# Гемы для сборки
GEMS=(
    asciidoctor
    asciidoctor-pdf
    asciidoctor-diagram
    rouge
    bundler
)

for gem_name in "${GEMS[@]}"; do
    if gem list "$gem_name" -i >/dev/null 2>&1; then
        log_success "gem '$gem_name' уже установлен"
    else
        log_info "Установка gem '$gem_name'..."
        gem install "$gem_name" --no-document
        log_success "gem '$gem_name' установлен"
    fi
done

# Опциональные гемы для качества кода (только full режим)
if [[ "$MODE" == "full" ]]; then
    for gem_name in html-proofer yaspeller; do
        if gem list "$gem_name" -i >/dev/null 2>&1; then
            log_success "gem '$gem_name' уже установлен"
        else
            log_info "Установка gem '$gem_name' (опционально)..."
            gem install "$gem_name" --no-document 2>/dev/null && \
                log_success "gem '$gem_name' установлен" || \
                log_warn "Не удалось установить '$gem_name' (не критично)"
        fi
    done
fi

# =============================================================================
# Шаг 4: Node.js и Mermaid CLI (только full режим)
# =============================================================================

if [[ "$MODE" == "full" ]]; then
    log_header "Node.js и Mermaid CLI"
    
    if ! is_installed node; then
        log_error "Node.js не установлен. Проверьте установку пакетов выше."
        exit 1
    fi
    
    log_success "Node.js: $(node --version)"
    log_success "npm: $(npm --version)"
    
    if ! is_installed mmdc; then
        log_info "Установка @mermaid-js/mermaid-cli..."
        npm install -g @mermaid-js/mermaid-cli
        log_success "Mermaid CLI установлен"
    else
        log_success "Mermaid CLI уже установлен: $(mmdc --version)"
    fi
else
    log_header "Node.js и Mermaid CLI"
    log_info "Пропущено (режим minimal)"
fi

# =============================================================================
# Шаг 5: Проверка шрифтов
# =============================================================================

log_header "Шрифты"

check_font() {
    local family="$1"
    if fc-list :family="$family" >/dev/null 2>&1; then
        local count
        count=$(fc-list :family="$family" | wc -l)
        log_success "$family: найдено $count начертаний"
    else
        log_warn "$family не найден в системе"
        log_info "  Установите: sudo apt install fonts-..."
        log_info "  Или используйте локальные шрифты в shared/fonts/"
    fi
}

check_font "PT Serif"
check_font "Fira Code"
check_font "Noto Serif"

# =============================================================================
# Шаг 6: Проверка AsciiDoctor
# =============================================================================

log_header "Проверка AsciiDoctor"

if is_installed asciidoctor; then
    log_success "asciidoctor: $(asciidoctor --version | head -1)"
else
    log_error "asciidoctor не найден"
    exit 1
fi

if is_installed asciidoctor-pdf; then
    log_success "asciidoctor-pdf: $(asciidoctor-pdf --version | head -1)"
else
    log_error "asciidoctor-pdf не найден"
    exit 1
fi

# Проверка asciidoctor-diagram
if ruby -e "require 'asciidoctor-diagram'" 2>/dev/null; then
    log_success "asciidoctor-diagram: доступен"
else
    log_warn "asciidoctor-diagram: недоступен (Mermaid-диаграммы не будут рендериться)"
fi

# =============================================================================
# Шаг 7: Итоговая проверка
# =============================================================================

log_header "Итоговая проверка"

echo ""
echo "Компонент              | Статус"
echo "-----------------------|-------"

for cmd in ruby gem asciidoctor asciidoctor-pdf make git python3; do
    if is_installed "$cmd"; then
        printf "%-22s | ${GREEN}✓${NC} %s\n" "$cmd" "$($cmd --version 2>&1 | head -1 | cut -c1-30)"
    else
        printf "%-22s | ${RED}✗${NC} не установлен\n" "$cmd"
    fi
done

if [[ "$MODE" == "full" ]]; then
    for cmd in node npm mmdc inkscape; do
        if is_installed "$cmd"; then
            printf "%-22s | ${GREEN}✓${NC} %s\n" "$cmd" "$($cmd --version 2>&1 | head -1 | cut -c1-30)"
        else
            printf "%-22s | ${YELLOW}○${NC} опционально\n" "$cmd"
        fi
    done
fi

echo ""
log_success "Установка завершена!"
echo ""
log_info "Следующие шаги:"
echo "  1. cd в корень репозитория esbok/"
echo "  2. ./build.sh <название-книги>"
echo "  3. Или: make build BOOK=<название-книги>"
echo ""
log_info "Полезные команды:"
echo "  make help          — список целей Makefile"
echo "  make list-books    — список книг в репозитории"
echo "  make init-book     — создать новую книгу из шаблона"
echo "  make check         — проверка окружения"
