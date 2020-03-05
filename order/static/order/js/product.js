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
	    //$('.product-card').removeClass('selected-card').val('Select');
	    $(card).closest('.product-card').addClass('selected-card').val('Selected');
	    $(card).addClass('selected');

	    $(".product-card").removeClass("card-not-selected")
		$("#mustchoose").hide();
		$("#selecteditems").show();
		selected_items[name] = $(card).context.value;
		// Maya's Old code
		//  var result = ''
		//  for(var key in  selected_items)
		// 	result += ('<li class="ul-'+ $(card).attr('id') + '">' + selected_items[key] + " - " + key  +'</li>');
		// document.getElementById("items_list").innerHTML = result

		// Check to see if that item has been addded already to the list as an UL element
		var existingClass = ".ul-" ;
		existingClass += $(card).attr('id');
		if ($(existingClass).text() != "") {
			// If it is, then change the text of that UL element
			newtext = "" + selected_items[name] + " - " + name
			$(existingClass).text(newtext);
		}
		// If the UL tag doesn't exist, then create add a UL into the list type
		else {
			var newUL = '';
			newUL += ('<li class="ul-'+ $(card).attr('id') + '">' + selected_items[name] + " - " + name  +'</li>');
			
			document.getElementById("items_list").innerHTML += newUL
		}
	}
	else {
		$(card).closest('.product-card').removeClass("selected-card");
		$(card).removeClass('selected').removeClass('btn-outline-success');
		// If a product used be on their list, then remove it from their list
        var id = $(card).attr('id');
        $(".ul-"+id).remove();
	} 

}
