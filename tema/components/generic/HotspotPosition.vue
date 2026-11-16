<template><span /></template>
<script>
// Measure the rendered card, including asynchronous prices and images. Keep it
// inside the image; prefer a visible side that does not cover its trigger.
function followHotspot(container, anchor, card) {
    let frame = null;
    let stopped = false;
    const set = (key, value) => {
        if (card.style[key] !== value) card.style[key] = value;
    };
    const clamp = (value, min, max) => Math.min(Math.max(value, min), Math.max(min, max));
    const update = () => {
        frame = null;
        if (stopped || !container.isConnected || !anchor.isConnected || !card.isConnected) return;
        const box = container.getBoundingClientRect();
        if (!box.width || !box.height) return;
        const pad = Math.min(8, box.width / 4, box.height / 4);
        const bounds = { left: box.left + pad, right: box.right - pad, top: box.top + pad, bottom: box.bottom - pad };
        set('boxSizing', 'border-box');
        set('minWidth', '0px');
        set('minHeight', '0px');
        set('maxWidth', `${bounds.right - bounds.left}px`);
        set('maxHeight', `${bounds.bottom - bounds.top}px`);
        set('overflow', 'auto');
        set('overflowWrap', 'anywhere');
        set('transform', 'none');
        set('right', 'auto');
        set('bottom', 'auto');
        const rect = card.getBoundingClientRect();
        const dot = anchor.getBoundingClientRect();
        const cx = (dot.left + dot.right) / 2;
        const cy = (dot.top + dot.bottom) / 2;
        const gap = 8;
        const options = [
            { side: 'right', x: dot.right + gap, y: cy - rect.height / 2 },
            { side: 'left', x: dot.left - gap - rect.width, y: cy - rect.height / 2 },
            { side: 'bottom', x: cx - rect.width / 2, y: dot.bottom + gap },
            { side: 'top', x: cx - rect.width / 2, y: dot.top - gap - rect.height },
        ];
        const viewport = window.visualViewport;
        const visibleTop = viewport ? viewport.offsetTop : 0;
        const visibleBottom = visibleTop + (viewport ? viewport.height : window.innerHeight);
        const visibleLeft = viewport ? viewport.offsetLeft : 0;
        const visibleRight = visibleLeft + (viewport ? viewport.width : window.innerWidth);
        options.forEach(option => {
            const x = clamp(option.x, bounds.left, bounds.right - rect.width);
            const y = clamp(option.y, bounds.top, bounds.bottom - rect.height);
            const overlap = Math.max(0, Math.min(x + rect.width, dot.right + 2) - Math.max(x, dot.left - 2))
                * Math.max(0, Math.min(y + rect.height, dot.bottom + 2) - Math.max(y, dot.top - 2));
            const visible = Math.max(0, Math.min(x + rect.width, visibleRight) - Math.max(x, visibleLeft))
                * Math.max(0, Math.min(y + rect.height, visibleBottom) - Math.max(y, visibleTop));
            option.score = visible - overlap * 4 - Math.abs(x - option.x) - Math.abs(y - option.y);
            option.left = x;
            option.top = y;
        });
        options.sort((a, b) => b.score - a.score);
        const best = options[0];
        const parent = card.offsetParent || container;
        const origin = parent.getBoundingClientRect();
        set('left', `${best.left - origin.left - parent.clientLeft + parent.scrollLeft}px`);
        set('top', `${best.top - origin.top - parent.clientTop + parent.scrollTop}px`);
        card.dataset.placement = best.side;
        set('visibility', 'visible');
    };
    const schedule = () => {
        if (!stopped && frame === null) frame = requestAnimationFrame(update);
    };
    const observer = typeof ResizeObserver === 'undefined' ? null : new ResizeObserver(schedule);
    if (observer) [container, anchor, card].forEach(element => observer.observe(element));
    window.addEventListener('resize', schedule);
    window.addEventListener('scroll', schedule, true);
    if (window.visualViewport) {
        window.visualViewport.addEventListener('resize', schedule);
        window.visualViewport.addEventListener('scroll', schedule);
    }
    card.addEventListener('load', schedule, true);
    update();
    return () => {
        stopped = true;
        if (frame !== null) cancelAnimationFrame(frame);
        if (observer) observer.disconnect();
        window.removeEventListener('resize', schedule);
        window.removeEventListener('scroll', schedule, true);
        if (window.visualViewport) {
            window.visualViewport.removeEventListener('resize', schedule);
            window.visualViewport.removeEventListener('scroll', schedule);
        }
        card.removeEventListener('load', schedule, true);
    };
}

export default { name: 'HotspotPosition', methods: { followHotspot } };
</script>
