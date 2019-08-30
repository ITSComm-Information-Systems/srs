function filterProducts(obj) { 
    value = $( "#productCat option:selected" ).val();
    console.log(value);

    $('[data-product-category]').hide();
    $("[data-product-category='" + value + "']").show();

  }