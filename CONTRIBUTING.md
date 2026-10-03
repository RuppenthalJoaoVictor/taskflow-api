# Como contribuir

Obrigado pelo interesse em melhorar este projeto! Este documento explica como
reportar problemas, sugerir mudanças e enviar código.

## 🐛 Reportando bugs

Abra uma issue usando o template **Bug report** e inclua:

- **O que aconteceu** — o comportamento observado
- **O que você esperava** — o comportamento correto
- **Passos para reproduzir** — o menor caminho que reproduz o problema
- **Ambiente** — versão do Python, sistema operacional, e saída de `python --version`

## 💡 Sugerindo funcionalidades

Abra uma issue com o template **Feature request** explicando:

- **Problema** — o que hoje é difícil ou impossível
- **Solução proposta** — o que você imagina
- **Alternativas** — outras abordagens que você já pensou

Prefira descrever o **problema** antes da solução: isso abre espaço para uma
implementação diferente e melhor do que a que você imaginou.

## 🔧 Enviando código

1. **Fork** o repositório e crie um branch descritivo:

   ```bash
   git checkout -b feat/endpoint-de-relatorios
   ```

2. **Instale o ambiente** e confirme que está tudo funcionando:

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -e ".[dev]"
   pytest
   ```

3. **Escreva o código** seguindo o estilo do projeto:

   ```bash
   ruff format .      # formata
   ruff check --fix . # corrige o que dá
   mypy src           # verifica os tipos
   ```

4. **Escreva testes** para qualquer comportamento novo. O CI exige 100% de
   sucesso — um PR com teste faltando não passa.

5. **Commite seguindo [Conventional Commits](https://www.conventionalcommits.org/pt-br/)**:

   ```text
   feat: adiciona endpoint de relatórios
   fix: corrige cálculo de streak ao virar o mês
   test: cobre paginação com limite máximo
   docs: atualiza exemplo de requisição no README
   chore: atualiza dependências de desenvolvimento
   ```

6. **Abra o Pull Request** preenchendo o template.

### Antes de abrir o PR

 checklist local:

```bash
pytest              # todos os testes passando
ruff check .        # sem erros de lint
ruff format --check .
mypy src            # sem erros de tipo
```

O CI roda exatamente esses comandos em Python 3.12. Se passar localmente, passa lá.

## 📏 Critérios de aceitação de um PR

- [ ] O código tem testes cobrindo o comportamento novo ou corrigido
- [ ] Os testes falham sem a mudança (a mudança importa de fato)
- [ ] `ruff`, `mypy` e `pytest` passam localmente
- [ ] Docstrings e type hints presentes em funções públicas
- [ ] Nenhum segredo, `.env` ou dado real commitado
- [ ] O README foi atualizado se o comportamento público mudou

## 💬 Código de conduta

Seja respeitoso. Críticas devem ser sobre o **código**, nunca sobre a pessoa.
Assuma boa intenção e ajude o outro a melhorar.

## 📄 Licença

Ao contribuir, você concorda que sua contribuição seja licenciada sob a
[licença MIT](LICENSE) do projeto.