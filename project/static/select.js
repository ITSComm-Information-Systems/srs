$(document).ready(function() {
	//Set bootstrap theme
	$.fn.select2.defaults.set( "theme", "bootstrap4" );

	// // Search results limited to "starts with"
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

	// Set select placeholder
	$("#html_test").select2({
    	placeholder: "Select a department",
    	width: "50%",
    	matcher: function(params, data) {
        	return matchStart(params, data);
    	}
	});

});