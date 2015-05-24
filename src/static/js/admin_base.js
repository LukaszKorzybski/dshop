window.adm = {};


/* ------------------------ Admin common utilities -------------------------- */

(function(m) {

    /**
     * Primitive Decimalal class for financial and Decimalal calculations. Max precision is 4.
     * Decimal objects are immutable.
     */
    m.Decimal = function(num) {
        this._val = null;
        if (num) {
            this._val = Number(num) * 10000;
        }
    }

    m.Decimal.prototype.add = function(a) {
        return m.Decimal._new(this._val + (typeof a == "number" ? (new m.Decimal(a))._val : a._val));
    };

    m.Decimal.prototype.mult = function(a) {
        return m.Decimal._new((this._val * (typeof a == "number" ? (new m.Decimal(a))._val : a._val))/10000);
    };

    m.Decimal.prototype.div = function(a) {
        return m.Decimal._new((this._val / (typeof a == "number" ? (new m.Decimal(a))._val : a._val))*10000);
    };

    m.Decimal.prototype.sub = function(a) {
        return m.Decimal._new(this._val - (typeof a == "number" ? (new m.Decimal(a))._val : a._val));
    };

    m.Decimal.prototype.val = function() {
        return Number((this._val / 10000).toFixed(4));
    };

    m.Decimal._new = function(v) {
        var b = new m.Decimal();
        b._val = v;
        return b;
    }

})(adm);




/* ---------------------- jQuery admin common plugins ----------------------- */

(function($) {

    /**
     * Open link in new window
     */
    $.fn.adm_new_window = function(options) {
        return this.each(function() {
           $(this).click(function() {
                window.open($(this).attr('href'));
                return false;
           });
        });
    };

    /**
     * Post json short version, with some defaults
     */
    $.adm_post = function(opts) {
        opts.type = 'POST';
        opts.url = adm.url_prefix+'/rpc/';
        opts.dataType = 'json';
        $.ajax(opts);
    };

    /**
     * Localized Decimal support. Works with input fields and with any html tag
     * that can contain text node.
     *
     * Use it to read/write Decimalal values from/to form inputs or html tags.
     *
     * Returns NaN if can't parse value to Number.
     */
    $.fn.adm_dec = function(val, prec, unit) {
        prec = (prec == null ? 2 : prec);

        if (val == null) {
            var tag = this.get(0).tagName.toLowerCase();
            var p = 0;
            if (tag == 'input' || tag == 'textarea') {
                p = parseFloat(this.eq(0).val().replace(/,/, '.'));
            } else {
                p = parseFloat(this.eq(0).text().replace(/,/, '.'));
            }
            return p;

        } else {
            var parts = Number(val).toFixed(prec).split('.');
            var price = parts[0] + ',' + parts[1];

            return this.each(function() {
                var tag = this.tagName.toLowerCase();
                if (tag == 'input' || tag == 'textarea') {
                    $(this).val(price);
                } else {
                    $(this).html(price + (unit == null ? '' : ' ' + unit));
                }
            });
        }
    }

    /**
     * Shortcut for money operations
     */
    $.fn.adm_money = function(val) {
        return $.fn.adm_dec.call(this, val, 2, 'zł');
    }

})(jQuery);