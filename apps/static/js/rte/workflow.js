var current_tab = 0

$(document).ready(function() {
	// Show first page
    $('#pills-step1').removeClass('disabled');
    $('#pills-step1').addClass('active');
    $('#step1').removeClass('fade');
    $('#step1').addClass('active');
    current_tab = 1;
})

function next(num_tabs) {
	// Enable prev button
	$('#prevBtn').removeClass('disabled');

	// Validate next action
	if (!(current_tab < num_tabs && validate_next())) {
		return(false);
	}

	// Hide current page
	$('#step' + current_tab).addClass('fade');
	$('#step' + current_tab).removeClass('active');
	$('#pills-step' + current_tab).removeClass('active');

	// Enable next page
	current_tab = current_tab + 1;
	$('#pills-step' + current_tab).removeClass('disabled');
	$('#pills-step' + current_tab).addClass('active');
    $('#step' + current_tab).removeClass('fade');
    $('#step' + current_tab).addClass('active');

    // Disable if on last tab
    if (!(current_tab < num_tabs)) {
    	$('#nextBtn').addClass('disabled');
	}
}

function prev() {
	// Enable next button
	$('#nextBtn').removeClass('disabled');

	// Validate previous action
	if (!(current_tab != 1 && validate_prev())) {
		return(false);
	}

	// Hide current page
	$('#step' + current_tab).addClass('fade');
	$('#step' + current_tab).removeClass('active');
	$('#pills-step' + current_tab).removeClass('active');

	// Show previous page
	current_tab = current_tab - 1;
	$('#pills-step' + current_tab).addClass('active');
	$('#step' + current_tab).removeClass('fade');
    $('#step' + current_tab).addClass('active');

	// Disable if on first tab
	if (current_tab == 1) {
		$('#prevBtn').addClass('disabled');
	}
}

function validate_next() {
	return(true);
}

function validate_prev() {
	return(true);
}