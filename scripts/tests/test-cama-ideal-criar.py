#!/usr/bin/env python3
"""Teste isolado (sem acesso à loja) do comando `scripts/cama-ideal criar`."""
import importlib.machinery
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
loader = importlib.machinery.SourceFileLoader('cama_ideal', str(ROOT / 'scripts' / 'cama-ideal'))
module_spec = importlib.util.spec_from_loader('cama_ideal', loader)
ci = importlib.util.module_from_spec(module_spec)
loader.exec_module(ci)


def expect_exit(spec, fragment):
    try:
        ci.validate_spec(spec)
    except SystemExit as error:
        assert fragment in str(error), (fragment, str(error))
        return
    raise AssertionError(f'esperava erro com {fragment!r}')


# modelo da skill é válido
model = json.loads((ROOT / 'skills/cama-ideal/modelo-cama-nova.json').read_text(encoding='utf-8'))
spec = ci.validate_spec(model)
assert spec['slug'] == 'cama-exemplo' and spec['ativa'] is True and spec['ordem'] is None and len(spec['itens']) == 3

# descrição no formato lido pelo tema, com escape
good = {'nome': 'Cama Teste', 'slug': 'cama-teste', 'resumo': 'Resumo <com> & "aspas".',
        'pergunta': 'O que transforma?', 'itens': [{'titulo': 'Toque & leveza', 'texto': 'Percal 400 fios.'}]}
description = ci.build_description(ci.validate_spec(good))
assert description == ('<p>Resumo &lt;com&gt; &amp; "aspas".</p><h3>O que transforma?</h3>'
                       '<p><strong>Toque &amp; leveza</strong> Percal 400 fios.</p>'), description
assert ci.description_parts(description) == ('Resumo <com> & "aspas".', 'O que transforma?', 1)
assert '<section' not in description and 'data-' not in description
assert ci.build_description(ci.validate_spec({'nome': 'A', 'slug': 'a', 'resumo': 'R'})) == '<p>R</p>'

# erros de preenchimento
expect_exit({**good, 'slug': 'Cama Teste'}, '"slug"')
expect_exit({**good, 'nome': ''}, '"nome"')
expect_exit({**good, 'resumo': ''}, '"resumo"')
expect_exit({**good, 'pergunta': ''}, '"pergunta" é obrigatória')
expect_exit({**good, 'itens': []}, '"pergunta" sem "itens"')
expect_exit({**good, 'itens': [{'titulo': 'x'}]}, 'item 1')
expect_exit({**good, 'capa': 'http://x/y.jpg'}, '"capa"')
expect_exit({**good, 'produtos': ['a', 'a']}, 'repetido')
expect_exit({**good, 'produtos': ['Produto X']}, 'inválidos')
expect_exit({**good, 'ordem': '2'}, '"ordem"')
expect_exit({**good, 'destaque': 'sim'}, '"destaque"')
expect_exit({**good, 'cor': 'azul'}, 'desconhecidos')

# PUT do produto montado a partir da leitura com include: preserva tudo, só soma a categoria, sem skus
product = {
    'name': 'P', 'slug': 'p', 'active': True, 'searchable': True, 'simple': False, 'is_digital': False, 'priority': 1,
    'brand': {'data': {'id': 7}},
    'texts': {'data': {'description': '<p>d</p>', 'specifications': 's', 'measures': ''}},
    'seo': {'data': {'seo_title': '', 'seo_description': 'x', 'seo_keywords': ''}},
    'extras': {'data': {'search_terms': 'termos'}},
    'variations': {'data': [{'id': 5}]},
    'collections': {'data': [{'id': 9}]},
    'categories': {'data': [{'id': 2}, {'id': 1}]},
    'skus': {'data': [{'id': 30, 'sku': 'A'}]},
}
payload = ci.product_put_payload(product, ci.product_snapshot(product)['categories_ids'] + [3])
assert payload == {'name': 'P', 'slug': 'p', 'active': True, 'searchable': True, 'simple': False, 'is_digital': False,
                   'priority': 1, 'brand_id': 7, 'description': '<p>d</p>', 'specifications': 's', 'measures': '',
                   'seo_title': '', 'seo_description': 'x', 'search_terms': 'termos', 'variations_ids': [5],
                   'collections_ids': [9], 'categories_ids': [1, 2, 3]}, payload
assert 'skus' not in payload

# motivo com mais de um parágrafo (ficha da ferramenta usa linha em branco)
multi = ci.build_description(ci.validate_spec({**good, 'itens': [{'titulo': 'A', 'texto': 'um\n\ndois'}]}))
assert multi.endswith('<p><strong>A</strong> um</p><p>dois</p>'), multi

# capa: nome de arquivo ou URL completa
assert ci.same_image('https://x/uploads/category_cover/abc.png', 'abc.png')
assert ci.same_image('https://x/a/abc.png?v=1', 'https://y/b/abc.png')
assert not ci.same_image('https://x/a/abc.png', 'def.png')
assert not ci.same_image('', 'abc.png')

print('ok')
