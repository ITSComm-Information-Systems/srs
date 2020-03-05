$(document).ready(function() {
	// Select first options by default
    $("#dept_id").prop("selectedIndex", 0);
    $("#bill_period").prop("selectedIndex", 0);

    // Filtering the report
    $('#applyfilters').on('click', function() {
    	alert('here');
    	$('invLocTable').each(function() {
    		alert('here');
    	})
    });
})