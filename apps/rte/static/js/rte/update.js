$(document).ready(function() {
	// Pagination for results table
	var num_rows = $('#select-entries-table').find('tbody tr:has(td)').length;
	var rows_per_page = 10;
	var num_pages = Math.ceil(num_rows / rows_per_page);

	// Fill pagination with correct number of pages
    for (i = 0; i < num_pages; i++) {
        $('<li class="page-item" id="' + (i + 1) +'"><a class="page-link">' + (i + 1) + '</a></li>').appendTo('#pagination');
    }
    $('<li class="page-item" id="next"><a class="page-link" id="next-tab">Next</a></li>').appendTo('#pagination');

    // Fill table initially
    $('#select-entries-table').find('tbody tr:has(td)').hide();
	var tr = $('#select-entries-table tbody tr:has(td)');
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
        $("#techSearch").val(tech_id);  
        $('#techTable').hide();
    });

    $('.update-next').on('click', function() {
    	if (current_tab === 3) {
    		copy_selected();
    	}
    })
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
	$('#select-entries-table').find('tbody tr:has(td)').hide();
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

// Copy selected rows for update
function copy_selected() {
	var num_checked = 0;

	$('#select-entries-table tr').each (function() {
		var row = $(this);
		var col0 = row.find('td:first-child input[type="checkbox"]'); // checkbox
		var work_order = row.find('td:nth-child(2)').text();
		var assigned_date = row.find('td:nth-child(3)').text();
		var duration_hours = split_duration(row.find('td:nth-child(4)').text(), 'hours');
		var duration_mins = split_duration(row.find('td:nth-child(4)').text(), 'mins');
		var rate_level = row.find('td:nth-child(5)').text();
		var assigned_group = row.find('td:nth-child(6)').text();
		var assigned_groups = $('#assigned_groups').text();
		assigned_groups = assigned_groups.replace('[', '').replace(']', '').replace("'", "").replace("'", "")
		assigned_groups = assigned_groups.split(',')
		console.log(assigned_groups);

		if (col0.is(':checked')) {
			var editable_row = $('#update-entries-table tbody tr').eq(num_checked);
			editable_row.find('td:nth-child(1)').html(work_order);
			editable_row.find('td:nth-child(2)').html('<input class="form-control" type="date" value="' + format_date(assigned_date) + '">');
			editable_row.find('td:nth-child(3)').html("<div class='form-inline'>" +
														"<input class='form-control col-2' type='text' value='" + duration_hours + "' placeholder='HH'>" +
														"<input class='form-control col-2' type='text' value='" + duration_mins + "' placeholder='MM'>" +
													  "</div>");
			num_checked = num_checked + 1;
		}
	})

	for (i = num_checked + 1; i <= 10; i++) {
		console.log(i);
		$('#update-entries-table tbody tr:nth-child(' + i + ')').remove();
		console.log('removed');
	}
}

// Split duration into hours and mins
function split_duration(duration, part) {
	split = duration.split(':');
	if (part === 'hours') {
		return(split[0]);
	}
	else {
		return(split[1]);
	}
}

// Format date
function format_date(date) {
	months = ['Jan.', 'Feb.', 'March', 'April', 'May', 'June', 'July', 'Aug.', 'Sept.', 'Oct.', 'Nov.', 'Dec.']
	date = date.split(' ');

	month = months.indexOf(date[0]);
	month = month + 1;
	if (month < 10) {
		month = '0' + month;
	}
	day = date[1].replace(',', '');

	if (day.length === 1) {
		day = '0' + day;
	}
	year = date[2];

	return(year + '-' + month + '-' + day);
}