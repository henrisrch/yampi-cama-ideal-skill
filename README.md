# Skill Cama Ideal — Yampi

Skill do Claude Code para cadastrar e revisar as "Camas Ideais" de uma loja Yampi
com tema Rocket. Uma Cama Ideal é uma subcategoria com foto, produtos, resumo e
marcações "+" sobre a foto, com posição para computador e para celular.

Feita para equipes não técnicas: a pessoa marca os "+" numa página HTML, cola o
resultado no Claude, e a skill simula, grava no preview e relê o que foi gravado.

## Conteúdo

| Caminho | O que é |
|---|---|
| `skills/cama-ideal/SKILL.md` | A skill. Copie para `.claude/skills/cama-ideal/` no repositório do tema. |
| `scripts/cama-ideal` | CLI: `status`, `ver`, `pontos`, `salvar-pontos`, `tirar-pontos`. Só simula, a menos que receba `--aplicar`. |
| `scripts/yampi-catalog-request` | Chamadas à API de catálogo. Só opera na loja definida em `YAMPI_ALLOWED_ALIAS`. |
| `scripts/yampi-store-file` | Leitura e escrita de arquivos do tema pela API oficial. Grava só no preview; publicar é um comando separado. |
| `ferramentas/cama-ideal-pontos.html` | Página para marcar os "+". Abra com `?loja=<alias>&raiz=<slug>`. Só faz leituras públicas. |
| `tema/elements/cama-ideal-marcacoes.twig` | Modelo do arquivo onde ficam as marcações. |

## Requisitos

- Python 3, bash e curl.
- `.env` na raiz, a partir de `.env.example`.
- Um tema que importe `elements/cama-ideal-marcacoes.twig` e desenhe os "+"
  na página da subcategoria. O componente de exibição não vem neste repositório.

## Por que as marcações ficam no tema

A Yampi remove `<section>` e atributos `data-*` da descrição da categoria quando
ela é salva. Por isso as marcações ficam num arquivo do tema, e não na descrição.
O efeito: valem no preview assim que enviadas, mas só chegam à loja publicada
quando o tema for publicado.

## Licença

MIT
