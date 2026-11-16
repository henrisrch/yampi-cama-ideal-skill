<template>
    <div class="rd-ci-detail" @keydown.esc="activeHotspot = null">
        <div class="rd-ci-detail__main">
            <div
                class="rd-ci-photo"
                @click="activeHotspot = null"
            >
                <img
                    v-if="image"
                    class="rd-ci-photo__image"
                    :src="image"
                    :alt="title"
                >

                <template v-for="(hotspot, index) in hotspots">
                    <button
                        :key="`marker-${index}`"
                        type="button"
                        class="rd-ci-hotspot"
                        :style="markerStyle(hotspot)"
                        :aria-label="`Ver ${hotspot.item.name}`"
                        :aria-expanded="activeHotspot === index ? 'true' : 'false'"
                        @click.stop="activeHotspot = activeHotspot === index ? null : index"
                    />

                    <a
                        v-if="activeHotspot === index"
                        :key="`card-${index}`"
                        class="rd-ci-hotspot-card"
                        style="visibility: hidden"
                        :href="productLink(hotspot.item)"
                        @click.stop
                    >
                        <span class="rd-ci-hotspot-card__thumb">
                            <img
                                v-if="hotspot.item.image"
                                :src="$thumborize(hotspot.item.image, { resize: '200x200' })"
                                :alt="hotspot.item.name"
                            >
                        </span>
                        <span class="rd-ci-hotspot-card__info">
                            <span>{{ hotspot.item.name }}</span>
                            <span>{{ hotspot.item.price | formatMoney }}</span>
                        </span>
                    </a>
                </template>
            </div>

            <div class="rd-ci-build">
                <header class="rd-ci-build__heading">
                    <h1 class="rd-ci-build__title">
                        {{ title }}
                    </h1>
                    <p
                        v-if="summary"
                        class="rd-ci-build__summary"
                    >
                        {{ summary }}
                    </p>
                </header>

                <ul class="rd-ci-items">
                    <li
                        v-for="item in items"
                        :key="item.id"
                        class="rd-ci-item"
                        :class="{
                            '-editing': item.editing,
                            '-unselected': !item.selected,
                            '-unavailable': item.unavailable
                        }"
                    >
                        <div class="rd-ci-item__row">
                            <input
                                :id="`rd-ci-item-${item.id}`"
                                v-model="item.selected"
                                type="checkbox"
                                class="rd-ci-item__check"
                                :disabled="item.unavailable"
                                @change="handleSelectionChange(item)"
                            >

                            <div class="rd-ci-item__info">
                                <div class="rd-ci-item__top">
                                    <label
                                        class="rd-ci-item__name"
                                        :for="`rd-ci-item-${item.id}`"
                                    >{{ item.name }}</label>
                                    <span
                                        v-if="item.unavailable"
                                        class="rd-ci-item__price -unavailable"
                                    >Indisponível</span>
                                    <span
                                        v-else
                                        class="rd-ci-item__price"
                                    >{{ item.price | formatMoney }}</span>
                                </div>

                                <div
                                    v-if="variationsOf(item).length"
                                    class="rd-ci-item__variant"
                                >
                                    <span>{{ variantLabel(item) }}  ·</span>
                                    <button
                                        type="button"
                                        :ref="`change-${item.id}`"
                                        class="rd-ci-item__change -clean"
                                        :aria-controls="pickerId(item)"
                                        :aria-expanded="item.editing ? 'true' : 'false'"
                                        :aria-label="`Trocar variações de ${item.name}`"
                                        @click="toggleEditing(item)"
                                    >
                                        trocar
                                    </button>
                                </div>
                            </div>
                        </div>

                        <div
                            v-if="item.editing"
                            :id="pickerId(item)"
                            class="rd-ci-picker"
                            @keydown.esc.stop.prevent="cancelEditing(item)"
                            role="region"
                            :aria-label="`Variações de ${item.name}`"
                        >
                            <div
                                v-for="variation in variationsOf(item)"
                                :key="variation.id"
                                class="rd-ci-picker__group"
                            >
                                <p class="rd-ci-picker__label">
                                    {{ variation.name }}: <strong>{{ pendingValueName(item, variation) }}</strong>
                                </p>

                                <div class="rd-ci-picker__options">
                                    <button
                                        v-for="value in valuesOf(item, variation)"
                                        :key="value.id"
                                        type="button"
                                        class="-clean"
                                        :class="[
                                            isSwatch(variation, value) ? 'rd-ci-picker__swatch' : 'rd-ci-picker__option',
                                            { '-selected': item.pending[variation.id] === value.id }
                                        ]"
                                        :style="swatchStyle(variation, value)"
                                        :title="valueLabel(value)"
                                        :aria-label="isSwatch(variation, value) ? valueLabel(value) : null"
                                        :aria-pressed="item.pending[variation.id] === value.id ? 'true' : 'false'"
                                        :disabled="!isValueAvailable(item, variation, value)"
                                        @click="pickValue(item, variation, value)"
                                    >
                                        <template v-if="!isSwatch(variation, value)">
                                            {{ valueLabel(value) }}
                                        </template>
                                    </button>
                                </div>
                            </div>

                            <button
                                type="button"
                                class="rd-ci-picker__confirm -clean"
                                @click="confirmEditing(item)"
                            >
                                Confirmar
                            </button>
                        </div>
                    </li>
                </ul>

                <div
                    v-if="!loading && !items.length"
                    class="alert -yellow"
                >
                    Nenhuma peça disponível nesta cama.
                </div>

                <template v-if="items.length">
                    <div class="rd-ci-build__footer">
                        <span class="rd-ci-build__count">{{ countLabel }}</span>
                        <span class="rd-ci-build__total">
                            total <strong>{{ totalPrice | formatMoney }}</strong>
                        </span>
                    </div>

                    <LoaderButton
                        class="rd-ci-build__buy"
                        :sending="submitting"
                        :disabled="!canSubmit"
                        :title="buyLabel"
                        @click="addSelectedToCart"
                    />
                </template>
            </div>
        </div>

        <div
            v-if="about"
            class="rd-ci-about"
        >
            <div class="rd-ci-about__box -structured">
                <h2
                    v-if="about.question"
                    class="rd-ci-about__question"
                >
                    {{ about.question }}
                </h2>

                <ul class="rd-ci-about__items">
                    <li
                        v-for="(item, index) in about.items"
                        :key="index"
                        class="rd-ci-about__item"
                    >
                        <h3 class="rd-ci-about__label">{{ item.label }}</h3>
                        <p
                            v-for="(text, textIndex) in item.texts"
                            :key="textIndex"
                            class="rd-ci-about__text"
                        >
                            {{ text }}
                        </p>
                    </li>
                </ul>
            </div>
        </div>

        <div
            v-else-if="explanation"
            class="rd-ci-about"
        >
            <div
                class="rd-ci-about__box"
                v-html="explanation"
            />
        </div>
    </div>
