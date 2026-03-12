/**
 * product-images.js
 * Maps auto part names to Font Awesome 6 icons with branded colour backgrounds.
 * Returns an HTML string (not img src) – the rendering code places it as innerHTML.
 *
 * Usage:
 *   var html = PartImages.getIcon(part);   // returns an HTML string
 *   var bg   = PartImages.getBg(part);     // returns CSS gradient string
 */
var PartImages = (function () {

    /* ── Icon + colour mapping ── */
    var LOOKUP = [
        { match: 'brake pad',       icon: 'fa-compact-disc',     bg: ['#e74c3c','#922b21'] },
        { match: 'oil filter',      icon: 'fa-filter',           bg: ['#e67e22','#784212'] },
        { match: 'spark plug',      icon: 'fa-bolt',             bg: ['#f39c12','#7d6608'] },
        { match: 'air filter',      icon: 'fa-wind',             bg: ['#2980b9','#154360'] },
        { match: 'alternator',      icon: 'fa-charging-station', bg: ['#8e44ad','#4a235a'] },
        { match: 'battery',         icon: 'fa-car-battery',      bg: ['#27ae60','#0e5e34'] },
        { match: 'radiator',        icon: 'fa-temperature-half', bg: ['#1a3a5c','#0d1f3c'] },
        { match: 'fuel pump',       icon: 'fa-gas-pump',         bg: ['#e74c3c','#922b21'] },
        { match: 'water pump',      icon: 'fa-droplet',          bg: ['#00cec9','#006b6b'] },
        { match: 'timing belt',     icon: 'fa-link',             bg: ['#2c3e50','#1a252f'] },
        { match: 'transmission',    icon: 'fa-oil-can',          bg: ['#00b894','#005f4e'] },
        { match: 'engine oil',      icon: 'fa-oil-can',          bg: ['#e67e22','#784212'] },
        { match: 'coolant',         icon: 'fa-snowflake',        bg: ['#4fc3f7','#0277bd'] },
        { match: 'fuel filter',     icon: 'fa-filter-circle-xmark', bg: ['#f39c12','#7d6608'] },
        { match: 'air condition',   icon: 'fa-fan',              bg: ['#00cec9','#006b6b'] },
        { match: 'steering',        icon: 'fa-dharmachakra',     bg: ['#e84393','#880e4f'] },
        { match: 'shock',           icon: 'fa-arrows-up-down',   bg: ['#636e72','#2d3436'] },
        { match: 'rotor',           icon: 'fa-circle-notch',     bg: ['#e74c3c','#922b21'] },
        { match: 'caliper',         icon: 'fa-c',                bg: ['#e67e22','#784212'] },
        { match: 'master cylinder', icon: 'fa-gauge-high',       bg: ['#1a3a5c','#0d1f3c'] }
    ];

    var DEFAULT = { icon: 'fa-gear', bg: ['#2980b9','#154360'] };

    function find(part) {
        var name = (part.name || '').toLowerCase();
        for (var i = 0; i < LOOKUP.length; i++) {
            if (name.indexOf(LOOKUP[i].match) !== -1) return LOOKUP[i];
        }
        return DEFAULT;
    }

    return {
        /** Returns Font Awesome icon class for the part */
        getIcon: function (part) {
            return 'fa-solid ' + find(part).icon;
        },
        /** Returns CSS linear-gradient for card background */
        getBg: function (part) {
            var bg = find(part).bg;
            return 'linear-gradient(135deg, ' + bg[0] + ', ' + bg[1] + ')';
        },
        /** Backward compat: returns a data URI with the FA icon embedded in SVG */
        get: function (part) {
            var entry = find(part);
            return 'data:image/svg+xml;charset=utf-8,' + encodeURIComponent(
                '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 200">' +
                '<defs><linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%">' +
                '<stop offset="0%" stop-color="' + entry.bg[0] + '"/>' +
                '<stop offset="100%" stop-color="' + entry.bg[1] + '"/>' +
                '</linearGradient></defs>' +
                '<rect width="400" height="200" fill="url(#bg)"/>' +
                '<text x="200" y="120" text-anchor="middle" fill="rgba(255,255,255,0.85)" ' +
                'font-family="system-ui,Arial,sans-serif" font-size="18" font-weight="700">' +
                (part.name || '').toUpperCase() + '</text>' +
                '</svg>'
            );
        }
    };
}());
