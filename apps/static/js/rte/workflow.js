var current_tab = 0

$(document).ready(function() {
	// Show first page
    $('#pills-step1').removeClass('disabled');
    $('#pills-step1').addClass('active');
    $('#step1').removeClass('fade');
    $('#step1').addClass('active');
    current_tab = 1;

    $('#submitBtn').hide();
	$('#prevBtn').hide();

    $('.nav-link').on('click', function() {
		disabled = $(this).hasClass('disabled');
		if (disabled) {
			return false;
		}
		current_tab = parseInt($(this).attr('id').substr(-1));

		// First tab
    	if (current_tab === 1) {
    		$('#prevBtn').addClass('disabled');
			$('#prevBtn').hide();
    	}
    	else {
			$('#prevBtn').show();
    		$('#prevBtn').removeClass('disabled');
    	}

    	// Last tab
    	if (current_tab != $('ul.nav-pills>li').length) {
    		$('#nextBtn').show();
    		$('#submitBtn').hide();
    	}
    	else {
    		$('#nextBtn').hide();
    		$('#submitBtn').show();
    	}
    })

    $("form").submit(function () {  // Prevent multiple submissions
		// submit more than once return false
		$(this).submit(function () {
		  console.log('prevent click')
		  return false;
		});
		// submit once return true
		return true;
	  });


}) 

function next(num_tabs) {
	// Enable prev button
	$('#prevBtn').removeClass('disabled');

	// Validate next action
	if (!(current_tab < num_tabs && validate_next(current_tab))) {
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

    // Make submit if on last tab
    if (!(current_tab < num_tabs)) {
    	$('#nextBtn').hide();
    	$('#submitBtn').show();
	}
}

function prev() {
	// Enable next button
	$('#nextBtn').removeClass('disabled');

	// Validate previous action
	if (!(current_tab != 1)) {
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
    $('#nextBtn').show();
    $('#submitBtn').hide();

	// Disable if on first tab
	if (current_tab == 1) {
		$('#prevBtn').addClass('disabled');
	}
}

function validate_next(current_tab) {
	if ($('#nextBtn').hasClass('single-next')) {
		return(validate_single(current_tab));
	}
	if ($('#nextBtn').hasClass('multiple-next')) {
		return(validate_multiple(current_tab));
	}
	if ($('#nextBtn').hasClass('update-next')) {
		return(validate_update(current_tab));
	}
}