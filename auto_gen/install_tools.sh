# Базовые системные
sudo apt update
sudo apt install -y ruby ruby-dev python3 python3-pip git make curl unzip

# Live-reload
sudo apt install -y entr

# Графика и конвертеры
sudo apt install -y inkscape imagemagick graphviz

# Шрифты
sudo apt install -y fonts-pt-serif fonts-pt-sans fonts-firacode fonts-noto

# Asciidoctor (глобально или через Bundler — см. ниже)
sudo gem install asciidoctor asciidoctor-pdf asciidoctor-diagram rouge

# Node.js для Mermaid CLI (нужен для рендера диаграмм в PDF)
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install -y nodejs
sudo npm install -g @mermaid-js/mermaid-cli

# Проверка орфографии
sudo npm install -g yaspeller