</template>

<script>
// Detalhe de uma cama da "Cama Ideal": a página da subcategoria. Foto da cama
// com marcações (hotspots) e a lista das peças (os produtos da subcategoria),
// cada uma já marcada, com troca de tamanho/cor e um único "adicionar ao
// carrinho" para as peças marcadas.
//
// Uso no twig (ver sections/category/cama_ideal_content.twig):
//
//   <cama-ideal-detail
//       category-path="cama-ideal/cama-exemplo"
//       title="Cama Exemplo"
//       :hotspots-by-slug="{{ pontos.marcacoes() }}"
//   ></cama-ideal-detail>
//
// search/products só resolve subcategoria pelo caminho completo
// (<raiz>/<subcategoria>) e não traz variações: a lista aparece com o SKU
// padrão de cada produto e, em seguida, catalog/products/{slug} completa
// cada peça com SKUs/variações (o que habilita o "trocar").
import { mapActions } from '~/vuex';
import api from '@/modules/axios/api';
import HotspotPosition from '@/components/generic/HotspotPosition.vue';

const MOBILE_QUERY = '(max-width: 700px)';

// A API da Yampi não preenche `color` nos valores criados via API. Sem este
// fallback, a seleção de Cor vira um botão textual e se distancia do swatch
// circular especificado no Figma para a montagem da Cama Ideal.
const COLOR_VARIATION_NAMES = ['cor', 'cores'];
const FALLBACK_SWATCH_COLORS = {
    azul: '#3B5B92',
    brun: '#6B4423',
    dune: '#C9B79C',
    ecru: '#C2B280',
    juniper: '#5B7C75',
    meadow: '#7A8B5F',
    oat: '#DDD0B8',
    olea: '#6B6E4E',
    willow: '#8A9A5B',
};

