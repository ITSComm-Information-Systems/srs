document.addEventListener('DOMContentLoaded', function(event) {
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
		placeholder: "Search by Department Name or ID",
		display:"inline",
		// width: "100%",
  		// matcher: function(params, data) {
        // 	return matchStart(params, data);
    	// }
	});
	
	$("#id_user").select2({
		placeholder: "Select a User",
		display:"inline",
	});

	$("#cf_dropdown").select2({
		// placeholder: "-- Select your current shortcode --",
		display:"inline",
		sorter: data => data.sort((a, b) => a.text.localeCompare(b.text)),
	});

	$("#chart_deptids").select2({
		placeholder: "-- Select your current department --",
		display:"inline",
	});

	$("#select_dept_3").select2({
		placeholder: "-- Select new department --",
		display:"inline",
	});

	$("#select_cf_3").select2({
		placeholder: "-- Select new chartfield --",
		display:"inline",
		sorter: data => data.sort((a, b) => a.text.localeCompare(b.text)),
	});

	$("#cf_chartfield").select2({
		placeholder: "-- Select your current chartfield --",
		display:"inline",
	});

	$("#cf_shortcode_dr").select2({
		placeholder: "-- Select shortcode --",
		display:"inline",
	});

	$("#cf_shortcode_3").select2({
		placeholder: "-- Select new shortcode --",
		display:"inline",
	});

	// Search bar placeholder text
  	// $("#deptf").one('select2:open', function(e) {
    // 	$('input.select2-search__field').prop('placeholder', 'Search by department name or ID');
	// });
  	$("#tolls_deptids").one('select2:open', function(e) {
    	$('input.select2-search__field').prop('placeholder', 'Search...');
	});
	$("#chart_deptids").one('select2:open', function(e) {
    	$('input.select2-search__field').prop('placeholder', 'Search...');
	});
	$("#select_dept_3").one('select2:open', function(e) {
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
	
	$('#workOrderSearch').select2({
		placeholder: "Search...",
		display:"inline",
	});
	
	$('#techSearchMultiple').select2({
		placeholder: "Search...",
		display:"inline",
    });

	// $("#chart_deptids").siblings()[1].style.width = "auto";
});
