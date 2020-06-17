$(document).ready(function() {
	// Pagination for results table
	var num_rows = $('#select-entries-table').find('tbody tr:has(td)').length;
	var rows_per_page = 15;
	var num_pages = Math.ceil(num_rows / rows_per_page);

	// Fill pagination with correct number of pages
    for (i = 0; i < num_pages; i++) {
        if (i < 2 || i > num_pages - 3) {
            $('<li class="page-item" id="' + (i + 1) +'"><a class="page-link">' + (i + 1) + '</a></li>').appendTo('#pagination');
        }
        else if (i == 2) {
            $('<li class="page-item" id="' + (i + 1) +'"><a class="page-link">...</a></li>').appendTo('#pagination');
        }
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

    	if (current_tab === 4) {
    		review_submit();
    	}
    })

    // Submit entries
    $('.update-submit').on('click', function() {
        var form_html = '<input name="num_entries" type="text" value="' +$('#review-update-table').find('tbody tr:has(td)').length + '" hidden>';
        $('#update-entries-form').append(form_html);
        $('#update-entries-form').submit();
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
	$('#update-entries-table tbody').html('');

	$('#select-entries-table tbody tr').each (function() {
		var row = $(this);
		var col0 = row.find('td:first-child input[type="checkbox"]'); // checkbox
		var work_order = row.find('td:nth-child(2)').text();
		var assigned_date = row.find('td:nth-child(3)').text();
		var duration_hours = split_duration(row.find('td:nth-child(4)').text(), 'hours');
		var duration_mins = split_duration(row.find('td:nth-child(4)').text(), 'mins');
		var rate_level = row.find('td:nth-child(5)').text();
		var assigned_group = row.find('td:nth-child(6)').text();
		var wo_labor_id = row.find('td:nth-child(7)').text();

		var rate_levels = $('#rate_levels').text();
		rate_levels = rate_levels.replace('[', '').replace(']', '').replace(/'/g, "").replace(/ /g, '');
		rate_levels = rate_levels.split(',');

		var assigned_groups = $('#assigned_groups').text();
		assigned_groups = assigned_groups.replace('[', '').replace(']', '').replace(/'/g, "");
		assigned_groups = assigned_groups.split(',');

		if (col0.is(':checked')) {
			var new_row = '<tr>' +
						  	  '<td>' + work_order + '</td>' +
						  	  '<td>' +
						  	  	    '<input class="form-control" type="date" value="' + format_date(assigned_date) + '">' +
						  	  '</td>' +
						  	  '<td>' +
								    "<input class='form-control d-inline col-6 hours' type='text' value='" + duration_hours + "' placeholder='HH'>" +
								    "<input class='form-control d-inline col-6 mins' type='text' value='" + duration_mins + "' placeholder='MM'>" +
						  	  '</td>' +
						  	  '<td>' +
						  	      '<select class="form-control">';

			for (i = 0; i < rate_levels.length; i++) {
				if (rate_levels[i] === rate_level) {
					new_row = new_row + '<option selected>' + rate_levels[i] + '</option>';
				}
				else {
					new_row = new_row + '<option>' + rate_levels[i] + '</option>';
				}
			}

			new_row = new_row + '</select>' +
							  	  '</td>' +
							  	  '<td>' +
							  	      '<select class="form-control">'

			for (i = 0; i < assigned_groups.length; i++) {
				if (assigned_groups[i].replace(/^\s+/g, '') === assigned_group) {
					new_row = new_row + '<option selected>' + assigned_groups[i].replace(/^\s+/g, '') + '</option>';
				}
				else {
					new_row = new_row + '<option>' + assigned_groups[i].replace(/^\s+/g, '') + '</option>';
				}
			}

			new_row = new_row + '</select>' +
							'</td>' +
							'<td>' +
								'<input class="form-control" type="text" placeholder="Enter a new note...">' +
							'</td>' +
							'<td hidden>' + wo_labor_id + '</td>' +
						'</tr>';

			$('#update-entries-table tbody:last-child').append(new_row);
			num_checked = num_checked + 1;
		}
	})
	return(num_checked);
}

// Copy rows to review submit page
function review_submit() {
	$('#tech-info-box').html('');
	$('#tech-info-box').append($('#tech-info').html());

	$('#review-update-table tbody').html('');

	var i = 1;
	$('#update-entries-table tbody tr').each (function() {
		var row = $(this);
		var work_order = row.find('td:nth-child(1)').text();
		var assigned_date = row.find('td:nth-child(2) input').val();
		var duration_hours = row.find('td:nth-child(3) .hours').val();
		var duration_mins = row.find('td:nth-child(3) .mins').val();
		var rate_level = row.find('td:nth-child(4) select').val();
		var assigned_group = row.find('td:nth-child(5) select').val();
		var notes = row.find('td:nth-child(6) input').val();
		var wo_labor_id = row.find('td:nth-child(7)').text();

		var new_row = '<tr>' +
					      '<td>' + work_order + '</td>' +
					      '<td>' + assigned_date + '</td>' +
					      '<td>' + format_duration(duration_hours, duration_mins) + '</td>' +
					      '<td>' + rate_level + '</td>' +
					      '<td>' + assigned_group + '</td>' +
					      '<td>' + notes + '</td>' +
					  '</td>'
		$('#review-update-table tbody:last-child').append(new_row);

		var form_html = '<input type="text" name="' + i + '_work_order" value="' + work_order + '" hidden>' +
                        '<input type="text" name="' + i + '_rate" value="' + rate_level + '" hidden>' +
                        '<input type="date" name="' + i + '_assigned_date" value="' + assigned_date + '" hidden>' +
                        '<input type="text" name="' + i + '_duration" value="' + format_duration(duration_hours, duration_mins) + '" hidden>' +
                        '<input type="text" name="' + i + '_assigned_group" value="' + assigned_group + '" hidden>' +
                        '<input type="text" name="' + i + '_notes" value="' + notes + '" hidden>' +
                        '<input type="text" name="' + i + '_wo_labor_id" value="' + wo_labor_id + '"hidden>';
        $('#update-entries-form').append(form_html);
        i = i + 1;
	})
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

// Format input date to HH:MM
function format_duration(hours, mins) {
    if (hours.length == 0) {
        hours = '00';
    }
    if (hours.length == 1) {
        hours = '0' + hours;
    }
    if (mins.length == 0) {
        mins = '00';
    }
    if (mins.length == 1){
        mins = '0' + mins;
    }
    return(hours + ':' + mins);
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

function validate_search_update() {
    if ($('#techSearch').val() === '') {
        $('#error-tech-id').show();
        return false;
    }
    return true;
}

// Validate selection of tech
function validate_tech_update() {
	if (!$('#tech_id').val()) {
        $('#error-notice').html('Please enter a  valid tech ID.');
        $('#error-notice').removeAttr('hidden');
        return(false);
    }
    return(true);
}

function validate_selection() {
	var num_checked = 0;
	$('#select-entries-table tbody tr').each(function() {
		var row = $(this);
		var col = row.find('td:first-child input[type="checkbox"]'); // checkbox

		if (col.is(':checked')) {
			num_checked = num_checked + 1;
		} 
	})

	if (num_checked === 0) {
		$('#num-checked-error').html('Please select entries to update.');
        $('#num-checked-error').removeAttr('hidden');
        return(false);
	}
	else if (num_checked > 10) {
		$('#num-checked-error').html('Please select no more 10 entries at a time.');
        $('#num-checked-error').removeAttr('hidden');
        return(false);
	}
	else {
		return(true);
	}
}

function validate_changes() {
	var success = true;
	$('#update-entries-table tbody tr').each(function() {
		var row = $(this);
		var assigned_date = row.find('td:nth-child(2) input').val();
		var duration_hours = row.find('td:nth-child(3) .hours').val();
		var duration_mins = row.find('td:nth-child(3) .mins').val();

		var regex = new RegExp('([12]\\d{3}-(0[1-9]|1[0-2])-(0[1-9]|[12]\\d|3[01]))');
	    if (!regex.test(assigned_date)) {
	        $('#update-error').html('Please enter a valid date. You entered: ' + assigned_date + '.');
	        $('#update-error').removeClass('hidden');
	        success = false;
	    }

	    if (!duration_hours && !duration_mins) {
	        $('#update-error').html('Please enter time worked.');
	        $('#update-error').removeClass('hidden');
	        success = false;
	    }

	    if (duration_hours > 23 || duration_hours < 0) {
	        $('#update-error').html('Please enter a value for hours between 0 and 23.');
	        $('#update-error').removeClass('hidden');
	        success = false;
	    }

	    if (duration_mins > 59 || duration_mins < 0) {
	        $('#update-error').html('Please enter a value for minutes between 0 and 59.');
	        $('#update-error').removeClass('hidden');
	        success = false;
	    }
	})
	return(success);
}

// Validate moving on in workflow
function validate_update() {
    if (current_tab === 1) {
    	return(validate_tech_update());
    }
    if (current_tab === 2) {
    	return(validate_selection());
    }
    if (current_tab === 3) {
    	return(validate_changes());
    }
}
