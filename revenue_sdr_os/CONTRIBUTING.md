# Contributing

Obrigado por considerar contribuir com o Revenue SDR OS! Este documento cobre como reportar bugs, sugerir features, e submeter mudancas.

## Reportando Bugs

Abra uma issue no GitHub com:

1. **Descricao clara** do bug
2. **Passos para reproduzir**
3. **Comportamento esperado vs observado**
4. **Screenshots** (se aplicavel)
5. **Ambiente**: OS, Python version, etc.

## Sugerindo Features

Abra uma issue com a tag `enhancement` descrevendo:

1. **Problema** que a feature resolve
2. **Solucao proposta**
3. **Alternativas** consideradas
4. **Impacto** esperado

## Submetendo Mudancas

### Setup de desenvolvimento

```bash
git clone https://github.com/Fernando-DaSilva/Revenue_SDR_OS.git
cd Revenue_SDR_OS
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python scripts/seed.py
```

### Workflow

1. **Fork** o repo
2. Crie uma **branch** a partir de `main`:
   ```bash
   git checkout -b feature/minha-feature
   ```
3. **Commit** suas mudancas seguindo [Conventional Commits](https://www.conventionalcommits.org/):
   ```bash
   git commit -m "feat: adiciona nova feature"
   git commit -m "fix: corrige bug X"
   git commit -m "docs: atualiza README"
   ```
4. **Push** para sua branch:
   ```bash
   git push origin feature/minha-feature
   ```
5. Abra um **Pull Request** no GitHub

### Convencoes de codigo

- **Python**: PEP 8 + type hints
- **Commits**: Conventional Commits
- **Tests**: pytest, coverage > 80%
- **Docstrings**: Google style
- **Branches**: `feature/`, `fix/`, `docs/`, `chore/`

### Pre-commit

Antes de commitar:

```bash
pytest tests/
ruff check app/ tests/
ruff format --check app/ tests/
```

## Estrutura do projeto

Veja [FOUNDATION.md](FOUNDATION.md) para entender a visao geral.

---

## Code of Conduct

Seja respeitoso, inclusivo, e profissional. Nao toleramos assedio ou discriminacao.

## Duvidas?

Abra uma issue ou entre em contato via team@myraos.com.