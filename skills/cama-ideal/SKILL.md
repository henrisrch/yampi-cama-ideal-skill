---
name: cama-ideal
description: Cadastrar, revisar e ajustar as "Camas Ideais" de uma loja Yampi (tema Rocket) — subcategoria, capa, produtos, resumo, bloco "O que transforma…" e as marcações "+" na foto (posição no computador e no celular). Use quando alguém da equipe pedir para criar uma cama nova, ver o que falta numa cama, posicionar/mover os "+" da foto, colar "Salvar marcações da Cama …" vindo da ferramenta, ou conferir a página da Cama Ideal.
---

# Cama Ideal — cadastro guiado

Quem usa esta skill é a equipe da loja, não necessariamente técnica. **Responda sempre em português (pt-BR)** — toda mensagem, inclusive confirmações curtas, tabelas e resumos, mesmo que as saídas dos comandos ou o contexto técnico estejam em inglês. Fale de forma simples, um passo por vez, e **sempre comece lendo o estado real** (loja + tema) — nunca responda de memória.

## Onde mora cada coisa

**Na Yampi (admin / API de catálogo)** — vale na hora, sem publicar o tema:
- A página **Cama Ideal** é a categoria raiz (slug atual `cama-do-mes`). Cada **cama** é uma **subcategoria** dela.
- **Foto da cama**: capa da subcategoria (`category_cover`); sem capa, um banner com o mesmo slug da subcategoria.
- **Destaque** na lista: subcategoria marcada como destaque (sem nenhuma, vale a primeira).
- **Peças**: os produtos da subcategoria.
- **Descrição da subcategoria**: 1º parágrafo = **resumo**; depois o **"O que transforma…"** — um título (H2/H3) com a pergunta e, em cada item, um parágrafo começando pelo nome do item em negrito:
  ```html
  <h3>O que transforma seu quarto em um hotel de luxo?</h3>
  <p><strong>Toque fresco</strong> Percal 400 fios…</p>
  ```

**No código da loja (tema)** — vale no preview ao enviar e na loja **só ao publicar o tema**:
- **Marcações "+" na foto**: `<THEME_DIR>/elements/cama-ideal-marcacoes.twig` (`THEME_DIR`, padrão `tema`), um JSON por cama:
  ```json
  "cama-do-mes-exemplo": [
      { "produto": "colcha-exemplo", "x": 13, "y": 37.7, "mx": 12, "my": 40 }
  ]
  ```
  `x,y` = computador, `mx,my` = celular (opcional), em % da foto (0 = esquerda/topo, 100 = direita/base). Só aparece "+" para produto que está na subcategoria.
- **Não** coloque marcações na descrição da categoria: a Yampi apaga `<section>` e atributos `data-*` ao salvar (comprovado em 12/11/2026 — sobraram só os nomes como texto solto na página).
- A foto tem a mesma proporção no computador (634×740) e no celular (402×469); a posição de celular serve quando o "+" (32 px fixo) cobre algo importante na tela menor.
- Leitura no componente: `components/cama-ideal/CamaIdealDetail.vue` (prop `hotspots-by-slug`, passada por `sections/category/cama_ideal_content.twig`).

## Ferramentas

Rode da raiz do repositório (credenciais em `.env` — veja `.env.example`; nunca mostre nem registre credenciais).

| Comando | O que faz |
|---|---|
| `scripts/cama-ideal status` | Todas as camas: produtos, marcações, link do preview e pendências |
| `scripts/cama-ideal ver <slug>` | Detalhe: capa, resumo, "O que transforma", produtos com posição |
| `scripts/cama-ideal pontos <slug>` | Marcações atuais da cama (JSON) |
| `scripts/cama-ideal salvar-pontos <arquivo>` | **Simulação**: antes/depois e a mudança no arquivo do tema |
| `… salvar-pontos <arquivo> --aplicar` | Grava no arquivo local, envia ao **preview** e relê |
| `scripts/cama-ideal tirar-pontos <slug> [--aplicar]` | Remove as marcações da cama |

`<arquivo>` é o texto copiado da ferramenta (ou `-` para ler da entrada). `--raiz <slug>` troca a categoria raiz. O script recusa salvar se o arquivo local estiver diferente do preview — nesse caso, investigue antes (não sobrescreva).

**Ferramenta para a pessoa marcar**: `ferramentas/cama-ideal-pontos.html`. Abrir no navegador dela (no WSL: `cd /mnt/c && cmd.exe /c start "" "$(wslpath -w <repo>/ferramentas/cama-ideal-pontos.html)"`). Passo a passo sem termos técnicos, só leituras públicas:
1. **Escolher a cama** — cards com foto e quantas peças já têm "+" (lidas do arquivo do tema no preview).
2. **Marcar as peças** — uma peça por vez, Computador/Celular, arrastar, "não aparece na foto", Desfazer, rascunho automático.
3. **Enviar** — "Copiar marcações" copia um texto "Salvar marcações da Cama X (slug): {json}" para colar aqui.

## Fluxos

### "O que falta?" / revisar
1. `scripts/cama-ideal status` (ou `ver <slug>`).
2. Explique cada ⚠ em linguagem simples e diga onde se resolve (admin da Yampi ou aqui).

### Cama nova
1. `status` para evitar duplicata (compare nomes e slugs).
2. No **admin da Yampi** (a equipe faz): Catálogo → Categorias → nova subcategoria dentro de **Cama Ideal**, com nome, slug curto, ativa, capa (foto da cama) e destaque se for a cama da vez. Vincule os produtos.
3. Monte com a pessoa o **resumo** e o **"O que transforma…"** (pergunta + 3–5 itens). Não invente características de produto.
4. `ver <slug>` para confirmar subcategoria, produtos e capa.
5. Siga "Marcar os +".

### Marcar ou mover os "+"
1. Abra a ferramenta para a pessoa. Ela escolhe a cama, marca, confere no Celular e clica em **Copiar marcações**.
2. Quando ela colar aqui "Salvar marcações da Cama …": salve o texto num arquivo temporário (fora do repositório) e rode a **simulação**. Mostre em linguagem simples o antes/depois e os avisos (peça fora da cama etc.) e descreva onde cada "+" cai na foto.
3. **Só rode `--aplicar` depois de a pessoa confirmar explicitamente.** Isso altera o tema no preview.
4. Confira a página da cama no preview (link do `status`) em computador e celular: "+" no lugar e card do produto abrindo.
5. Diga claramente: **na loja publicada só aparece quando o tema for publicado.** Publicar envia o preview inteiro — antes, confira o que mais está pendente no preview e peça autorização explícita. Não publique por conta própria.
6. Faça commit do `elements/cama-ideal-marcacoes.twig` e registre a mudança no controle do projeto (sem credenciais).

## Cuidados

- Escrita só com confirmação explícita, uma vez. Se a releitura não bater, não repita: mostre o resultado e investigue.
- Nunca apague subcategoria nem produto por esta skill. Para tirar um "+", marque a peça como "não aparece na foto" na ferramenta ou use `tirar-pontos`.
- `scripts/yampi-catalog-request` e `scripts/yampi-store-file` só escrevem na loja definida em `YAMPI_ALLOWED_ALIAS` (normalmente a loja de teste). Para a loja oficial, o desenvolvedor precisa configurar; não contorne.
