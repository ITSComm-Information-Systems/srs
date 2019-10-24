function selectLocationCard(card) {

    $(card).addClass('btn-outline-success');
    $('.location-card').removeClass('selected-card').val('Select');
    $(card).closest('.product-card').addClass('selected-card').val('Selected');
    $("button").removeClass('selected');
    $(card).addClass('selected');

    $(".location-card").removeClass("card-not-selected")
    $("#mustchoose").hide();

}