
/* -------------------------- jQuery forms plugins -------------------------- */

(function($) {
    
    /**
     * Attach onchange handler to RawIdField. It calls event handler additionally
     * when lookup window is closed for that field.
     */
    $.fn.adm_rawidfield_change = function(handler) {

        return this.each(function() {
            
            var $input = $(this);
            $input.change(handler);
            
            var orig_dismiss = window.dismissRelatedLookupPopup;
            var orig_dismiss_add = window.dismissAddAnotherPopup;
            
            window.dismissRelatedLookupPopup = function(win, chosenId) {
                var val = $input.val();
                orig_dismiss(win, chosenId);
                if ($input.val() != val) {
                    handler();
                }
            }
            
            window.dismissAddAnotherPopup = function(win, newId, newRepr) {
                var val = $input.val();
                orig_dismiss_add(win, newId, newRepr);
                if ($input.val() != val) {
                    handler();
                }
            }
        });
    }

    /**
     * Disable given form input. Such a field is not submitted upon form submition.
     * Set submitable=True if input should still be submitted.
     * 
     * If submitable=True then input is cloned and appended to DOM as hidden element.
     *
     * @param submitable Set to true if input should be submited even if disabled.
     */
    $.fn.adm_disable = function(submitable) {
        return this.each(function() {
            var $input = $(this);
            
            if (submitable) {
                $input.clone().removeAttr('id').addClass('adm_disabled hidden').appendTo($input.parent()).val($input.val());
            }
            
            $input.prev('label').removeClass('required');
            this.disabled = true;
        });
    };

    /**
     * Enable given form input. Cloned hidden input (if was added by adm_disable) is removed.
     *
     * @param required Set to true if field is required (uses strong).
     */
    $.fn.adm_enable = function(required) {
        required = (required === undefined ? true : required);
        
        return this.each(function() {
            var $input = $(this);
            this.disabled = false;
            if (required) {
                $input.prev('label').addClass('required');
                $input.parent().find('.adm_disabled').remove();
            }
        });
    };

    /**
     * Plugin that makes readonly field from given form-row divs.
     * 
     * The field will still be submitted since input is not being disabled, it is just hidden.
     **/
    $.fn.adm_readonly_field = function(options) {
        return this.each(function() {
            var $div = $(this).addClass('readonly');
            var $input = $div.find(':text,textarea').eq(0);
            $input.after($input.val()).css('display', 'none');
        });
    };
    

    /**
     * Plugin that integrates change list page into edit page of another object.
     * It works with adm_tab plugin. You need to call this plugin on tab content element
     * in which you want to integrate change list.
     */
    $.fn.adm_detail_list = function(options) {
        var opts = $.extend({}, $.fn.adm_detail_list.defaults, options);
        
        return this.each(function() {    
            var $tab = $(this);
            var $frame = $tab.find('iframe.detail-list');
            var $outer = $frame.parent();
            var emptyLoad = true;
            var srcUrl = '';

            function init() {
                $outer.css('height', '350px');
                $frame.css('border', 'none');

                srcUrl = lookupSrcUrl();

                $frame.load(frameLoadHndl);

                $tab.bind('adm_tabs:before-show', function(e) {
                    $frame.addClass('hidden');
                    $outer.css( { 'background' : 'url(/static/img/ajax-bloader.gif) no-repeat center center' });
                    $frame.css('width', '100%');
                });

                $tab.bind('adm_tabs:after-show', function(e) {
                    emptyLoad = false;
                    $frame.attr('src', srcUrl);
                });

                if (opts.add_button) {
                    createAddButton();
                }
            }

            function lookupSrcUrl() {
                var tabName = $tab.attr('id');
                var regex = new RegExp('adm_'+tabName+'_url=([^&]+)');
                var match = window.location.search.match(regex);

                if (match) {
                    return match[1];
                }
                else {
                    if (opts.filter) {
                        return opts.base_url + '?' + opts.filter;
                    } else {
                        return opts.base_url;
                    }
                }
            }

            function frameLoadHndl() {
               if (emptyLoad) { return; }

               var $doc = $(this.contentDocument);
               var $clist = $doc.find('#changelist');

               $doc.find('body').empty().append($clist);
               $doc.find('body').addClass('detail-list');
               $clist.css('width', 'auto');

               $clist.find('#changelist-search span a').attr('href', '?'+opts.filter);
               $clist.find('div.actions').remove();

               var $object_links = $clist.find('table > tbody a').click(function() {
                   $this = $(this);
                   var win = window.open($this.attr('href')+'?adm_ret_url='+opts.return_url);

                   window.closeRelatedWin = function(tab_name) {
                       var $fr = $('#'+tab_name).find('iframe');
                       $fr.addClass('hidden');
                       $fr.attr('src', $fr.get(0).contentDocument.defaultView.location);
                   }
                   return false;
               });

               $doc.find('a').not($object_links).click(function() {
                   $frame.addClass('hidden');
                   return true;
               });
               $doc.find('#changelist-search').submit(function() {
                   $frame.addClass('hidden');
                   return true;
               });

               $frame.removeClass('hidden');
               var bodyHeight = $doc.find('body').outerHeight();
               var filtersHeight = $doc.find('#changelist-filter').outerHeight();
               
               if (filtersHeight && filtersHeight + 60 > bodyHeight) {
                    $frame.add($outer).css('height', '' + (filtersHeight + 70) + 'px');
               } else {
                   $frame.add($outer).css('height', '' + (bodyHeight + 30) + 'px');
               }
            }

            function createAddButton() {
                $('div.submit-row p.deletelink-box', $tab).after('<input type="button" value="'+opts.add_button_caption+'" name="_add_detail"/>');

                $('input[name="_add_detail"]', $tab).click(function() {
                    var win = window.open(opts.base_url+'add/?adm_ret_url='+opts.return_url);
                    
                    window.closeRelatedWin = function(tab_name) {
                        var $fr = $('#'+tab_name).find('iframe');
                        $fr.addClass('hidden');
                        $fr.attr('src', $fr.get(0).contentDocument.defaultView.location);
                    }
                    return false;
                });
            }

            init();
        });
    };
    $.fn.adm_detail_list.defaults = {
        base_url: '',
        filter : '',
        return_url : '',
        add_button : false,
        add_button_caption : ''
    };  


    /**
     * Net/gross price calculation plugin.
     * 
     * It is designed to work in all situations where there are price_calc,
     * gross, net inputs and vat input or value provided.
     */
    $.fn.adm_price_calc = function(options) {
        var opts = $.extend({}, $.fn.adm_price_calc.defaults, options);

        return this.each(function() {
            var $pcalc = $(this);
            var $net = opts.net_input;
            var $gross = opts.gross_input;

            function vat() {
                if (opts.vat_input) {
                    return opts.vat_input.adm_dec(null, 2);
                } else {
                    return Number(opts.vat_value);
                }
            }

            function pcalc_change() {
                if (!opts.decision_func()) {
                    return;
                }
                
                if ($pcalc.val() == 'N') {
                    $net.adm_enable();
                    $gross.adm_disable();
                } else {
                    $net.adm_disable();
                    $gross.adm_enable();
                }
            }

            function recalc_prices() {
                if ($pcalc.val() == 'N') {
                    $gross.adm_money($net.adm_money() * (1 + vat()/100));
                } else {
                    $net.adm_money($gross.adm_money() / (1 + vat()/100));
                }
            }

            $net.add($gross).change(recalc_prices);
            
            $pcalc.change(function() {
                pcalc_change();
                recalc_prices();
            }).each(pcalc_change);

            if (opts.vat_input) {
                opts.vat_input.change(recalc_prices);
            }
        });
    };
    
    $.fn.adm_price_calc.defaults = {
        vat_input: null,
        vat_value: null,
        net_input: null,
        gross_input: null,
        decision_func: function() { return true; }
    };








/* ----------------------- Form and Page plugins ---------------------------- */


    /**
     * Plugin that does various dynamic stuff in address forms.
     **/
    $.fn.adm_address_form = function(options) {
        var opts = $.extend({}, $.fn.adm_address_form.defaults, options);
        
        return this.each(function() {
            var $form = $(this);

            function init() {
                var $type = $form.find('select[id$="type"]');

                $type.each(type_changed);
                $type.change(type_changed);
            }

            function type_changed() {
                var $sel = $(this);
                var $labels = $form.find('label[for$="company_name"], label[for$="nip"]');

                if (opts.condition_func() == false) {
                    return;
                }

                if ($sel.val() == 'C') {
                    $labels.addClass('required');
                }
                else {
                    $labels.removeClass('required');
                }
            }

            init();
        });
    };

    $.fn.adm_address_form.defaults = {
        condition_func: function() { return true; }
    };


    /**
     * Plugin for Discount model forms
     */
    $.fn.adm_discount_form = function(options) {
        
        return this.each(function () {
            var $percent = $('#id_percent');
            var $net = $('#id_net');
            var $gross = $('#id_gross');
            var $pcalc = $('#id_price_calc');
            var $orig_net = $('#id_orig_net');
            var $orig_gross = $('#id_orig_gross');

            function nature_change() {
                if ($(this).val() == 'F') {
                    $percent.adm_disable();

                    if ($pcalc.val() == 'N') {
                        $net.adm_enable();
                    } else {
                        $gross.adm_enable();
                    }
                }
                else {
                    $percent.adm_enable();
                    $net.add($gross).adm_disable();
                }
            }
            
            function set_article(event, article) {
                $net.adm_money(article.fields.net);
                $gross.adm_money(article.fields.gross);
                $pcalc.val(article.fields.price_calc);
                $orig_net.val(article.fields.net);
                $orig_gross.val(article.fields.gross);
                $('#id_vat').val(article.fields.vat);

                if ($('#id_nature').val() == 'P') {
                    $percent.change();
                }
            }

            function percent_change() {
                if ($pcalc.val() == 'N') {
                    $net.adm_money($orig_net.adm_money() * (1- $percent.adm_dec()/100)).trigger('change');
                } else {
                    $gross.adm_money($orig_gross.adm_money() * (1- $percent.adm_dec()/100)).trigger('change');
                }
            }

            $('#id_nature').change(nature_change);
            $('#id_nature').each(nature_change);
            $percent.change(percent_change);

            $pcalc.adm_price_calc({
                vat_input: $('#id_vat'),
                net_input: $net,
                gross_input: $gross,
                decision_func: function() { return $('#id_nature').val() == 'F' ? true : false }
            });
            
            $('#id_article_0').bind('article_change.article_mwidget', set_article);
        });
    };

    /**
     * Plugin for ShopArticle edit form
     */
    $.fn.adm_page_shoparticle = function(options) {
        return this.each(function() {
            var $props_div = $('#property_set-group > div.inline-related');
            var article_id = $('#id_property_set-0-article').val() || '';
            var initial_props_num = Number($('#id_property_set-INITIAL_FORMS').val());
            
            var $variants_base_fields = $('div.variants_type, div.variants_name, div.main_variant_name');
            var $variants_extra_fields = $('div.main_variant_qty, div.variants_unit')
            
            function init() {
                setup_property_inlines();

                configure_tinymce();
                setup_variants();
                setup_photos();
                setup_attachments();

                $('#id_specification').adm_rawidfield_change(change_spec);

                $('#id_art_price_calc').adm_price_calc({
                    vat_input: $('#id_art_vat'), net_input: $('#id_art_net'), gross_input: $('#id_art_gross')
                });
                $('#id_art_price_calc').adm_price_calc({
                    vat_input: $('#id_art_vat'), net_input: $('#id_art_purchase_net'), gross_input: $('#id_art_purchase_gross')
                });
            }

            function setup_variants() {
                $variants_base_fields.add($variants_extra_fields).find('label').addClass('required');
                $('#id_variants_type option[value=""]').remove();

                $('#id_variants').change(variants_change);
                $('#id_variants').each(variants_change);
                $('#id_variants_type').change(variants_type_change);
                
                $('#variant_set-group tr:not(.empty-form)').each(function() {
                    var $tr = $(this);
                    $('td.art_price_calc select', $tr).adm_price_calc({
                        vat_input:   $('#id_art_vat'),
                        net_input:   $('td.art_net input', $tr),
                        gross_input: $('td.art_gross input', $tr)
                    });
                });
            }

            function setup_photos() {
                $('body').bind('adm_tabs:before-form-move', function() {
                    $('#tab-photos tr.dynamic-photo_set:not(.has_original)').each(function() {
                        var $tr = $(this);
                        if ($('td.photo input', $tr).val() == '') {
                            $('td.large input', $tr).get(0).checked = true;
                            $('td.main input', $tr).get(0).checked = false;
                        }
                    });
                    return true;
                });
            }

            function setup_attachments() {
                $('body').bind('adm_tabs:before-form-move', function() {
                    $('#tab-attachments tr.dynamic-attachment_set:not(.has_original)').each(function() {
                        var $tr = $(this);
                        if ($('td.file input', $tr).val() == '') {
                            $('td.listed input', $tr).get(0).checked = true;
                        }
                    });
                    return true;
                });
            }

            function variants_change() {
                var $vtype = $('#id_variants_type');
                
                if (this.checked) {
                    $('#main-tabs').trigger('adm_tabs:enable-tab', ['#variants']);
                    if ($vtype.val() == '') {
                        $vtype.val('K');
                    }

                    $vtype.each(variants_type_change);
                }
                else {
                    $('#main-tabs').trigger('adm_tabs:disable-tab', ['#variants']);
                    $variants_base_fields.add($variants_extra_fields).slideUp('normal',
                        function() { $variants_base_fields.add($variants_extra_fields).find('input,select').val(''); }
                    );
                }
                if (Cufon) { Cufon.refresh('body.change-form ul.tabs li a'); }
            }

            function variants_type_change() {
                if ($(this).val() == 'Q') {
                    $variants_base_fields.add($variants_extra_fields).slideDown();
                    $('#tab-variants table td.qty input').adm_enable();
                    $('#tab-variants').find('td:nth-child(3), th:nth-child(2)').css('display', 'table-cell');
                }
                else {
                    $variants_base_fields.slideDown();
                    $variants_extra_fields.slideUp();
                    $('#tab-variants table td.qty input').adm_disable().val('');
                    $('#tab-variants').find('td:nth-child(3), th:nth-child(2)').hide();
                }
            }

            function configure_tinymce() {
                $('body').bind('adm_tabs:before-form-move', function() {
                    $('#id_desc').tinymce().remove();
                });

                $('#id_desc').tinymce({
                    script_url : adm.media_url + 'lib/tinymce/tiny_mce.js',
                    cleanup_on_startup : true,
                    cleanup : true,
                    theme : "advanced",
                    width: "718",
                    height: "600",
                    content_css : adm.media_url+"css/tinymce.css",
                    body_class : "tcontent",
                    inline_styles : false,
                    entity_encoding : "raw",
                    invalid_elements : "font,span,i,h1",
                    keep_styles : false,
                    apply_source_formatting : false,
                    verify_css_classes : true,
                    plugins : "searchreplace,media,table,preview,advimage,advlink,flashtube",
                    convert_urls : false,
                    document_base_url : "/",
                    theme_advanced_buttons1 : "formatselect,bold,separator,justifyleft,justifycenter,bullist,numlist",
                    theme_advanced_buttons2 : "charmap,link,unlink,image,media,indent,outdent,separator,replace,undo,redo,separator,hr,preview",
                    theme_advanced_buttons3 : "tablecontrols,flashtube,code",
                    theme_advanced_toolbar_location : "top",
                    table_styles : "Bez ramki=no-border;Wysrodkowana=centered",
                    flashtube_thumb_repl : '$1_thumb.jpg',
                    flashtube_fallback_repl : '$1_low.$2'
                });
            }

            function setup_property_inlines() {
                $('#tab-base fieldset.base div.spec_changed').hide();
                $props_div.find('tr.add-row').hide();

                $props_div.find('td.delete input').hide();
                $props_div.find('td.original p').css('font-size', '11px');
                $props_div.find('tr.has_original td').css('padding-top', '5px');
                $props_div.find('thead th:last').text('');

                // remove empty rows
                $props_div.find('tbody > tr:not(.has_original) td.property input:not([value])').closest('tr').remove();
                $('#id_property_set-TOTAL_FORMS').val($props_div.find('tbody tr').size());

                // hide original properties in case if form errors occured and form is redisplayed
                if ($('#id_spec_changed').val() == 'True') {
                    var $origs = $props_div.find('tbody tr.has_original').hide();
                    $props_div.find('tbody > tr:not(.has_original)').each(function() {
                        $('td.original',this).prepend('<p style="font-size: 11px">' + $('td.property_name input', this).val() + '</p>');
                    });
                }
            }

            function change_spec() {
                var $spec = $('#id_specification');
                var $origs = $props_div.find('tbody > tr.has_original');

                if (isNaN(Number($spec.val()))) {
                    return;
                }
                
                $props_div.slideUp('normal', function() {
                    // mark rows of existing properties for deletion and hide them
                    $origs.find('td.delete input').each(function() { this.checked = true; });
                    $origs.hide();

                    // remove all properties rows that are not assigned to any existing property
                    $props_div.find('tbody > tr:not(.has_original)').remove();

                    // fetch new properties and create rows for them
                    load_properties($spec.val());
                });

                $('#id_spec_changed').val('True');
            }

            function load_properties(spec_id) {
                var postdata = {
                    method : 'getProperties',
                    params : JSON.stringify({ spec_id : spec_id })
                };

                function loadOK(data) {
                    var template =
                        '<table><tr class="row1 ">\
                            <td class="original">\
                                <p style="font-size: 11px"></p>\
                                <input type="hidden" id="id" name=""/>\
                                <input type="hidden" id="article" value="1" name=""/>\
                            </td>\
                            <td class="property">\
                                <input type="hidden" id="property" name="" value=""/>\
                            </td>\
                            <td class="value">\
                                <input type="text" id="value" name="" maxlength="1000" class="vTextField"/>\
                            </td>\
                            <td class="property_name">\
                                <input type="hidden" id="property_name" name="" value="">\
                            </td>\
                            <td class="delete"/>\
                        </tr></table>';

                    function fname_func(field, id) {
                        return function(a) { 
                            return (id ? 'id_' : '') + 'property_set-'+(initial_props_num + a.pos)+'-'+field;
                        };
                    }

                    function prop_name(arg) {
                        var res = '';
                        $.each(props, function() {
                           if (this.pk == arg.prop.item.fields.prop) {
                               res = this.fields.name;
                           }
                        });

                        return res;
                    }

                    var directives = {
                        'tr' : {
                            'prop<-prop_members' : {
                                '@class' : function(a) { return a.pos % 2 == 0 ? 'row1' : 'row2'; },
                                'td.original p' : prop_name,
                                'td.original #id@name' : fname_func('id'),
                                'td.original #id@id' : fname_func('id', true),
                                'td.original #article@name' : fname_func('article'),
                                'td.original #article@value' : function() { return article_id || ''; },
                                'td.original #article@id' : fname_func('article', true),
                                'td.property #property@name' : fname_func('property'),
                                'td.property #property@value' : 'prop.pk',
                                'td.property #property@id' : fname_func('property', true),
                                'td.value #value@name' : fname_func('value'),
                                'td.value #value@id' : fname_func('value', true),
                                'td.property_name #property_name@name' : fname_func('property_name'),
                                'td.property_name #property_name@value' : prop_name
                            }
                        }
                        
                    };

                    var prop_members = JSON.parse(data.result['prop_members']);
                    var props = JSON.parse(data.result['properties']);
                    $props_div.find('tbody').prepend($(template).render({ 'prop_members' : prop_members }, directives).find('tr'));

                    $('#id_property_set-TOTAL_FORMS').val(initial_props_num + props.length);

                    $props_div.slideDown();
                }

                $.adm_post({ data: postdata, success: loadOK });
            }

            init();
        });
    };


    /**
     * Plugin for Shippper edit page
     */
    $.fn.adm_page_shipper = function(options) {
        return this.each(function() {
            var $packages_table = $('div.inline-group:has(#id_package_set-TOTAL_FORMS) table');
            var $pallets_table = $('div.inline-group:has(#id_pallet_set-TOTAL_FORMS) table');
            
            function init() {
                $('div.package_wrapping_weight').addClass('required');
                $('div.pallet_capacity').addClass('required');
                $('div.cash_on_delivery_net').addClass('required');
                

                if ($('#id_packages').get(0).checked) {
                    $('div.package_wrapping_weight').show();
                    $packages_table.show();
                }
                if ($('#id_pallets').get(0).checked) {
                    $('div.pallet_capacity').show();
                    $pallets_table.show();
                }
                if ($('#id_cash_on_delivery').get(0).checked) {
                    $('div.cash_on_delivery_net').show();
                }

                $('#id_packages').change(change_packages);
                $('#id_pallets').change(change_pallets);
                $('#id_cash_on_delivery').change(change_cod);

                $('#shipper_form').submit(on_submit);
            }

            function on_submit() {
                if ($('#id_packages').get(0).checked == false) {
                    $packages_table.find('tr:not(.has_original) input:text').val('');
                    $packages_table.find('tr.has_original td.delete input').each(function() { this.checked = true; });
                }
                if ($('#id_pallets').get(0).checked == false) {
                    $pallets_table.find('tr:not(.has_original) input:text').val('');
                    $pallets_table.find('tr.has_original td.delete input').each(function() { this.checked = true; });
                }
            }

            function change_packages() {
                if (this.checked) {
                    $packages_table.show();
                    $('div.package_wrapping_weight').slideDown();
                } else {
                    $packages_table.hide();
                    $('div.package_wrapping_weight').slideUp().find('input').val('');
                }
            }

            function change_pallets() {
                if (this.checked) {
                    $pallets_table.show();
                    $('div.pallet_capacity').slideDown();
                } else {
                    $pallets_table.hide();
                    
                    $('div.pallet_capacity').slideUp().find('input').val('');
                }
            }

            function change_cod() {
               if (this.checked) {
                    $('div.cash_on_delivery_net').slideDown();
                } else {
                    $('div.cash_on_delivery_net').slideUp().find('input').val('');
                }
            }

            init();
        });
    };


    /**
     * Plugin that does various dynamic stuff in client forms.
     **/
    $.fn.adm_client_form = function(options) {
        
        return this.each(function() {
            var $form = $(this);
            var $p_complete = $form.find('input[id$="profile_complete"]');

            function init() {
                $p_complete.each(p_complete_changed);
                $p_complete.change(p_complete_changed);

                $form.adm_address_form({
                    condition_func : function() {
                        return $p_complete.get(0).checked == true ? true : false;
                    }
                });
            }

            function p_complete_changed() {
                var $cbox = $(this);

                var labels = ['type', 'first_name', 'last_name', 'code', 'town', 'street',
                            'number', 'phone'];
                if ($form.find('select[id$="type"]').val() == 'C') {
                    labels.push('company_name', 'nip');
                }

                var selector = "";
                $.each(labels, function() {
                    selector += 'label[for$="'+this+'"],';
                });
                selector = selector.substring(0, selector.length-1);
                var $labels = $form.find(selector).not('label[for$="second_phone"]');

                if ($cbox.get(0).checked) {
                    $labels.addClass('required');
                }
                else {
                    $labels.removeClass('required');
                }
            }

            init();
        });
    };


    $.fn.adm_order_form = function(options) {
        return this.each(function() {
            var $orderitems = $('#orderitem_set-group');

            function init() {

                orderitems_init();

                $('#id_auto_params').change(auto_params_change);
                $('#id_auto_shipper').change(auto_shipper_change);
                $('#id_payment').change(payment_change);
                $('#id_status').change(status_change);

                $('#id_auto_shipper').each(auto_shipper_change);
                $('#id_payment').each(payment_change);

                init_employee_msg();
                $('#id_send_status_email').get(0).disabled = true;

                $('td.article', $orderitems).live(
                    'article_change.article_mwidget', orderitem_article_change);
                $('td.article', $orderitems).live(
                    'shoparticle_change.article_mwidget', orderitem_sarticle_change);

                $('tbody tr', $orderitems).not('.empty-form, .add-row').each(function() {
                    var $row = $(this);

                    $('td.discount_net, td.discount_gross, td.qty, td.discount_price_calc',
                        this).find('input, select').change(function() {
                            orderitem_recalc_sums($row);
                    });

                    $('td.discount_price_calc select', this).adm_price_calc({
                        vat_input: $('td.orig_price span.vat', this),
                        net_input: $('td.discount_net input', this),
                        gross_input: $('td.discount_gross input', this)
                    });
                });

                console.log($('#orderitem_set-group tr.add-row'));
                $('#orderitem_set-group tr.add-row').remove();
                //$('#orderitem_set-group tr.add-row a').live('click', orderitem_row_added);
            }

            function orderitems_init() {
                $('#orderitem_set-group td.original p').each(function() {
                    var $row = $(this).closest('tr');
                    $(this).html('<a href="../../shoparticle/'
                            + $row.find('td.article input').val() + '/">' + $(this).text() + '</a>');
                    $row.find('td.original p > a').adm_new_window();
                });
            }

            // unused yet
//            function orderitem_row_added() {
//                console.log("qweqeqe");
//                var $row = $(this).closest('table').find('tr.tr.dynamic-orderitem_set:last');
//                $('input.article_mwidget', $row).d_article_mwidget();
//            }

            function orderitem_recalc_sums($row) {
                var pcalc = $('td.discount_price_calc select', $row).val();
                var net = new adm.Decimal($('td.discount_net input', $row).adm_money());
                var gross = new adm.Decimal($('td.discount_gross input', $row).adm_money());
                var vat = new adm.Decimal($('td.orig_price span.vat', $row).adm_dec());
                var weight = new adm.Decimal($('td.orig_price span.weight', $row).adm_dec());
                var qty = new adm.Decimal($('td.qty input', $row).adm_dec());
                var one = new adm.Decimal(1);

                vat = vat.div(new adm.Decimal(100));

                if (pcalc == 'N') {
                    var sum_net = net.mult(qty);
                    var sum_gross = sum_net.mult(one.add(vat));
                } else {
                    var sum_gross = gross.mult(qty);
                    var sum_net = sum_gross.div(one.add(vat));
                }

                var t_weight = weight.mult(qty);

                $('td.sum_discount strong', $row).adm_money(sum_gross.val());
                $('td.sum_discount span span', $row).adm_money(sum_net.val());
                $('td.total_weight span', $row).adm_dec(t_weight.val());

                update_order_sums();
            }

            function update_order_sums() {
                var $sum = $('fieldset.summary');
                $('div.sum_discount span', $sum).html('-');
                $('div.sum_orig span', $sum).html('-');
                $('div.sum_savings span', $sum).html('-');

                $('fieldset.shipment div.shipment_weight span').html('-');
            }

            function orderitem_sarticle_change(e, sarticle) {
                var $row = $(this).parent();
                console.log("shoparticle_changed");
                console.log(sarticle);

                function success(data) {
                    if (data.result.param) {
                        var param = JSON.parse(data.result.param)[0];
                        $('td.param_value > strong', $row).text(param.fields.name);
                        $('td.param_value textarea', $row).slideDown();
                    }
                }

                if (sarticle.fields.param) {
                    var postdata = {
                        method : 'getArticleParam',
                        params : JSON.stringify({ id: sarticle.fields.param })
                    }
                    $.adm_post({ data: postdata, success: success });
                } else {
                    $('td.param_value > strong', $row).text('');
                    $('td.param_value textarea', $row).slideUp();
                }
                
            }

            function orderitem_article_change(e, article, discount) {
                var $row = $(this).parent();
                var disc_data = discount ? discount : article

                var $orig_p = $('td.orig_price > span', $row);
                $orig_p.find('span:eq(0)').adm_money(article.fields.net);
                $orig_p.children('strong').adm_money(article.fields.gross);

                $('td.discount_price_calc select', $row).val(disc_data.fields.price_calc);
                $('td.discount_net input', $row).adm_money(disc_data.fields.net);
                $('td.discount_gross input', $row).adm_money(disc_data.fields.gross);
                $('td.orig_price span.vat', $row).adm_dec(article.fields.vat);

                $('td.orig_price span.weight', $row).adm_dec(article.fields.weight);
                $('td.stock_level span', $row).adm_dec(article.fields.stock_lvl);
                
                $('td.sum_discount span', $row).html('<strong></strong> / <span></span>');
                $('td.total_weight span', $row).html('-');

                orderitem_recalc_sums($row);
            }

            function status_change() {
                var $status = $(this);
                var $send_msg = $('#id_send_status_email');

                if ($.inArray($status.val(), ['AC', 'SE', 'RJ', 'CA']) != -1) {
                    $send_msg.get(0).checked = true;
                    $send_msg.get(0).disabled = false;
                } else {
                    $send_msg.get(0).checked = false;
                    $send_msg.get(0).disabled = true;
                }
                $send_msg.trigger('change');
            }

            function init_employee_msg() {
                var $emsg = $('#id_send_employee_msg').closest('div.form-row');
                var $content = $('#id_employee_msg').closest('div.form-row');
                
                if ($('#id_send_employee_msg').get(0).checked == false) {
                    $content.hide();
                }
                
                $('#id_send_employee_msg').change(function() { $content.slideToggle(); });
            }

            function payment_change() {
                var $payment = $(this);
                if ($payment.val() == 'DE') {
                    $('#id_payment_deadline').adm_enable(true);
                } else {
                    $('#id_payment_deadline').adm_disable();
                }
            }

            function auto_shipper_change() {
                if (this.checked) {
                    $('#id_auto_params').adm_disable(true).get(0).checked = true;
                    $('#id_shipper').adm_disable(true);
                    $('#id_auto_params').each(auto_params_change);
                } else {
                    $('#id_shipper').adm_enable();
                    $('#id_auto_params').adm_enable();
                    $('#id_auto_params').each(auto_params_change);
                }
            }

            function auto_params_change() {
                if (this.checked) {
                    $('#id_pkg_type').adm_disable(true);
                    $('#id_net').adm_disable(true);
                    $('#id_gross').adm_disable(true);
                    $('#id_discount_net').adm_disable(true);
                    $('#id_discount_gross').adm_disable(true);
                } else {
                    $('#id_pkg_type').adm_enable();
                    $('#id_net').adm_enable();
                    $('#id_gross').adm_enable();
                    $('#id_discount_net').adm_enable();
                    $('#id_discount_gross').adm_enable();
                }
            }

            init();
        });
    };


    /**
     * Admin tab plugin
     * Published events:
     *  - adm_tabs:before-show      (tab to show)
     *  - adm_tabs:after-show       (tab shown)
     *  - adm_tabs:before-form-move (body)
     *  - adm_tabs:after-form-move  (body)
     */
    $.fn.adm_tabs = function(options) {
        var opts = $.extend({}, $.fn.adm_tabs.defaults, options);
        
        return this.each(function() {
            var $tabs = $(this);

            function init() {
                splitForm();
                displayErrorNotes();
                setupSubmitRows();
                bindEvents();

                $tabs.find('li').click(function() { changeTab($(this)); });
                var $actTab = tab(activeTabName());
                
                $actTab.trigger('adm_tabs:before-show');
                opts.beforeShow($actTab);

                $actTab.show();
                $actTab.trigger('adm_tabs:after-show');
                opts.afterShow($actTab);
            }

            function bindEvents() {
                $tabs.bind('adm_tabs:disable-tab', function(e, tab_name) {
                    tabLink(tab_name).unbind('click').addClass('disabled');
                });

                $tabs.bind('adm_tabs:enable-tab', function(e, tab_name) {
                    tabLink(tab_name).bind('click', function() { changeTab($(this)); }).removeClass('disabled');
                });
            }

            function tabId(tab_name) {
                return opts.idPrefix + '-' + tab_name.substring(1);
            }

            function tab(param) {
                if (typeof param == 'string') {
                    return $('#'+tabId(param));
                } else {
                    return $('#'+tabId(tabName(param)));
                }
            }

            function tabLink(tab_name) {
                return $tabs.find('li a[href="' + tab_name + '"]').parent();
            }

            // get tab name using tab link or tab content jQuery object
            function tabName($tab) {
                if ($tab.hasClass('tab')) {
                    return '#'+$tab.attr('id').substring(opts.idPrefix.length+1);
                }
                else {
                    return $tab.find('a').attr('href');
                }
                
            }
            
            function activeTabName() {
                return $tabs.find('li.active a').attr('href');
            }

            // Split change form across tabs
            function splitForm() {
                var $mtab = tab(opts.mainTab);
                
                for (ftitle in opts.formSplit) {
                    var $fpart = $mtab.find('div.inline-group, fieldset.module:not(div.inline-group fieldset)')
                                      .filter(':has(h2:contains('+ ftitle +'))');
                    $fpart.prependTo(tab(opts.formSplit[ftitle]).find('div.form-holder'));
                }
            }

            // attach necessary functionality to submit row buttons on tabs
            function setupSubmitRows() {
                var submit_done = false;

                $('div.submit-row input[type="submit"]').click(function() {
                    if (submit_done) {
                        return true;
                    }

                    var $mform = $('#'+opts.formId);
                    var $tab = $(this).closest('div.tab');
                    var $mtab = tab(opts.mainTab);
                    var tab_name = tabName($tab);
                    var $fparts = $('div.tab:not(.main)')
                            .find('div.inline-group, fieldset.module:not(div.inline-group fieldset)');
                    submit_done = true

                    $('body').trigger('adm_tabs:before-form-move');

                    $('div.tab:not(.main)')
                            .not('#'+tabId(tab_name))
                            .find('div.inline-group, fieldset.module:not(div.inline-group fieldset)').addClass('hidden');

                    // move main form here
                    if (! $tab.hasClass('main')) {
                        $mform.children().addClass('hidden');
                        $mform.appendTo($tab.find('div.form-holder'));
                    }
                    
                    // move all form parts from all tabs into the form
                    $mform.append($fparts);

                    // set active tab
                    $('#id_active_tab').val($('#main-tabs li.active a').attr('href').substring(1));

                    $('body').trigger('adm_tabs:after-form-move');

                    // submit the form
                    if (! $tab.hasClass('main')) {
                        $mform.find('div.submit-row input[name="' + $(this).attr('name') + '"]').eq(0).click();
                    }                    
                });
                
                
//                $('#'+opts.formId).submit(function() {
//                    var $mform = $('#'+opts.formId);
//                    var $fparts = $('div.tab:not(.main)')
//                            .find('div.inline-group, fieldset.module:not(div.inline-group fieldset)');
//
//                    // set active tab
//                    $('#id_active_tab').val($('#main-tabs li.active a').attr('href').substring(1));
//
//                    // move all form parts from all tabs into the form
//                    $mform.append($fparts.addClass('hidden'));
//                });
            }

            // Display error note on tabs which have errors
            function displayErrorNotes() {
                var mtab = tab(opts.mainTab);

                var foo = $('ul.errorlist li' , mtab);
                if ($('ul.errorlist li' , mtab).size() == 0) {
                    $('p.errornote', mtab).remove();
                }
                else {
                    tabLink(opts.mainTab).addClass('errors');
                }

                for (t in opts.formSplit) {
                    var tname = opts.formSplit[t];
                    var t = tab(tname);
                    
                    if ($('ul.errorlist li', t).size() > 0) {
                        tabLink(tname).addClass('errors');
                        t.children('.form-holder').prepend('<p class="errornote">Proszę popraw poniższe błędy</p>');
                    }
                }
            }

            function changeTab($new) {
               var $active = tabLink(activeTabName());
               var $act_cnt = tab($active);
               var $new_cnt = tab($new);

               $act_cnt.hide();
               $active.removeClass('active');
               opts.afterHide($act_cnt);

               $new_cnt.trigger('adm_tabs:before-show');
               opts.beforeShow($new_cnt);

               $new_cnt.show();
               $new.addClass('active');

               if (Cufon) { Cufon.refresh('body.change-form ul.tabs li a'); }
               
               $new_cnt.trigger('adm_tabs:after-show');
               opts.afterShow($new_cnt);
            }

            init();
        });
    }


$.fn.adm_tabs.defaults = {
        afterHide : function() {},
        beforeShow : function() {},
        afterShow : function() {},
        idPrefix : 'tab',
        formSplit : null, // 'form fieldset/inlines title' : '#tab_name',
        mainTab : '',
        formId : ''
    };

})(jQuery);








