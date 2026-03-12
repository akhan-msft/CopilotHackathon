/**
 * cart.js – shared cart logic (localStorage-backed)
 * Provides: Cart.add, Cart.remove, Cart.items, Cart.total, Cart.count
 * Also wires the cart dialog and updates the header badge on every page.
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
        var items = load();
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
        $.ui.toast && $.ui.toast({ message: '"' + part.name + '" added to cart!' });
    }

    function remove(id) {
        var items = load().filter(function (i) { return i.id !== id; });
        save(items);
        updateBadge();
    }

    function items() { return load(); }

    function total() {
        return load().reduce(function (sum, i) { return sum + i.price * i.qty; }, 0);
    }

    function count() {
        return load().reduce(function (sum, i) { return sum + i.qty; }, 0);
    }

    function updateBadge() {
        $('#cart-count').text(count());
    }

    function renderDialog() {
        var cartItems = load();
        var $list = $('#cart-items-list').empty();
        var $empty = $('#cart-empty-msg');
        var $totalEl = $('#cart-total');

        if (cartItems.length === 0) {
            $empty.show();
            $totalEl.hide();
        } else {
            $empty.hide();
            $totalEl.show();
            $.each(cartItems, function (idx, item) {
                var $row = $('<div class="cart-item"></div>');
                $row.append('<span class="cart-item-name">' + $('<span>').text(item.name).html() + '</span>');
                $row.append('<span class="cart-item-qty">x' + item.qty + '</span>');
                $row.append('<span class="cart-item-price">$' + (item.price * item.qty).toFixed(2) + '</span>');
                var $removeBtn = $('<button class="btn-remove" title="Remove">✕</button>');
                $removeBtn.on('click', (function (id) {
                    return function () {
                        remove(id);
                        renderDialog();
                    };
                }(item.id)));
                $row.append($removeBtn);
                $list.append($row);
            });
            $totalEl.html('Total: <strong>$' + total().toFixed(2) + '</strong>');
        }
    }

    /* Wire cart button on DOM ready */
    $(function () {
        updateBadge();

        /* Init jQuery UI dialog (hidden by default) */
        $('#cart-dialog').dialog({
            autoOpen: false,
            modal: true,
            width: 460,
            buttons: {
                'Clear Cart': function () {
                    save([]);
                    updateBadge();
                    renderDialog();
                },
                'Close': function () { $(this).dialog('close'); }
            }
        });

        $('#cart-btn').on('click', function () {
            renderDialog();
            $('#cart-dialog').dialog('open');
        });
    });

    return { add: add, remove: remove, items: items, total: total, count: count };
}());
