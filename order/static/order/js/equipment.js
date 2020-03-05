function selectProductCard(card) {
    $(".product-button").text('Select');
    $(card).addClass('btn-outline-success');
    $('.product-card').removeClass('selected-card').val('Select');
    $(card).closest('.product-card').addClass('selected-card').val('Selected');
    $("button").removeClass('selected');
    $(card).addClass('selected');
    $(card).text("Selected");

    $(".product-card").removeClass("card-not-selected")
    $("#mustchoose").hide();

}
