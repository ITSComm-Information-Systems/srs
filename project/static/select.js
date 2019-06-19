$(document).ready(function() {
	//Set bootstrap theme
	$.fn.select2.defaults.set( "theme", "bootstrap4" );

	// Search results limited to "starts with"
	function matchStart(params, data) {
	    params.term = params.term || '';
	    if (data.text.toUpperCase().indexOf(params.term.toUpperCase()) == 0) {
	        return data;
	    }
	    return false;
	}

	$("#deptf").select2({
		placeholder: "Select a department",
		width: "100%",
  		matcher: function(params, data) {
        	return matchStart(params, data);
    	}
	});

	// Search bar placeholder text
  	$("#deptf").one('select2:open', function(e) {
    	$('input.select2-search__field').prop('placeholder', 'Search...');
	});
  	$("#tolls_deptids").one('select2:open', function(e) {
    	$('input.select2-search__field').prop('placeholder', 'Search...');
	});
	$("#chart_deptids").one('select2:open', function(e) {
    	$('input.select2-search__field').prop('placeholder', 'Search...');
	});


	// Set select for tolls- choose dept
	$("#tolls_deptids").select2({
    	placeholder: "Select a department",
    	width: "100%",
    	matcher: function(params, data) {
        	return matchStart(params, data);
    	}
	});

	// tolls - choose billing period
	$("#tolls_billing").select2({
    	minimumResultsForSearch: Infinity,
    	placeholder: "Select a billing period"
	});


	// Set select for chartfield change - choose dept
	// $("#chart_deptids").select2({
 //    	placeholder: "Choose department",
 //    	matcher: function(params, data) {
 //        	return matchStart(params, data);
 //    	}
	// });

});