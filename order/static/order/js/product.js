function filterProducts(obj) { 
    value = $( "#productCat option:selected" ).val();
    console.log(value);

    $('[data-product-category]').hide();
    $("[data-product-category='" + value + "']").show();

  }
  function selectProductCard(card) {
  	if($(card).context.value > 0){
	    $(card).addClass('btn-outline-success');
	    $('.product-card').removeClass('selected-card').val('Select');
	    $(card).closest('.product-card').addClass('selected-card').val('Selected');
	    $(card).addClass('selected');

	    $(".product-card").removeClass("card-not-selected")
	    $("#mustchoose").hide();
	}    

}
