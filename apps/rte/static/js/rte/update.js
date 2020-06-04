$(document).ready(function() {
	// Pagination for results table
	var num_rows = $('#update-results-table').find('tbody tr:has(td)').length;
	var rows_per_page = 10;
	var num_pages = Math.ceil(num_rows / rows_per_page);

	// Fill pagination with correct number of pages
    for (i = 0; i < num_pages; i++) {
        $('<li class="page-item" id="' + (i + 1) +'"><a class="page-link">' + (i + 1) + '</a></li>').appendTo('#pagination');
    }
    $('<li class="page-item" id="next"><a class="page-link" id="next-tab">Next</a></li>').appendTo('#pagination');

    // Fill table initially
    $('#update-results-table').find('tbody tr:has(td)').hide();
	var tr = $('#update-results-table tbody tr:has(td)');
	for (var i = 0; i <= rows_per_page - 1; i++) {
	    $(tr[i]).show();
	}
	var current_page = 1;
	$('#1').addClass('active');

	// Enable pagination
	$('.page-link').click(function(event) {
		current_page = paginate($(this).text(), rows_per_page, current_page, tr);
		next_prev(current_page, num_pages);
  	});

  	$("#techTable").hide();

    $("#techSearch").on("keyup", function() {
        $("#techTable").show();
        var value = $(this).val().toLowerCase();
        $("#techTable tr").filter(function() {
        $(this).toggle($(this).text().toLowerCase().indexOf(value) > -1)
        });
    });

    $('#techTable tr').click(function() {
        var tech_name = $(this).find("td").eq(1).html();   
        var tech_id = $(this).find("td").eq(0).html(); 
        $("#techSearch").val(tech_id + ':' + tech_name);  
        $('#techTable').hide();
    });
})

/// Validate update/search submission
function validate() {
	if ($('#techid').val() === "") {
		$('#error-notice').html('Please enter a tech ID.');
		$('#error-notice').removeAttr('hidden');
		return false;
	}
	if ($('#date-start').val() === "" || $('#date-end').val() === "") {
		$('#error-notice').html("Please select a start and end date.");
		$('#error-notice').removeAttr('hidden');
		return false;
	}
	if ($('#date-start').val() > $('#date-end').val()) {
		$('#error-notice').html("Please select an end date after your selected start date.");
		$('#error-notice').removeAttr('hidden');
		return false;
	}
	return true;
}

// Pagination
function paginate(page, rows_per_page, current_page, tr) {
	$('#update-results-table').find('tbody tr:has(td)').hide();
	$('#' + current_page).removeClass('active');

	if (page === 'Next') {
		page = current_page + 1;
	}
	if (page === 'Previous') {
		page = current_page - 1;
	}

    var begin = (page - 1) * rows_per_page;
    var end = page * rows_per_page - 1;
    for (var i = begin; i <= end; i++) {
    	$(tr[i]).show();
    }

    $('#' + page).addClass('active');

    return(parseInt(page));
}

// Next/previous functionality
function next_prev(current_page, num_pages) {
	// Disable previous
	if (current_page === 1) {
		$('#previous').addClass('disabled');
		$('#previous-tab').attr('tabindex', '-1');
	}
	// Enable previous
	else {
		$('#previous').removeClass('disabled');
		$('#previous-tab').removeAttr('tabindex');
	}

	// Disable next
	if (current_page === num_pages) {
		$('#next').addClass('disabled');
		$('#next-tab').attr('tabindex', '-1');
	}
	// Enable next
	else {
		$('#next').removeClass('disabled');
		$('#next-tab').removeAttr('tabindex');
	}
}