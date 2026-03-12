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
        state.search   = '';
        state.page     = 0;
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
            page:     state.page,
            limit:    state.limit,
            minPrice: state.minPrice,
            maxPrice: state.maxPrice
        };
        if (state.search) params.search = state.search;

        $.getJSON('/api/parts', params, function (resp) {
            renderGrid(resp.data);
            renderPagination(resp.total, resp.totalPages);
        }).fail(function () {
            $('#product-grid').html(
                '<div class="col-12"><div class="alert alert-danger m-2">' +
                'Failed to load products. Is the server running?</div></div>'
            );
        });
    }

    /* ── Render grid ── */
    function renderGrid(parts) {
        var $grid      = $('#product-grid').empty();
        var $noResults = $('#no-results');

        if (!parts || parts.length === 0) {
            $noResults.removeClass('d-none');
            return;
        }
        $noResults.addClass('d-none');

        $.each(parts, function (i, part) {
            var iconClass = PartImages.getIcon(part);
            var bgStyle   = PartImages.getBg(part);
            var safeName = $('<span>').text(part.name).html();
            var safeMfg  = $('<span>').text(part.manufacturer).html();
            var safeDesc = $('<span>').text(part.description).html();

            var $col  = $('<div class="col"></div>');
            var $card = $(
                '<div class="card h-100 product-card">' +
                    '<div class="card-img-top d-flex align-items-center justify-content-center" style="background:' + bgStyle + '">' +
                        '<i class="' + iconClass + ' text-white" style="font-size:3rem;opacity:.85"></i>' +
                    '</div>' +
                    '<div class="card-body pb-2">' +
                        '<h6 class="card-title fw-bold mb-1">' + safeName + '</h6>' +
                        '<p class="small text-muted mb-1">' + safeMfg + '</p>' +
                        '<p class="small text-secondary desc-clamp mb-2">' + safeDesc + '</p>' +
                        '<p class="fw-bold text-danger mb-0 fs-5">$' + part.price.toFixed(2) + '</p>' +
                    '</div>' +
                    '<div class="card-footer bg-transparent border-top d-flex justify-content-between align-items-center py-2">' +
                        '<button class="btn btn-sm btn-dark btn-add-cart">' +
                            '<i class="bi bi-cart-plus me-1"></i>Add to Cart' +
                        '</button>' +
                        '<span class="badge bg-secondary">Stock: ' + part.stock + '</span>' +
                    '</div>' +
                '</div>'
            );

            /* Navigate to detail page on card click (not on the Add to Cart button) */
            $card.on('click', function (e) {
                if (!$(e.target).closest('.btn-add-cart').length) {
                    window.location.href = 'product.html?id=' + part.id;
                }
            });

            /* Add to cart button */
            $card.find('.btn-add-cart').on('click', function (e) {
                e.stopPropagation();
                Cart.add(part);
                showToast('"' + part.name + '" added to cart!');
            });

            $col.append($card);
            $grid.append($col);
        });
    }

    /* ── Pagination ── */
    function renderPagination(total, totalPages) {
        var $ul  = $('#pagination').empty();
        var $nav = $('#pagination-nav');

        if (totalPages <= 1) { $nav.addClass('d-none'); return; }
        $nav.removeClass('d-none');

        var startPage = Math.max(0, state.page - 2);
        var endPage   = Math.min(totalPages - 1, state.page + 2);

        var $prev = $(
            '<li class="page-item' + (state.page === 0 ? ' disabled' : '') + '">' +
                '<a class="page-link" href="#">‹ Prev</a>' +
            '</li>'
        );
        $prev.on('click', function (e) {
            e.preventDefault();
            if (state.page > 0) { state.page--; loadProducts(); }
        });
        $ul.append($prev);

        for (var p = startPage; p <= endPage; p++) {
            (function (pg) {
                var $li = $(
                    '<li class="page-item' + (pg === state.page ? ' active' : '') + '">' +
                        '<a class="page-link" href="#">' + (pg + 1) + '</a>' +
                    '</li>'
                );
                $li.on('click', function (e) { e.preventDefault(); state.page = pg; loadProducts(); });
                $ul.append($li);
            }(p));
        }

        var $next = $(
            '<li class="page-item' + (state.page >= totalPages - 1 ? ' disabled' : '') + '">' +
                '<a class="page-link" href="#">Next ›</a>' +
            '</li>'
        );
        $next.on('click', function (e) {
            e.preventDefault();
            if (state.page < totalPages - 1) { state.page++; loadProducts(); }
        });
        $ul.append($next);
    }

    /* ── Bootstrap toast notification ── */
    function showToast(msg) {
        var $t = $(
            '<div class="toast align-items-center text-white bg-dark border-0 ' +
            'position-fixed bottom-0 end-0 m-3 show" role="alert" ' +
            'style="z-index:9999;min-width:240px">' +
                '<div class="d-flex">' +
                    '<div class="toast-body">' + msg + '</div>' +
                    '<button type="button" class="btn-close btn-close-white me-2 m-auto"' +
                    ' data-bs-dismiss="toast"></button>' +
                '</div>' +
            '</div>'
        );
        $('body').append($t);
        setTimeout(function () { $t.fadeOut(400, function () { $(this).remove(); }); }, 2500);
    }

    /* ── Initial load ── */
    loadProducts();
});