export default {
    name: 'CamaIdealDetail',

    props: {
        // content.data.slug da subcategoria: "<raiz>/<subcategoria>".
        categoryPath: {
            type: String,
            required: true,
        },

        title: {
            type: String,
            default: '',
        },

        // Capa da subcategoria; sem ela, vale o banner com o slug da subcategoria.
        cover: {
            type: String,
            default: '',
        },

        // { '<slug da subcategoria>': [{ x, y, mx?, my?, produto }] } — x/y em %
        // da foto; mx/my = celular (opcional). Vem de elements/cama-ideal-marcacoes.twig.
        // (json_encode de um hash vazio vira [], por isso aceita Array.)
        hotspotsBySlug: {
            type: [Object, Array],
            default: () => ({}),
        },

        // Teto de peças buscadas na subcategoria.
        maxProducts: {
            type: Number,
            default: 50,
        },
    },

    data: () => ({
        items: [],
        description: '',
        banner: '',
        activeHotspot: null,
        isMobile: false,
        loading: true,
        submitting: false,
    }),

    computed: {
        slug() {
            return this.categoryPath.split('/').pop();
        },

        image() {
            return this.cover || this.banner;
        },

        hotspots() {
            return (this.hotspotsBySlug[this.slug] || [])
                .map(hotspot => ({
                    ...hotspot,
                    item: this.items.find(item => item.slug === hotspot.produto),
                }))
                .filter(hotspot => hotspot.item);
        },

        descriptionParts() {
            if (!this.description) {
                return { summary: '', rest: '' };
            }

            const { body } = new DOMParser().parseFromString(this.description, 'text/html');

            const first = body.firstElementChild;

            if (!first || first.tagName !== 'P') {
                return first
                    ? { summary: '', rest: body.innerHTML.trim() }
                    : { summary: (body.textContent || '').trim(), rest: '' };
            }

            const summary = (first.textContent || '').trim();

            first.remove();

            return { summary, rest: body.innerHTML.trim() };
        },

        summary() {
            return this.descriptionParts.summary;
        },

        explanation() {
            return this.descriptionParts.rest;
        },

        // Bloco "O que transforma…" lido da descrição (o que vem depois do
        // resumo): 1º título (H1–H3) ou parágrafo todo em negrito → pergunta;
        // cada item começa com um negrito (strong/b no início do parágrafo,
        // ou um título H3–H6 depois da pergunta) → label, e o texto vem no
        // mesmo parágrafo ou nos seguintes. Fora desse padrão (listas,
        // tabelas, imagens, texto sem label) devolve null e a descrição
        // aparece crua, como antes.
        about() {
            if (!this.explanation) {
                return null;
            }

            const { body } = new DOMParser().parseFromString(this.explanation, 'text/html');
            const clean = value => (value || '').replace(/\s+/g, ' ').trim();
            const cleanLabel = value => clean(value).replace(/\s*[:–—-]\s*$/, '');
            const isBold = node => node.nodeType === 1 && ['STRONG', 'B'].includes(node.tagName);
            const meaningful = node => node.nodeType === 1
                ? node.tagName !== 'BR'
                : clean(node.textContent) !== '';

            let question = '';
            const items = [];

            for (const node of Array.from(body.childNodes)) {
                if (!meaningful(node)) {
                    continue;
                }

                if (node.nodeType !== 1) {
                    return null;
                }

                const content = clean(node.textContent);
                const heading = /^H([1-6])$/.exec(node.tagName);
                const isFirst = !question && !items.length;

                if (!content) {
                    continue;
                }

                if (heading) {
                    if (isFirst && heading[1] <= 3) {
                        question = content;
                    } else if (question || heading[1] >= 3) {
                        items.push({ label: cleanLabel(content), texts: [] });
                    } else {
                        return null;
                    }

                    continue;
                }

                if (node.tagName !== 'P' && node.tagName !== 'DIV') {
                    return null;
                }

                if (node.querySelector('img, ul, ol, table, iframe')) {
                    return null;
                }

                const children = Array.from(node.childNodes).filter(meaningful);
                const lead = children[0];
                const boldText = Array.from(node.querySelectorAll('strong, b'))
                    .filter(bold => !bold.parentElement.closest('strong, b'))
                    .map(bold => clean(bold.textContent))
                    .join(' ');

                if (isFirst && clean(boldText) === content) {
                    question = content;
                    continue;
                }

                if (isBold(lead)) {
                    const label = cleanLabel(lead.textContent);

                    lead.remove();
                    items.push({ label, texts: [] });

                    const rest = clean(node.textContent);

                    if (rest) {
                        items[items.length - 1].texts.push(rest);
                    }

                    continue;
                }

                if (!items.length) {
                    return null;
                }

                items[items.length - 1].texts.push(content);
            }

            const valid = items.length
                && items.every(item => item.label && item.texts.length);

            return valid ? { question, items } : null;
        },

        selectedItems() {
            return this.items.filter(item => item.selected && !item.unavailable);
        },

        totalPrice() {
            return this.selectedItems.reduce((total, item) => total + item.price, 0);
        },

        canSubmit() {
            return !this.submitting && this.selectedItems.length > 0;
        },

        countLabel() {
            const count = this.selectedItems.length;

            return count === 1 ? '1 peça selecionada' : `${count} peças selecionadas`;
        },

        buyLabel() {
            const count = this.selectedItems.length;

            return count === 1 ? 'Adicionar 1 peça' : `Adicionar ${count} peças`;
        },
    },

    mounted() {
        this.loadCama();
        this.loadBanner();
        this.watchViewport();
    },

    watch: {
        activeHotspot() { this.positionHotspotCard(); },
        hotspots() { this.positionHotspotCard(); },
    },

    beforeDestroy() {
        if (this.stopPositioning) this.stopPositioning();
        if (this.stopViewport) this.stopViewport();
    },

    methods: {
        ...mapActions('cart', ['addProductsToCart']),

        async loadCama() {
            try {
                const { data } = await api.get('search/products', {
                    params: {
                        context: 'category',
                        slug: this.categoryPath,
                        limit: this.maxProducts,
                    },
                });

                this.description = data.meta?.description || '';
                this.items = (data.data ?? []).map(this.normalizeProduct);
            } catch (e) {
                this.items = [];
            }

            this.loading = false;
            this.items.forEach(item => this.loadSkus(item));
        },

        normalizeProduct(product) {
            return {
                id: product.id,
                slug: product.slug,
                name: product.name,
                raw: product,
                image: product.images?.data?.[0]?.url || '',
                url: product.url_path || `/${product.slug}/p`,
                product: null,
                sku: { id: product.sku_id },
                price: product.prices?.data?.price ?? 0,
                unavailable: product.blocked_sale,
                selected: !product.blocked_sale,
                editing: false,
                pending: {},
            };
        },

        async loadSkus(item) {
            try {
                const { data } = await api.get(`catalog/products/${item.slug}`);
                const product = data.data;
                const skus = product?.skus?.data ?? [];
                const sku = skus.find(candidate => candidate.id === item.sku.id && !candidate.blocked_sale)
                    || skus.find(candidate => !candidate.blocked_sale);

                if (!sku) {
                    return;
                }

                item.product = product;
                // O action do carrinho espera o produto completo (com dados
                // de catálogo/SKU), não o resumo de search/products usado
                // apenas para montar a lista visual.
                item.raw = product;
                this.applySku(item, sku);
            } catch (e) {
                // sem os SKUs a peça segue com o SKU padrão, só sem o "trocar"
            }
        },

        applySku(item, sku) {
            item.sku = sku;
            item.price = sku.prices?.data?.price ?? item.price;
            item.image = sku.images?.data?.[0]?.url || item.image;
        },

        async loadBanner() {
            if (this.cover) {
                return;
            }

            try {
                const { data } = await api.get('catalog/banners');
                const banner = (data.data ?? []).find(candidate => candidate.slug === this.slug);

                this.banner = banner?.image_url || '';
            } catch (e) {
                this.banner = '';
            }
        },

        variationsOf(item) {
            return item.product?.variations?.data ?? [];
        },

        sellableSkus(item) {
            return (item.product?.skus?.data ?? []).filter(sku => !sku.blocked_sale);
        },

        skuHasValue(sku, variation, valueId) {
            return (sku.variations || [])
                .some(entry => entry.id === variation.id && entry.value_id === valueId);
        },

        // Só os valores que existem em algum SKU deste produto.
        valuesOf(item, variation) {
            const skus = item.product?.skus?.data ?? [];

            return (variation.values?.data ?? [])
                .filter(value => skus.some(sku => this.skuHasValue(sku, variation, value.id)));
        },

        isValueAvailable(item, variation, value) {
            return this.sellableSkus(item).some(sku => this.skuHasValue(sku, variation, value.id));
        },

        valueLabel(value) {
            return value.value || value.name || '';
        },

        isColorVariation(variation) {
            return COLOR_VARIATION_NAMES.includes((variation.name || '').trim().toLowerCase());
        },

        swatchColor(value) {
            const name = this.valueLabel(value).trim().toLowerCase();

            return value.color || FALLBACK_SWATCH_COLORS[name] || null;
        },

        isSwatch(variation, value) {
            return this.isColorVariation(variation) && Boolean(this.swatchColor(value));
        },

        swatchStyle(variation, value) {
            const color = this.isColorVariation(variation) ? this.swatchColor(value) : null;

            return color ? { backgroundColor: color } : null;
        },

        variantLabel(item) {
            return (item.sku.variations || []).map(entry => entry.value).join(' · ');
        },

        pendingValueName(item, variation) {
            const value = (variation.values?.data ?? [])
                .find(candidate => candidate.id === item.pending[variation.id]);

            return value ? value.value : '';
        },

        pendingFromSku(sku) {
            const pending = {};

            (sku.variations || []).forEach(entry => {
                pending[entry.id] = entry.value_id;
            });

            return pending;
        },

        toggleEditing(item) {
            if (!item.editing) {
                item.pending = this.pendingFromSku(item.sku);
            }

            item.editing = !item.editing;
        },

        pickerId(item) {
            return `rd-ci-picker-${item.id}`;
        },

        handleSelectionChange(item) {
            // No Figma, a variação aberta pertence a um item selecionado.
            // Ao desmarcá-lo, recolhemos o painel para manter os dois estados
            // (recolhido/expandido) consistentes.
            if (!item.selected) {
                item.editing = false;
            }
        },

        // A escolha em andamento é sempre um SKU vendável: ao trocar um valor,
        // fica o SKU com esse valor que mais preserva as outras escolhas.
        pickValue(item, variation, value) {
            const matches = sku => (sku.variations || [])
                .filter(entry => entry.id !== variation.id && item.pending[entry.id] === entry.value_id)
                .length;

            const best = this.sellableSkus(item)
                .filter(sku => this.skuHasValue(sku, variation, value.id))
                .sort((a, b) => matches(b) - matches(a))[0];

            if (best) {
                item.pending = this.pendingFromSku(best);
            }
        },

        focusChange(item) {
            this.$nextTick(() => {
                const button = this.$refs[`change-${item.id}`];
                (Array.isArray(button) ? button[0] : button)?.focus();
            });
        },

        cancelEditing(item) {
            item.pending = this.pendingFromSku(item.sku);
            item.editing = false;
            this.focusChange(item);
        },

        confirmEditing(item) {
            const sku = this.sellableSkus(item).find(candidate => (candidate.variations || [])
                .every(entry => item.pending[entry.id] === entry.value_id));

            if (sku) {
                this.applySku(item, sku);
            }

            item.editing = false;
            this.focusChange(item);
        },

        // Mesmo corte do tema: abaixo de 701px vale a posição mobile.
        watchViewport() {
            if (!window.matchMedia) return;

            const query = window.matchMedia(MOBILE_QUERY);
            const update = () => {
                this.isMobile = query.matches;
                this.positionHotspotCard();
            };

            update();

            if (query.addEventListener) {
                query.addEventListener('change', update);
                this.stopViewport = () => query.removeEventListener('change', update);
            } else {
                query.addListener(update);
                this.stopViewport = () => query.removeListener(update);
            }
        },

        markerStyle(hotspot) {
            const useMobile = this.isMobile && hotspot.mx !== undefined && hotspot.my !== undefined;
            const x = Number(useMobile ? hotspot.mx : hotspot.x) || 0;
            const y = Number(useMobile ? hotspot.my : hotspot.y) || 0;

            return {
                left: `clamp(16px, ${x}%, calc(100% - 16px))`,
                top: `clamp(16px, ${y}%, calc(100% - 16px))`,
            };
        },

        positionHotspotCard() {
            if (this.stopPositioning) this.stopPositioning();
            this.$nextTick(() => {
                const container = this.$el.querySelector('.rd-ci-photo');
                const card = container && container.querySelector('.rd-ci-hotspot-card');
                const anchor = container && container.querySelector('.rd-ci-hotspot[aria-expanded="true"]');
                if (card && anchor) this.stopPositioning = HotspotPosition.methods.followHotspot(container, anchor, card);
            });
        },

        // Mantém a query string da página atual (ex.: ?preview=true).
        productLink(item) {
            const [path, query = ''] = item.url.split('?');
            const params = new URLSearchParams(window.location.search);

            new URLSearchParams(query).forEach((value, key) => params.set(key, value));

            const queryString = params.toString();

            return queryString ? `${path}?${queryString}` : path;
        },

        async addSelectedToCart() {
            this.submitting = true;

            const items = this.selectedItems;

            try {
                await this.addProductsToCart({
                    skus: items.map(item => item.sku),
                    products: items.map(item => item.raw),
                    value: this.totalPrice,
                });
            } catch (error) {
                // Mantém o seletor utilizável caso a sessão do carrinho do
                // preview esteja expirada ou seja recusada pela API.
                console.error('[CamaIdealDetail] Não foi possível adicionar as peças.', error);
            } finally {
                this.submitting = false;
            }
        },
    },
};
</script>
