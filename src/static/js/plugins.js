
(function($) {

    /**
     * singleFieldForm plugin.
     *
     * Register onsubmit handler on given form and override form's default
     * request url to more friendly one.
     *
     * [Example]
     * With html like that:
     *     <form class="search" action="/search/">Find article: <input type="text" name="what"/> <button type="submit">Search</button></form>
     *
     * After page load (document ready) call:
     *     $('form.search').d_singleFieldForm();
     *
     * It will change request url from /search/?what=xxx to more friendly: /search/xxxx/
     */
    $.fn.d_singleFieldForm = function(options) {
        var opts = $.extend({}, { 'trim' : false }, options);

        return this.each(function() {
            var $form = $(this);
            $form.submit(function() {
                var val = $form.find('input:text,select').eq(0).val();
                if (opts.trim) {
                    val = $.trim(val.replace(/\s+/g, ' '));
                }
                window.location = $form.attr('action') +
                    encodeURIComponent(val) + '/';
                return false;
            });
        });
    };

    $.fn.d_submitButton = function(options) {
        return this.each(function() {
            var $form = $(this).closest('form');

            $(this).click(function() {
                $form.get(0).submit();
                return false;
            });
            
            //$form.find('input:text, input:password').keydown(function(event) {
            //    if (event.keyCode == 13) {
            //        $form.get(0).submit();
            //    }
            //});
        });
    };

    $.fn.d_newWindow = function(options) {
        return this.each(function() {
           $(this).click(function() {
                window.open($(this).attr('href'));
                return false;
           });
        });
    };



    /**
     * Enhanced select widget.
     */
    $.fn.d_eselect = function(options) {
        var opts = $.extend({}, $.fn.d_eselect.defaults, options);

        return this.each(function() {
            var $select = $(this);
            var $opts = $(opts.options);
            var value = opts.init_value;

            function init() {
                $opts.css('display', 'none');
                $opts.appendTo($select.parent());
                $opts.css('position', 'absolute');

                $select.click(function() { showHide(); return false; });
                $opts.find(".option").click(function() { select(this); });
            }
            
            function showHide() {
                if ($opts.css('display') == 'none') {
                    var pos = $select.position();
                    $opts.css('top', pos.top + $select.outerHeight());
                    //$opts.css('right', $select.offsetParent().width() - pos.left - $select.outerWidth());
                    $opts.css('left', pos.left);
                    $opts.css('display', 'block');
                }
                else {
                    $opts.fadeOut();
                }
            }

            function select(opt) {
                if ($(opt).hasClass('disabled')) {
                    return;
                }
                
                var newvalue = $('.value', opt).text();
                var oldvalue = value;

                value = newvalue;
                $select.find('dfn').text($('.display', opt).text());
                $opts.fadeOut();

                if (newvalue != oldvalue) {
                    opts.onchange(oldvalue, newvalue);
                }
            }
            
            init();

        });
    };
    $.fn.d_eselect.defaults = {
        value_cls : 'value',
        display_cls : 'display',
        init_value : null,
        onchange : function() {}
    };


    
    /**
     * Shopping cart plugin. Needs shopping cart main form.
     */
    $.fn.d_shoppingCart = function(options) {
        var opts = $.extend({}, $.fn.d_shoppingCart.defaults, options);

        return this.each(function() {
            var $form = $(this);
            var $cart = $('div.cart');

            function init() {
                $cart.find('#clearBtn').click(clearCart);
                $cart.find('#recalcBtn').click(recalcCart);
                $cart.find('#orderBtn').click(toOrder);

                $form.find('tr.item').each(function() {
                    var $tr = $(this);
                    $tr.find('button.delete-btn').click(function() { deleteItem($tr); });
                    $tr.find("p.param span").click(function() { openParamEdit($tr); return false; });
                });
            }

            function getArticleId($tr) {
                return $tr.attr('id').split('-')[1];
            }

            function toOrder() {
                window.location = opts.url_prefix+opts.toOrder;
                return false;
            }

            function recalcCart() {
                 $form.find('input[name=action]').val('recalc');
                 $form.submit();
                 return false;
            }

            function deleteItem($tr) {
                $form.find('input[name=action]').val('remove');
                $form.find('input[name=article]').val(getArticleId($tr));
                $form.submit();
                return false;
            }

            function clearCart() {
                $form.find('input[name=action]').val('clear');
                $form.submit();
                return false;
            }

            function openParamEdit($tr) {
                var $fbox = $('#fboxParam');
                var id = getArticleId($tr);

                $('h2',$fbox).text($('a.articleName',$tr).text());
                $('h2 + p',$fbox).text($('span.variant',$tr).text());
                $('.unit',$fbox).text($('td.unit',$tr).text());
                $('#id_article',$fbox).val(id);
                $('#id_param',$fbox).val($('.full-param',$tr).text());

                $form.data('tr-id', $tr.attr('id'));
                $(document).bind('close.facebox', setItemParam);

                $('#facebox div.content').children().appendTo('#fboxWindows');

                $('div.cinfo', $fbox).hide();
                $('#id_param', $fbox).prev().text('Podaj');
                $.getJSON(opts.url_prefix+opts.rpc+'getArticleParam/', {'name' : $('span.param-name', $tr).text()},
                    function(json) {
                        var param = JSON.parse(json.result.param)[0];
                        $('div.cinfo', $fbox).html(param.fields.explanation);
                        $('div.cinfo', $fbox).slideDown();
                        $('#id_param', $fbox).prev().text('Podaj ' + param.fields.name_plural);
                    });
                $.facebox($('#fboxParam'), 'save');
                $fbox.find('#id_param').focus();
            }

            function setItemParam() {
                var $fbox = $('#fboxParam');
                var $tr = $('#'+$form.data('tr-id'));
                var postdata = {
                    method : 'setCartItemParam',
                    params : JSON.stringify({
                        article : $fbox.find('#id_article').val(),
                        param   : $fbox.find('#id_param').val(),
                        orderMode : opts.orderMode,
                        order_id : opts.orderId })
                }
                
                function setOK(data) {
                    $tr.find('.param span span').text(data.result.firstline.replace(/>/g,'&gt;').replace(/</g,'&lt;'));
                    $tr.find('.full-param').text(data.result.param.replace(/>/g,'&gt;').replace(/</g,'&lt;'));
                    if (data.result.param) {
                        $tr.find('.param > span').removeClass('atwork').addClass('success');
                        $tr.find('.param a').text('zmień');
                    }
                    else {
                        $tr.find('.param > span').removeClass('atwork').addClass('notice');
                        $tr.find('.param a').text('podaj');
                    }
                }
                function setFailed() {
                    $tr.find('.param > span').removeClass('atwork').addClass('error');
                    $tr.find('.param span span').text('błąd');
                    $tr.find('.param a').text('podaj');
                }

                $(document).unbind('close.facebox', setItemParam);
                $tr.find('.param > span').removeClass('notice success').addClass('atwork');
                $tr.find('.param a').text('zapisuję...');
                $.ajax({
                        type: 'post',
                        url: opts.url_prefix+opts.rpc,
                        dataType: 'json',
                        data: postdata,
                        success: setOK,
                        error: setFailed });
            }
            
            init();
        });
    };
    $.fn.d_shoppingCart.defaults = {
        url_prefix : '',
        rpc : '/rpc/',
        toOrder : '/utworz-zamowienie/',
        orderMode : false,
        orderId : ''
    };
    


})(jQuery);