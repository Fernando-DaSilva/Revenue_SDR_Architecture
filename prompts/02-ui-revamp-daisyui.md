# PROMPT / SCRIPT: Revamp de UI com Tailwind CSS e DaisyUI (Sprint 00 / 01)

Este script deve ser lido e executado pelo **Agente de Codificação** encarregado de elevar a estética e modernização do UI da aplicação. A adoção desta stack (Tailwind CSS + DaisyUI) reflete as diretrizes arquiteturais atualizadas no **ADR-001**.

> **ATENÇÃO AGENTE:** O objetivo não é mudar a lógica do backend (FastAPI) e sim **reconstruir visualmente** o projeto, trocando o "CSS puro" por componentes profissionais do DaisyUI.

## 1. Contexto e Ferramentas

O Revenue SDR OS usa Jinja2 + HTMX + Alpine.js. Não adicionaremos React/Vue/Node.js no servidor de produção.

- **Tailwind CSS**: Será utilizado para utilitários de layout e espaçamento. Você deve usar a versão via Standalone CLI (`tailwindcss` binário) para não depender de Node.js no ambiente de produção.
- **DaisyUI**: Será o plugin oficial do Tailwind para fornecer componentes lindíssimos e prontos (botões, modais, cards, formulários). **Preço: 100% gratuito e open-source (+41k stars no Github).**

## 2. Tarefas do Agente (Step-by-Step)

### Etapa 1: Instalação
1. Configure o CLI do Tailwind localmente no repositório de desenvolvimento (Node.js/npm é permitido apenas no ambiente de **build/dev**, garantindo que o bundle final será um arquivo CSS gerado estaticamente para produção).
2. Rode `npm init -y` e `npm install -D tailwindcss postcss autoprefixer daisyui`.
3. Inicialize o `tailwind.config.js`.

### Etapa 2: Configuração do `tailwind.config.js`
Você deve configurar o Tailwind para escanear todos os arquivos HTML (`app/web/templates/**/*.html`, `app/web/pages/**/*.html` e arquivos python que possam injetar HTML via HTMX).

```javascript
/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./app/web/templates/**/*.html",
    "./app/web/pages/**/*.html"
  ],
  theme: {
    extend: {},
  },
  plugins: [
    require('daisyui'),
  ],
  daisyui: {
    // Definir os temas do DaisyUI que alinham com o ADR-013 (White-label)
    themes: ["light", "dark", "corporate", "luxury", "black"], 
  },
}
```

### Etapa 3: Integração White-label (ADR-013)
Conecte o sistema dinâmico de cores de tenant do Revenue SDR OS com o motor de variáveis CSS do DaisyUI.
O DaisyUI automaticamente escuta as tags `data-theme="luxury"` na tag `<html>`. Configure o `templating.py` (Jinja2 render) para injetar dinamicamente esse atributo conforme o tenant atual.

### Etapa 4: Componentização (Refatoração de UI)
1. **Layout e Navbar**: Refatore o `base.html`. Utilize os componentes de [Navbar](https://daisyui.com/components/navbar/) e [Drawer](https://daisyui.com/components/drawer/) do DaisyUI.
2. **Botões e Inputs**: Remova CSS inline e classes antigas. Aplique estritamente as classes `btn btn-primary`, `input input-bordered`, `select select-ghost`, etc.
3. **Cards (Leads/Memories)**: Use a estrutura semântica `.card` (ex: `card bg-base-100 shadow-xl`) para exibir o funil e a listagem de Leads.
4. **Modais (HTMX + Alpine)**: Utilize o `.modal` do DaisyUI integrado ao `<dialog>` nativo ou manipulado pelo HTMX via Alpine.js.

### 3. Validação de Qualidade
- [ ] O app continua a rodar offline, sem chamadas a CDNs externos no HTML renderizado? (Se usar o standalone CLI para buildar o CSS, tudo deve ficar vendored na pasta `static`).
- [ ] A reatividade do HTMX quebra a estilização? (Não deve, pois as classes do Tailwind já estarão compiladas no bundle CSS base).
- [ ] O layout transmite uma experiência "Premium e State of the art"? Se a resposta for "parece um MVP simples", você DEVE melhorar e aprimorar o uso de cores, gradientes e estados de hover (`hover:bg-primary-focus`).

---
**Comando final esperado para gerar o bundle em desenvolvimento:**
`npx tailwindcss -i ./app/web/static/css/input.css -o ./app/web/static/css/output.css --watch`
