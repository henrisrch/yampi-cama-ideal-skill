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
| `tema/components/cama-ideal/CamaIdealDetail.vue` | Página da cama: foto com os "+", card da peça, lista das peças com troca de tamanho e cor, e um botão que adiciona todas as marcadas à sacola. |
| `tema/components/generic/HotspotPosition.vue` | Põe o card do "+" do lado que cabe dentro da foto e recalcula no resize. |
| `tema/sections/category/cama_ideal_content.twig` | Exemplo de como chamar o componente na subcategoria. |
| `tema/assets/styles/sections/cama-ideal-page.scss` | Estilos da página (classes `rd-ci-*`). |

## Requisitos

- Python 3, bash e curl.
- `.env` na raiz, a partir de `.env.example`.
- Tema Rocket da Yampi. Para usar os componentes:
  - copie os arquivos de `tema/` para as mesmas pastas do seu tema;
  - registre `CamaIdealDetail.js` em `elements/scripts/components.twig` (a linha está no `.twig` de exemplo);
  - importe `cama-ideal-page.scss` na folha da página de categoria.
- O componente usa o que o Rocket já tem: `~/vuex` (ação de adicionar à sacola)
  e `@/modules/axios/api` (rotas `search/products` e `catalog/products/{slug}`).
- O SCSS usa mixins do tema (`desktop`, `mobile`, `rd-title`) e tokens de cor e
  fonte (`--roxo-*`, `--neutral-*`, `--brand-*`, `--lilas-01`, `--font-*`,
  `--fonts-texts-family`). Defina os seus ou troque pelos do seu tema.
- A imagem do checkbox vai na variável `--rd-ci-checkbox` (no exemplo,
  `assets/images/ci-checkbox.png`, que você precisa fornecer).

## Por que as marcações ficam no tema

A Yampi remove `<section>` e atributos `data-*` da descrição da categoria quando
ela é salva. Por isso as marcações ficam num arquivo do tema, e não na descrição.
O efeito: valem no preview assim que enviadas, mas só chegam à loja publicada
quando o tema for publicado.

## Licença

MIT
