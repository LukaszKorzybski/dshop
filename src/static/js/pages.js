
dshop.page = function() {};

(function(m) {


    m.Base = function() {
        
        function init() {

            if ($.browser.msie && $.browser.version=="6.0") {
                ie6Message();
                menuFixIE();
            }
            if ($.browser.msie && $.browser.version=="7.0") {
                menuFixIE();
            }
            
            $.facebox.settings.opacity = 0.8;
            
            $('a.new-window').d_newWindow();
            $('a.submit').d_submitButton();
            $('form.search').d_singleFieldForm({ 'trim' : true });

            $('div.gtree li a').mouseover(function() {
                $(this).addClass('hover');
            }).mouseout(function() {
                $(this).removeClass('hover');
            });

            
            initFlashTube();
        }

        function ie6Message() {
            $('#ie6').html('Twoja przeglądarka ma już 9 lat, zawiera wiele błędów i dziur bezpieczeństwa. Niestety nie jesteśmy<br/> \
                        w stanie zagwarantować Tobie wsparcia w przypadku problemów z działaniem naszej strony pod Internet Explorer 6.<br/><br/> \
                        Prosimy zaktualizować przeglądarkę do nowszej wersji. \
                        <a href="http://www.mozilla-europe.org/pl/firefox/">Firefox 3.5</a> \
                        <a href="http://www.google.com/chrome/index.html?hl=pl&brand=CHMG&utm_source=pl">Google Chrome</a> \
                        <a href="http://www.microsoft.com/poland/windows/internet-explorer/default.aspx">Internet Explorer 8</a>');
        }

        function initFlashTube() {
            $("div.flashTube").jFlashTube({
                        playerURL : dshop.media_url + 'lib/flowplayer/flowplayer-3.0.7.swf',
                        key: '$215163d9e1c2812c574',
                        flashVersion: [9, 115],
                        oldVersionNotif : function(vid) { },
                        extraClip : { onStart : function(clip) { pageTracker._trackPageview(clip.url); } }
            });
        }

        function menuFixIE() {
            $('#menu li').mouseover(
                    function() { $(this).addClass('active');
                }).mouseout(
                    function() { $(this).removeClass('active');
                });
        }
        
        init();
        
    };


    m.MainPage = function() {
        swfobject.embedSWF(dshop.media_url+"slider/slider.swf",
                           "adbannerin",
                           "510","200",
                           "9.0.0",
                           null,
                           null);
    };


    m.MyOrders = function() {
        $('#yearSel').d_singleFieldForm();
        $('#yearSel select').change(function() {
            $('#yearSel').submit();
        });
    };

    
    m.Article = function(options) {
        var variants = options.variants;
        var variant = options.init_variant;
        
        function initPhotoSlide() {
            var $photos = $('#photos li');
            var $photoChoosers = $('#photo-choose a');

            $photos.find('a').facebox();

            $('#photo-choose a').click(function() {
                var $a = $(this);
                var num = $a.prevAll().size();

                if ($a.hasClass('active')) {
                    return false;
                }

                $photoChoosers.removeClass('active');
                $a.addClass('active');
                
                $photos.not(':hidden').fadeOut();
                $photos.eq(num).fadeIn();

                return false;
            });
        }

        function changeVariant(oldval, newval) {
            variant = newval;

            var $exec_time = $('#exec_time span');
            $exec_time.html($('#var-'+variant).find('p.exec_time').html());
            $exec_time.find('a').unbind('click').d_newWindow();
            
            if ($('#variants').hasClass('diffPrice')) {
                $vprice = $('#var-'+variant);
                $price = $('#price');

                if ($vprice.hasClass('discount')) {
                    $price.find('li.std').addClass('old');
                    $price.find('li.promo').show();

                    $price.find('li.std strong').text($vprice.find('.oldprice span').text()+' brutto');
                    $price.find('li.std span').text($vprice.find('.oldprice em').text()+' netto');

                    $price.find('li.promo strong').text($vprice.find('.total span').text()+' brutto');
                    $price.find('li.promo span').text($vprice.find('.total em').text()+' netto');
                }
                else {
                    $price.find('li.promo').hide();
                    $price.find('li.std').removeClass('old');

                    $price.find('li.std strong').text($vprice.find('.total span').text()+' brutto');
                    $price.find('li.std span').text($vprice.find('.total em').text()+' netto');
                }
            }
        }

        function buy() {
            if (variants) {
                if (variant == null) {
                    $.facebox.settings.topPosition = 0.33;
                    $.facebox('<h2>Informacja</h2><p>Przed dodaniem do koszyka wybierz wariant towaru.</p>', 'variantInfo');
                    $.facebox.settings.topPosition = 0.1;
                    return;
                }
                $('#add2cart input[name=variant]').val(variant);
            }
            $('#add2cart input[name=qty]').val($('#qty').val());
            $('#add2cart').submit();
        }
        
        function toggle_opinions_form() {
            var $a = $(this);
            $('#opinions form').toggleClass('open').slideToggle('normal', function() {
                if ($(this).hasClass('open')) {
                    $a.html('<em></em><span></span>Zamknij');
                } else {
                    $a.html('<em></em><span></span>Dodaj opinię');
                }
            });
        }

        function report_abuse() {
            var $a = $(this);
            var $opinion = $(this).closest('li');
            var postdata = {
                method : 'reportOpinionAbuse',
                params : JSON.stringify({ opinion_id : $opinion.attr('data-id') })
            };

            $a.text('zgłaszam...');
            $.post(
                dshop.url_prefix + '/rpc/',
                postdata,
                function() { $a.replaceWith('opinia zgłoszona'); },
                'json'
            );
        }

        function init_opinions() {
            var $toggle = $('#opinions > div.rating a.toggle').click(toggle_opinions_form);
            
            $('#opinions ul a.abuse').click(report_abuse);
            $('#opinions form button').click(function() {
                $('#id_id').val('13');
                $('#opinions form').get(0).submit();
            });

            if (options.opinions_form_invalid) {
                $('#opinions form').addClass('open').show();
                $toggle.html('<em></em><span></span>Zamknij');
            }

            $('#opinions div.stars').raty({
                path: dshop.media_url + 'img/',
                readOnly: true,
                showHalf: true,
                start: options.avg_rating,
                number: options.max_rating
            });

            $('#opinions ul > li span.stars').each(function() {
                $(this).text('').raty({
                    path: dshop.media_url + 'img/',
                    readOnly: true,
                    starOn: 'star-light-on.png?v=100710',
                    starOff: 'star-light-off.png?v=100710',
                    start: Number($(this).attr('data-rating')),
                    number: options.max_rating
                });
            });

            $('#id_rating').replaceWith('<span id="id_rating" class="stars"></span>');
            $('#id_rating').raty({
                path: dshop.media_url + 'img/',
                readOnly: false,
                start: 0,
                number: options.max_rating,
                scoreName: 'rating',
                starOn: 'star-light-on.png?v=100710',
                starOff: 'star-light-off.png?v=100710'
            });
        }

        function init() {
            $('#variantSel').d_eselect({ options : $('#variants'), onchange : changeVariant });
            $('#add2cart a').click(function() { buy(); return false; });
            initPhotoSlide();

            if (options.opinions_active == "1") {
                init_opinions();
            }
        }

        init();
    };

    
    m.Articles = function() {
        function init() {
            $('li.article div.price a').click(buy);
        }

        function buy() {
            var ids = $('em', this).text().split(',');
            $('#add2cart input[name=article]').val(ids[0]);
            if (ids.length > 1) {
                $('#add2cart input[name=variant]').val(ids[1]);
            }
            $('#add2cart').submit();
            return false;
        }

        init();
    };


    m.NewOrderEdit = function(order_id) {

        function init() {
            $('form.cart').d_shoppingCart({ orderMode: true, orderId: order_id });
            $('#courierSel').d_eselect({ options : $('#couriers'), onchange : changeCourier });
            $('#notes a').click(openNotesWindow)
        }

        function openNotesWindow() {
                var $fbox = $('#fboxNotes');
                $fbox.find('#id_notes').val($('#notes .notes-bckp').text());
                $(document).bind('close.facebox', setOrderNotes);

                $('#facebox div.content').children().appendTo('#fboxWindows');
                $.facebox($('#fboxNotes'), 'save');
                $fbox.find('#id_notes').focus();
                return false;
            }

        function setOrderNotes() {
                var $notes = $('#notes');
                var $cnt = $notes.find('.notes-cnt');
                var $fbox = $('#fboxNotes');
                var postdata = {
                    method : 'setOrderNotes',
                    params : JSON.stringify({
                        id : $('#id_id', $fbox).val(),
                        notes : $fbox.find('#id_notes').val()
                    })
                }

                function setOK(data) {
                    $cnt.html(data.result.notes.replace(/>/g,'&gt;').replace(/</g,'&lt;').replace(/\n/g, '<br />'));
                    $notes.find('.notes-bckp').text(data.result.notes);
                    if (data.result.notes) {
                        $notes.find('a').text('zmień');
                        $cnt.removeClass('empty');
                    }
                    else {
                        $notes.find('a').text('dodaj uwagi');
                        $cnt.addClass('empty');
                    }
                }
                function setFailed() {
                    $cnt.removeClass('atwork').addClass('error');
                    $cnt.text('wystąpił błąd');
                    $cnt.removeClass('empty');
                    $notes.find('.notes-bckp').text(data.result.notes);
                }

                $(document).unbind('close.facebox', setOrderNotes);
                $cnt.removeClass('error success').addClass('atwork');
                $cnt.text('zapisuję...');
                $.ajax({
                        type: 'post',
                        url: dshop.url_prefix+'/rpc/',
                        dataType: 'json',
                        data: postdata,
                        success: setOK,
                        error: setFailed });
            }

        function changeCourier(oldval, newval) {
            var $form = $('#courierForm');
            $form.find('input[name=action]').val('courier');
            $form.find('input[name=courier]').val(newval);
            $form.get(0).submit();
        }

        init();
    };


    m.NewOrderPayment = function() {
        function init() {
            $('#buyBtn').click(function() {
                $('#paymentForm').get(0).submit();
                return false;
            });

            $('ul.payments em, ul.payments li').not('li.disabled').not('li.disabled em').click(changePayment);
        }

        function changePayment() {
            $prevli = $(this).closest('ul').find('li.active');
            $prevli.removeClass('active');

            $li = $(this).closest('li');
            $li.addClass('active').find('input').get(0).checked = true;
        }

        init();
    };


    m.CompleteProfile = function() {
        function init() {
            if ($('select[name=clientType]').val() == 'P') {
                $('#li_companyName, #li_nip').hide();
            }
            
            $('select[name=clientType]').change(chClientType);
        }

        function chClientType() {
            if ($(this).val() == 'C') {
                $('#li_companyName, #li_nip').fadeIn();
            }
            else {
                $('#li_companyName, #li_nip').fadeOut();
            }
        }

        init();
    };

})(dshop.page);
