---
name: cama-ideal
description: Cadastrar, revisar e ajustar as "Camas Ideais" de uma loja Yampi (tema Rocket) — subcategoria, capa, produtos, resumo, bloco "O que transforma…" e as marcações "+" na foto (posição no computador e no celular). Use quando alguém da equipe pedir para criar uma cama nova, ver o que falta numa cama, posicionar/mover os "+" da foto, editar textos/foto/peças de uma cama, colar "Salvar marcações da Cama …", "Criar cama nova …" ou "Salvar alterações da cama …" vindo da ferramenta, ou conferir a página da Cama Ideal.
---

# Cama Ideal — cadastro guiado

Quem usa esta skill é a equipe da loja, não necessariamente técnica. **Responda sempre em português (pt-BR)** — toda mensagem, inclusive confirmações curtas, tabelas e resumos, mesmo que as saídas dos comandos ou o contexto técnico estejam em inglês. Fale de forma simples, um passo por vez, e **sempre comece lendo o estado real** (loja + tema) — nunca responda de memória.

## Sempre pela ferramenta HTML

**Toda vez que a pessoa quiser criar uma cama, editar textos, foto ou peças de uma cama, ou marcar/mover os "+", abra a ferramenta `ferramentas/cama-ideal-pontos.html` no navegador dela e diga o que fazer lá** — não colete os dados pela conversa nem peça para ela editar JSON. Abrir (WSL):

```sh
xdg-open "ferramentas/cama-ideal-pontos.html?loja=<alias>"          # Linux
open "ferramentas/cama-ideal-pontos.html"                            # macOS
cd /mnt/c && cmd.exe /c start "" "$(wslpath -w "$PWD/ferramentas/cama-ideal-pontos.html")"   # WSL
```

Se não abrir, mande o caminho do arquivo para ela abrir no navegador. A ferramenta só faz leituras públicas e não grava nada: ela gera um texto ("Criar cama nova …", "Salvar alterações da cama …" ou "Salvar marcações da …") que a pessoa cola aqui, e você simula e só grava depois da confirmação.

## Onde mora cada coisa

**Na Yampi (admin / API de catálogo)** — vale na hora, sem publicar o tema:
- A página **Cama Ideal** é a categoria raiz (slug atual `cama-do-mes`). Cada **cama** é uma **subcategoria** dela.
- **Foto da cama**: capa da subcategoria (`category_cover`); sem capa, um banner com o mesmo slug da subcategoria. Na cama nova, a pessoa sobe a foto como banner e o `criar` copia a imagem dele para a capa.
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
| `scripts/cama-ideal criar <arquivo.json>` | **Simulação** da cama nova: textos, capa, ordem, destaque e produtos, com avisos |
| `… criar <arquivo.json> --aplicar` | Cria a subcategoria (ou altera, se o slug já for uma cama), grava a capa se mudou, põe e tira produtos para ficar igual à ficha e relê tudo. `editar` é o mesmo comando |

`<arquivo>` é o texto copiado da ferramenta (ou `-` para ler da entrada). `--raiz <slug>` troca a categoria raiz. O script recusa salvar se o arquivo local estiver diferente do preview — nesse caso, investigue antes (não sobrescreva).

