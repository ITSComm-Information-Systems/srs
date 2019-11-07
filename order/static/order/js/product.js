 //dictionary for selected items to quantity
function filterProducts(obj) { 
    value = $( "#productCat option:selected" ).val();
    console.log(value);

    $('[data-product-category]').hide();
    $("[data-product-category='" + value + "']").show();

  }
  function selectProductCard(card,name) {
  	if($(card).context.value > 0){
	    $(card).addClass('btn-outline-success');
	    $('.product-card').removeClass('selected-card').val('Select');
	    $(card).closest('.product-card').addClass('selected-card').val('Selected');
	    $(card).addClass('selected');

	    $(".product-card").removeClass("card-not-selected")
		$("#mustchoose").hide();
		$("#selecteditems").show();
		selected_items[name] = $(card).context.value;
		 var result = ''
		 for(var key in  selected_items)
			result += ('<li>'+ selected_items[key] + " - " + key  +'</li>');
		document.getElementById("items_list").innerHTML = result
	}   

}
