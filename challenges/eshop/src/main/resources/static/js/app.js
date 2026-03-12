/**
 * app.js – product listing page (index.html)
 */
$(function () {

    /* ── State ── */
    var state = {
        page: 0,
        limit: 8,
        search: '',
        minPrice: 0,
        maxPrice: 250
    };

    /* ── Price slider ── */
    $('#price-slider').slider({
        range: true,
        min: 0,
        max: 250,
        values: [0, 250],
        slide: function (event, ui) {
            state.minPrice = ui.values[0];
            state.maxPrice = ui.values[1];
            $('#price-range-label').text('$' + ui.values[0] + ' – $' + ui.values[1]);
        },
        stop: function () {
            state.page = 0;
            loadProducts();
        }
    });

    /* ── Search autocomplete ── */
    $('#search-input').autocomplete({
        source: function (request, response) {
            $.getJSON('/api/parts', { search: request.term, limit: 8 }, function (data) {
                response($.map(data.data, function (p) {
                    return { label: p.name + ' – ' + p.manufacturer, value: p.name, id: p.id };
                }));
            });
        },
        minLength: 2,
        select: function (event, ui) {
            state.search = ui.item.value;
            state.page = 0;
            loadProducts();
        }
    });

    /* ── Search button ── */
    $('#search-btn').on('click', function () {
        state.search = $('#search-input').val().trim();
        state.page = 0;
        loadProducts();
    });

    $('#search-input').on('keypress', function (e) {
        if (e.which === 13) $('#search-btn').trigger('click');
    });

    /* ── Reset ── */
    $('#reset-btn').on('click', function () {
        state.search = '';
        state.page = 0;
        state.minPrice = 0;
        state.maxPrice = 250;
        $('#search-input').val('');
        $('#price-slider').slider('values', [0, 250]);
        $('#price-range-label').text('$0 – $250');
        loadProducts();
    });

    /* ── Load products ── */
    function loadProducts() {
        var params = {
            page: state.page,
            limit: state.limit,
            minPrice: state.minPrice,
            maxPrice: state.maxPrice
        };
        if (state.search) params.search = state.search;

        $.getJSON('/api/parts', params, function (resp) {
            renderGrid(resp.data);
            renderPagination(resp.total, resp.totalPages);
        }).fail(function () {
            $('#product-grid').html('<p style="color:red">Failed to load products. Is the server running?</p>');
        });
    }

    /* ── Render grid ── */
    function renderGrid(parts) {
        var $grid = $('#product-grid').empty();
        var $noResults = $('#no-results');

        if (!parts || parts.length === 0) {
            $noResults.show();
            return;
        }
        $noResults.hide();

        $.each(parts, function (i, part) {
            var imgSrc = part.image_url || ('https://placehold.co/400x200/e0e0e0/555?text=' + encodeURIComponent(part.name));
            var $card = $(
                '<div class="product-card">' +
                    '<img src="' + imgSrc + '" alt="' + $('<span>').text(part.name).html() + '" onerror="this.src=\'https://placehold.co/400x200/e0e0e0/555?text=No+Image\'"/>'+
                    '<div class="card-body">' +
                        '<p class="card-title">' + $('<span>').text(part.name).html() + '</p>' +
                        '<p class="card-mfg">' + $('<span>').text(part.manufacturer).html() + '</p>' +
                        '<p class="card-desc">' + $('<span>').text(part.description).html() + '</p>' +
                        '<p class="card-price">$' + part.price.toFixed(2) + '</p>' +
                    '</div>' +
                    '<div class="card-footer">' +
                        '<button class="btn-add-cart">Add to Cart</button>' +
                        '<span class="stock-label">Stock: ' + part.stock + '</span>' +
                    '</div>' +
                '</div>'
            );

            /* Navigate to detail page on card click (not button) */
            $card.on('click', function (e) {
                if (!$(e.target).hasClass('btn-add-cart')) {
                    window.location.href = 'product.html?id=' + part.id;
                }
            });

            /* Add to cart button */
            $card.find('.btn-add-cart').on('click', function (e) {
                e.stopPropagation();
                Cart.add(part);
                showToast('"' + part.name + '" added to cart!');
            });

            $grid.append($card);
        });
    }

    /* ── Pagination ── */
    function renderPagination(total, totalPages) {
        var $pag = $('#pagination').empty();
        if (totalPages <= 1) return;

        var $prev = $('<button>‹ Prev</button>').prop('disabled', state.page === 0);
        $prev.on('click', function () { state.page--; loadProducts(); });
        $pag.append($prev);

        var startPage = Math.max(0, state.page - 2);
        var endPage   = Math.min(totalPages - 1, state.page + 2);

        for (var p = startPage; p <= endPage; p++) {
            (function (pg) {
                var $btn = $('<button>' + (pg + 1) + '</button>');
                if (pg === state.page) $btn.addClass('active');
                $btn.on('click', function () { state.page = pg; loadProducts(); });
                $pag.append($btn);
            }(p));
        }

        var $next = $('<button>Next ›</button>').prop('disabled', state.page >= totalPages - 1);
        $next.on('click', function () { state.page++; loadProducts(); });
        $pag.append($next);
    }

    /* ── Simple toast notification ── */
    function showToast(msg) {
        var $toast = $('<div style="position:fixed;bottom:20px;right:20px;background:#1a1a2e;color:#fff;padding:10px 18px;border-radius:6px;z-index:9999;box-shadow:0 2px 8px rgba(0,0,0,.3);">' + msg + '</div>');
        $('body').append($toast);
        setTimeout(function () { $toast.fadeOut(400, function () { $(this).remove(); }); }, 2500);
    }

    /* ── Initial load ── */
    loadProducts();
});