**Ferramenta da equipe**: `ferramentas/cama-ideal-pontos.html` (veja "Sempre pela ferramenta HTML"). Sem termos técnicos, só leituras públicas:
- **Nova cama** (último card da lista): ficha em 5 passos numerados. (1) Nome — o endereço/slug é gerado e só muda em "Mudar o endereço". (2) Foto — passo a passo para criar um **banner** no painel (Loja Virtual → Banners → + Novo banner; Nome = nome da cama, com botão "Copiar nome"; imagem JPG de pé, 634×740; ativo; Salvar; link do [artigo da Yampi](https://help.yampi.com.br/pt-BR/articles/6067123-como-criar-e-configurar-um-banner-na-loja-virtual-da-yampi)). "Buscar a foto" lê os banners públicos e associa sozinho o que tem o mesmo nome/slug; sem correspondência, mostra os 8 banners mais recentes para clicar. (3) Peças — busca por nome e "Adicionar" (alternativa: colar links). (4) Resumo, pergunta, 3–5 motivos e destaque. (5) "Copiar ficha" → "Criar cama nova Nome (slug): {json}". Mostra o que falta, avisa nome/endereço repetido e guarda rascunho.
- **Editar textos, foto e peças** (link embaixo de cada cama, e no topo do passo de marcar): a mesma ficha, preenchida com o que está na loja — nome, foto atual, peças da cama, resumo, pergunta e motivos (lidos da descrição com a mesma regra da página; motivo com vários parágrafos vira texto com linha em branco). O endereço não muda. "Tirar" uma peça a tira da cama. O botão só libera quando algo mudou; rascunho por cama, com opção de voltar ao que está na loja. Se a descrição atual estiver fora do formato, a ficha avisa e mostra o texto original. Copia "Salvar alterações da cama Nome (slug): {json}".
- **Marcações**, em três passos:
1. **Escolher a cama** — cards com foto e quantas peças já têm "+" (lidas do arquivo do tema no preview).
2. **Marcar as peças** — uma peça por vez, Computador/Celular, arrastar, "não aparece na foto", Desfazer, rascunho automático.
3. **Enviar** — "Copiar marcações" copia um texto "Salvar marcações da Cama X (slug): {json}" para colar aqui.

## Fluxos

### "O que falta?" / revisar
1. `scripts/cama-ideal status` (ou `ver <slug>`).
2. Explique cada ⚠ em linguagem simples e diga onde se resolve (admin da Yampi ou aqui).

### Cama nova
1. `status` para evitar duplicata (compare nomes e slugs).
2. **Abra a ferramenta** e peça para a pessoa clicar em **Nova cama** (último card) e seguir os 5 passos. Ela só precisa ter em mãos a foto da cama (arquivo JPG), saber quais produtos entram e os textos. A foto ela sobe como banner no painel, guiada pelo passo 2; não peça link de imagem. Se a ferramenta não achar o banner, pode ser o cache da Yampi (até alguns minutos): peça para tentar de novo. Ajude com o resumo e os motivos se ela pedir, sem inventar características de produto.
3. Quando ela colar "Criar cama nova …": salve o texto num arquivo temporário **fora do repositório** e rode `scripts/cama-ideal criar <arquivo>` (simulação). Mostre em linguagem simples como fica e explique cada ⚠: produto não encontrado bloqueia; capa que não abre como imagem bloqueia; outra cama em destaque, ajustar no admin. Para corrigir algo, ela ajusta na ferramenta (o rascunho fica salvo) e copia de novo.
4. **Só rode `--aplicar` depois de a pessoa confirmar explicitamente.** Ele grava na Yampi (vale na hora na loja, sem publicar o tema): cria a subcategoria dentro de Cama Ideal com nome, slug, descrição, ordem (depois da última), destaque e ativa; grava a capa; vincula cada produto e relê tudo. Se a releitura apontar diferença, **pare e não reenvie**.
5. `ver <slug>` para confirmar e abra a página (link do `status`) no preview em computador e celular.
6. Peça para ela voltar à ferramenta (recarregar), escolher a cama nova e marcar os "+" — siga "Marcar os +". A cama aparece na loja mesmo sem marcações; o tema não precisa mudar para uma cama nova.

Sem a ferramenta (equipe técnica): copie `skills/cama-ideal/modelo-cama-nova.json` para fora do repositório, preencha e rode o mesmo `criar`.

### Editar uma cama (textos, foto, peças)
1. **Abra a ferramenta** e peça para a pessoa clicar em **Editar textos, foto e peças** embaixo da cama, mudar o que precisar e clicar em **Copiar alterações**.
2. Quando ela colar "Salvar alterações da cama …": salve num arquivo temporário fora do repositório e rode `scripts/cama-ideal editar <arquivo>` (simulação). Explique em linguagem simples o que muda: textos (antes/depois — resuma a diferença, não cole HTML), foto ("a mesma de hoje" ou nova), peças que entram e que **saem** (o produto não é apagado, só sai da cama). Se aparecer "Textos: sem mudança", diga isso.
3. **Só rode `--aplicar` depois da confirmação explícita.** Vale na hora na loja. Releitura com diferença → pare e não reenvie.
4. Confira a página da cama no preview. Se saiu peça que tinha "+", ele some sozinho; se entrou peça nova, ofereça marcar o "+".

Como a vinculação funciona: a API não tem rota para "pôr produto na categoria"; o script lê o produto com `?include=brand,texts,seo,extras,categories,variations,collections,skus` (o include aceita `.` para descer um nível, ex.: `skus.images`), reenvia o produto inteiro com a categoria somada **sem `skus`** (assim os SKUs ficam intactos) e compara a releitura campo a campo. Limite conhecido: `buy_similars` não aparece em nenhum include, então não é reenviado nem conferido.

### Marcar ou mover os "+"
1. **Abra a ferramenta** para a pessoa. Ela escolhe a cama, marca, confere no Celular e clica em **Copiar marcações**.
2. Quando ela colar aqui "Salvar marcações da Cama …": salve o texto num arquivo temporário (fora do repositório) e rode a **simulação**. Mostre em linguagem simples o antes/depois e os avisos (peça fora da cama etc.) e descreva onde cada "+" cai na foto.
3. **Só rode `--aplicar` depois de a pessoa confirmar explicitamente.** Isso altera o tema no preview.
4. Confira a página da cama no preview (link do `status`) em computador e celular: "+" no lugar e card do produto abrindo.
5. Diga claramente: **na loja publicada só aparece quando o tema for publicado.** Publicar envia o preview inteiro — antes, confira o que mais está pendente no preview e peça autorização explícita. Não publique por conta própria.
6. Faça commit do `elements/cama-ideal-marcacoes.twig` e registre a mudança no controle do projeto (sem credenciais).

## Cuidados

- Escrita só com confirmação explícita, uma vez. Se a releitura não bater, não repita: mostre o resultado e investigue.
- Nunca apague subcategoria nem produto por esta skill. Tirar um produto de uma cama (pela ficha de edição) só remove a categoria dele, relendo e comparando o produto inteiro. Para tirar um "+", marque a peça como "não aparece na foto" na ferramenta ou use `tirar-pontos`.
- `scripts/yampi-catalog-request` e `scripts/yampi-store-file` só escrevem na loja definida em `YAMPI_ALLOWED_ALIAS` (normalmente a loja de teste). Para a loja oficial, o desenvolvedor precisa configurar; não contorne.
