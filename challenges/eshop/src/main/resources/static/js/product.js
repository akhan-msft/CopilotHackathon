/**
 * product.js – product detail page (product.html)
 */
$(function () {

    /* ── Read part id from query string ── */
    function getQueryParam(name) {
        var match = new RegExp('[?&]' + name + '=([^&]*)').exec(window.location.search);
        return match ? decodeURIComponent(match[1]) : null;
    }

    var partId = getQueryParam('id');
    if (!partId) {
        window.location.href = 'index.html';
        return;
    }

    /* ── Fetch part details ── */
    $.getJSON('/api/parts/' + partId, function (part) {
        document.title = part.name + ' – AutoParts eShop';

        var iconClass = PartImages.getIcon(part);
        var bgStyle = PartImages.getBg(part);
        $('#detail-img').css('background', bgStyle);
        $('#detail-icon').addClass(iconClass);
        $('#detail-name').text(part.name);
        $('#detail-mfg').text('Manufacturer: ' + part.manufacturer + '  |  Part #: ' + part.partNumber);
        $('#detail-desc').text(part.description);
        $('#detail-price').text('$' + part.price.toFixed(2));
        if (part.stock > 0) {
            $('#detail-stock-label')
                .text('In stock (' + part.stock + ')')
                .removeClass('bg-danger bg-secondary')
                .addClass('bg-success');
        } else {
            $('#detail-stock-label')
                .text('Out of stock')
                .removeClass('bg-success bg-secondary')
                .addClass('bg-danger');
        }

        /* Specifications table */
        var $table = $('#specs-table').empty();
        if (part.specifications) {
            var specs = part.specifications;
            if (specs.weight)     $table.append('<tr><td>Weight</td><td>' + $('<span>').text(specs.weight).html() + '</td></tr>');
            if (specs.dimensions) $table.append('<tr><td>Dimensions</td><td>' + $('<span>').text(specs.dimensions).html() + '</td></tr>');
            if (specs.material)   $table.append('<tr><td>Material</td><td>' + $('<span>').text(specs.material).html() + '</td></tr>');
        }

        /* Model compatibility */
        if (part.modelCompatibility && part.modelCompatibility.length) {
            $('#detail-compat').text('Compatible with: ' + part.modelCompatibility.join(', '));
        }

        /* Add to cart button */
        $('#btn-add-detail').on('click', function () {
            Cart.add(part);
            showToast('"' + part.name + '" added to cart!');
        });

        if (part.stock === 0) {
            $('#btn-add-detail').prop('disabled', true)
                .addClass('opacity-50')
                .html('<i class="bi bi-x-circle me-2"></i>Out of Stock');
        }

    }).fail(function () {
        $('#detail-info').html('<p style="color:red">Part not found or server error.</p>');
    });

    /* ── Simple toast ── */
    function showToast(msg) {
        var $toast = $('<div style="position:fixed;bottom:20px;right:20px;background:#1a1a2e;color:#fff;padding:10px 18px;border-radius:6px;z-index:9999;box-shadow:0 2px 8px rgba(0,0,0,.3);">' + msg + '</div>');
        $('body').append($toast);
        setTimeout(function () { $toast.fadeOut(400, function () { $(this).remove(); }); }, 2500);
    }
});
