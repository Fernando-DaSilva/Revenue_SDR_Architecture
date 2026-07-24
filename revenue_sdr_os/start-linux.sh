#!/bin/bash
# Script de inicialização para Linux - Revenue SDR OS

echo "=================================================="
echo "🚀 Iniciando Revenue SDR OS no Linux"
echo "=================================================="

# Ir para a pasta do projeto (garantindo que estamos no local correto)
cd "$(dirname "$0")"

# Verificar se as dependências do npm estão instaladas
if [ ! -d "node_modules" ]; then
    echo "📦 Instalando dependências do npm..."
    npm install
fi

# 1. Compilar Tailwind CSS de forma estática (Frontend)
echo "🎨 Compilando o bundle CSS do Tailwind..."
npx @tailwindcss/cli -i ./app/web/static/css/input.css -o ./app/web/static/css/output.css

# 2. Iniciar o servidor Node.js/TypeScript (Backend & Middleware)
echo "🔌 Ativando servidor web..."
npm run dev
