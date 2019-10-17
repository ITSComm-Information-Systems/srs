function selectProductCard(card) {

    $(card).addClass('btn-outline-success');
    $('.product-card').removeClass('selected-card').val('Select');
    $(card).closest('.product-card').addClass('selected-card').val('Selected');
    $("button").removeClass('selected');
    $(card).addClass('selected');

    $(".product-card").removeClass("card-not-selected")
    $("#mustchoose").hide();

}
