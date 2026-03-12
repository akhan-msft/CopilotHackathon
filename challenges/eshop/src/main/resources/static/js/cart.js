/**
 * cart.js – shared cart logic (localStorage-backed)
 * Provides: Cart.add, Cart.remove, Cart.items, Cart.total, Cart.count
 * Cart panel uses Bootstrap Offcanvas (no jQuery UI dialog).
 */
var Cart = (function () {
    var STORAGE_KEY = 'eshop_cart';

    function load() {
        try { return JSON.parse(localStorage.getItem(STORAGE_KEY)) || []; }
        catch (e) { return []; }
    }

    function save(items) {
        localStorage.setItem(STORAGE_KEY, JSON.stringify(items));
    }

    function add(part) {
        var items    = load();
        var existing = null;
        for (var i = 0; i < items.length; i++) {
            if (items[i].id === part.id) { existing = items[i]; break; }
        }
        if (existing) {
            existing.qty += 1;
        } else {
            items.push({ id: part.id, name: part.name, price: part.price, qty: 1 });
        }
        save(items);
        updateBadge();
    }

    function remove(id) {
        var items = load().filter(function (i) { return i.id !== id; });
        save(items);
        updateBadge();
    }

    function items()  { return load(); }

    function total() {
        return load().reduce(function (sum, i) { return sum + i.price * i.qty; }, 0);
    }

    function count() {
        return load().reduce(function (sum, i) { return sum + i.qty; }, 0);
    }

    function updateBadge() {
        $('#cart-count').text(count());
    }

    function renderCart() {
        var cartItems = load();
        var $list     = $('#cart-items-list').empty();
        var $empty    = $('#cart-empty-msg');
        var $totalEl  = $('#cart-total');
        var $clearBtn = $('#clear-cart-btn');

        if (cartItems.length === 0) {
            $empty.removeClass('d-none');
            $totalEl.addClass('d-none');
            $clearBtn.addClass('d-none');
        } else {
            $empty.addClass('d-none');
            $totalEl.removeClass('d-none');
            $clearBtn.removeClass('d-none');

            $.each(cartItems, function (idx, item) {
                var $row = $('<div class="d-flex align-items-center gap-3 py-2 border-bottom"></div>');
                $row.append(
                    '<div class="flex-grow-1">' +
                        '<div class="fw-semibold small">' + $('<span>').text(item.name).html() + '</div>' +
                        '<div class="text-muted small">qty ' + item.qty +
                            ' &times; $' + item.price.toFixed(2) + '</div>' +
                    '</div>'
                );
                $row.append(
                    '<span class="fw-bold text-danger small">$' +
                    (item.price * item.qty).toFixed(2) + '</span>'
                );
                var $removeBtn = $(
                    '<button class="btn btn-sm btn-link text-muted p-0 ms-1" title="Remove">' +
                    '<i class="bi bi-x-lg"></i></button>'
                );
                $removeBtn.on('click', (function (id) {
                    return function () { remove(id); renderCart(); };
                }(item.id)));
                $row.append($removeBtn);
                $list.append($row);
            });
            $totalEl.html('Total: <strong>$' + total().toFixed(2) + '</strong>');
        }
    }

    /* ── Wire up on DOM ready ── */
    $(function () {
        updateBadge();

        /* Populate cart content when the offcanvas panel is opened */
        var cartEl = document.getElementById('cartOffcanvas');
        if (cartEl) {
            cartEl.addEventListener('show.bs.offcanvas', renderCart);
        }

        /* Clear cart button */
        $('#clear-cart-btn').on('click', function () {
            save([]);
            updateBadge();
            renderCart();
        });
    });

    return { add: add, remove: remove, items: items, total: total, count: count };
}());