/* -------------------------- Admin form pages ------------------------------ */

$(document).ready(function() {

    /* ---------------------- All pages -------------------------- */

    function init() {
        return_url();
    }

    function return_url() {
        $('input[name="adm_ret_url"]').eq(0).each(function() {
            var $dlink = $('a.deletelink');
            $dlink.attr('href', $dlink.attr('href')+'?adm_ret_url=../'+$(this).val());
        });
    }

    init();

    /* --------------------- Shop Article -------------------------- */

    $('body.main-shoparticle').eq(0).each(function() {
        var qs = window.location.search;
        var m = qs.match(/ref=.+\/category\/(\d+)\//);
        if (m) {
            if (!$('#id_category').val()) {
                $('#id_category').val(m[1]);
            }
        }
    });

    /* --------------------- Client -------------------------- */

    $('body.main-client').eq(0).each(function() {

        $('#client_form').find('div.client_num, div.activation_code').adm_readonly_field();

        $('#tab-orders').adm_detail_list({ 
            base_url : '../../order/',
            filter   : 'client__id__exact='+$('#client-id').text(),
            return_url : '../../../close-related-view/tab-orders/'
        });

        $('#tab-discounts').adm_detail_list({
            base_url   : '../../clientdiscount/',
            filter     : 'client__id__exact='+$('#client-id').text(),
            return_url : '../../../close-related-view/tab-discounts/',
            add_button : true,
            add_button_caption : 'Dodaj rabat'
        });

        $('#main-tabs').adm_tabs({
            mainTab : '#profile',
            formId : 'client_form',
            formSplit : { 'Adresy' : '#address' }
        });

        $('#tab-address div.inline-related').adm_address_form();
        $('#tab-profile #client_form').adm_client_form();
    });


    /* --------------------- Discount/Promotion -------------------------- */


    $('body.main-clientdiscount, body.main-promotion').eq(0).each(function() {
        $('#clientdiscount_form, #promotion_form').adm_discount_form();
    });


    /* --------------------- Article -------------------------- */

    $('body.main-article').eq(0).each(function() {});

    /* --------------------- ShopArticle -------------------------- */

    $('body.main-shoparticle').eq(0).each(function() {

        $('#tab-opinions').adm_detail_list({
            base_url : '../../opinion/',
            filter   : 'article__id__exact='+$('#shoparticle-id').text(),
            return_url : '../../../close-related-view/tab-opinions/'
        });

        $('#main-tabs').adm_tabs({
            mainTab : '#base',
            formId : 'shoparticle_form',
            formSplit : {
                'Opis'       : '#desc',
                'Warianty'   : '#variants',
                'Zdjęcia'    : '#photos',
                'Załączniki' : '#attachments'
            }
        });

        $('body').adm_page_shoparticle();
    });

    /* --------------------- Shipper -------------------------- */

    $('body.main-shipper').eq(0).each(function() {
        $('body').adm_page_shipper();
    });

    /* --------------------- Order -------------------------- */

    // Call to adm_order_form has been moved to Order's change_form.html template
    // due to collisions with django's inline js code. We depend, in adm_order_form,
    // on the fact that the "add new row" link is already in DOM tree, and this link is
    // created by django JS.

});


