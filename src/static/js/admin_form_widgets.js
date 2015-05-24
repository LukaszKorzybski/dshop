(function($) {

    /**
     * ArticleMultiWidget plugin.
     *
     * Events emmited:
     * @article_mwidget.change(article, best_discount) - when new shoparticle is chosen or when article variant is changed
     * @article_mwidget.sarticle_change(article) - when new shoparticle is chosen
     */
    $.fn.d_article_mwidget = function() {
        
        this.each(function() {
            var $sarticle = $(this);
            var $select = $sarticle.siblings('div.article_mwidget').find('select');

            function populate_variants(data) {
                if ('sarticle' in data.result) {
                    var sarticle = JSON.parse(data.result.sarticle)[0];

                    if ($select.parent().prev().attr('tagName') != "STRONG") {
                        $select.parent().before('<strong></strong>');
                    }
                    $select.parent().prev().text(sarticle.fields.name);

                    if ('variants' in data.result) {
                        var variants = JSON.parse(data.result.variants);

                        $select.children().remove();
                        $.each(variants, function(i, v) {
                            $select.append('<option value="' + v.fields.article + '">' + v.fields.variant + '</option>');
                        });

                        $select.adm_enable().parent().slideDown();
                        ajax_load_article($select.val());
                    }
                    else {
                        ajax_load_article(sarticle.fields.article);
                        
                        $select.adm_disable().parent().slideUp('normal', function() {
                            $select.children().remove();
                        });
                    }
                    $sarticle.trigger('shoparticle_change.article_mwidget', [sarticle]);
                } else {
                    
                }
            }

            function ajax_load_variants() {
                var postdata = {
                    method : 'getArticleVariants',
                    params : JSON.stringify({ sarticle_id: $sarticle.val() })
                };

                if (isNaN(Number($sarticle.val())) == false) {
                    $.adm_post({ data: postdata, success: populate_variants });
                }
            }

            function ajax_load_article(id) {
                var postdata = {
                    method : 'getArticle',
                    params : JSON.stringify({ pk: id })
                };

                function success(data) {
                    if (data.result.discount) {
                        $sarticle.trigger('article_change.article_mwidget',
                            [JSON.parse(data.result.article)[0], JSON.parse(data.result.discount)[0]]);
                    } else {
                        $sarticle.trigger('article_change.article_mwidget',
                            [JSON.parse(data.result.article)[0]]);
                    }
                }
                
                $.adm_post({ data: postdata, success: success });
            }

            $sarticle.adm_rawidfield_change(ajax_load_variants);
            $select.change(function() { ajax_load_article($(this).val()); });
            $select.each(function() {
                if ($select.children('option').length) {
                    $select.parent().slideDown();
                }
            });
        });
    };

    $(document).ready(function() {
        $('input.article_mwidget').d_article_mwidget();
    });
    
})(jQuery);