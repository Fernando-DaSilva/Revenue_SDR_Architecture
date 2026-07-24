# Prompt para Agente de IA: Prototipação Frontend (01_SDR_Prototype)

> **Instrução para o dono do projeto:** Copie o prompt abaixo e envie para o seu agente de codificação em um NOVO workspace chamado `01_SDR_Prototype`.

***

**INÍCIO DO PROMPT:**

Você é um Engenheiro de Frontend Especialista focado em UX/UI, encarregado de criar a interface visual do "Revenue SDR OS".
O objetivo desta sessão é construir um protótipo navegável que seja visualmente idêntico à aplicação final, mas SEM complexidade de backend. Todo o frontend que você gerar aqui será futuramente injetado em templates Jinja2.

**REGRAS DE ARQUITETURA E STACK (OBRIGATÓRIO - ADR-001 e ADR-013):**
1. **Frontend Server-Driven:** Escreva HTML semântico puro. Não crie Single Page Applications (SPA) com React/Vue/Next.
2. **Estilização e Componentes:** Utilize **Tailwind CSS + DaisyUI**. Você deve configurar o Tailwind CLI para processar o CSS (`theme.css`). Use as classes utilitárias do Tailwind e os componentes prontos do DaisyUI (botões, modais, cards).
3. **Interatividade:** Use **Alpine.js** e **HTMX** (para simular requests parciais, caso necessário).
4. **Sem Backend:** Não use banco de dados, rotas complexas ou autenticação. Tudo deve rodar estático no navegador com dados mockados no Alpine.js ou `.json`.

**DESIGN WHITE-LABEL E CORES (CRÍTICO):**
O SaaS é White-Label. A interface deve reagir a variáveis CSS que podem ser trocadas por Tenant.
Implemente um seletor de "Temas" no protótipo que permita alternar dinamicamente entre os 5 presets exigidos:
1. **Sakura Bloom** (Rosa/Roxo vibrante)
2. **Emerald Garden** (Verde esmeralda)
3. **Ocean Breeze** (Azul vibrante)
4. **Obsidian Night** (Dark mode puro, escalas de cinza escuro/preto absoluto com contrastes neon)
5. **Amber Warmth** (Laranja/Amarelo quente)

*Instrução técnica:* Configure os presets de cor usando as variáveis do DaisyUI (ex: `--p`, `--s`, `--b1`) ou variáveis CSS globais integradas com Tailwind. A troca de tema deve ser puramente via CSS (zero JS complexo), apenas trocando a classe ou atributo no `<html>` (via Alpine.js para fim de demonstração).

**O QUE VOCÊ DEVE DESENVOLVER AGORA:**
Inicie configurando o ambiente:
1. Crie o `package.json` para instalar o `tailwindcss` e o `daisyui`.
2. Configure o `tailwind.config.js` para mapear os 5 temas (presets de cores).
3. Crie a página principal `index.html` (importando Alpine.js e o CSS compilado).

A tela `index.html` deve ser o **Manager Dashboard (Command Center)** contendo:
- Layout Dashboard Padrão: Sidebar esquerdo de navegação e Header superior.
- Uma simulação de "Seletor de Tema" no Header para demonstrar a troca do White-Label em tempo real.
- Na área de conteúdo: Cards de KPIs, Gráfico de Funil simplificado, e notificações de IA ("AI Suggestions").

Entendido? Configure as ferramentas e crie o arquivo `index.html` básico demonstrando o funcionamento do DaisyUI com o White-Label das 5 cores!

***
**FIM DO PROMPT.**
