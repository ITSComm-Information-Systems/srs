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
		display:"inline",
		// width: "100%",
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

	$("#dept_id").one('select2:open', function(e) {
    	$('input.select2-search__field').prop('placeholder', 'Search...');
	});

	$("#doc_depts").one('select2:open', function(e) {
    	$('input.select2-search__field').prop('placeholder', 'Search...');
	});



	// Set select for tolls- choose dept
	$("#tolls_deptids").select2({
		minimumResultsForSearch: '3',
    	matcher: function(params, data) {
        	return matchStart(params, data);
    	}
	});

	// tolls - choose billing period
	$("#tolls_billing").select2({
    	minimumResultsForSearch: Infinity
	});


	// Set select for DOC - departments
	$('#doc_depts').select2({
		minimumResultsForSearch: '3',
		matcher: function(params, data) {
        	return matchStart(params, data);
    	}
	})

	// Set select for DOC - date
	$('#doc_bill_date').select2({
		minimumResultsForSearch: Infinity
	})

	// Set select for Inventory and Location - departments
	$('#dept_id').select2({
		minimumResultsForSearch: '3',
		matcher: function(params, data) {
        	return matchStart(params, data);
    	}
	})

	// Set select for Inventory and Location - bill period
	$('#bill_period').select2({
		minimumResultsForSearch: Infinity
	})

});