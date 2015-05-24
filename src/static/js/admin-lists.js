(function($) {
    $(document).ready(function() {

        $('body.main-order').each(function() {
            $('#result_list tr').each(function() {
                $(this).children().eq(2).removeClass('nowrap');
                $(this).addClass($('em.status-group', this).text());
                if (!adm.external_supplier && $('em.sent-to-supplier', this).text().length > 0) {
                    $(this).addClass('sent-to-supplier');
                }
            });
        });
        
        $('body.main-logentry').each(function() {
            $('h1').html('Dziennik systemowy');
            Cufon.replace('h1');
        });
    });
})(jQuery);
