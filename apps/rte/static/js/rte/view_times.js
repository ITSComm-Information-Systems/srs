$(document).ready(function() {
    // Table searches - tech ID
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


    // Table searches - work order
    $("#workOrderTable").hide();

    $("#workOrderSearch").on("keyup", function() {
        $("#workOrderTable").show();
        var value = $(this).val().toLowerCase();
        $("#workOrderTable tr").filter(function() {
        $(this).toggle($(this).text().toLowerCase().indexOf(value) > -1)
        });
    });

    $('#workOrderTable tr').click(function() {
        var work_order = $(this).find("td").eq(0).html();; 
        $("#workOrderSearch").val(work_order);  
        $('#workOrderTable').hide();
    });

    
    // Radio button functionality
    $('#selectByWorkOrderDiv').hide();
    $('#selectByCalendarRangeDiv').hide();
    $('#selectByDateRangeDiv').hide();

    $('#selectByWorkOrder').on('change', function() {
        $('#selectByWorkOrderDiv').show();
        $('#selectByCalendarRangeDiv').hide();
        $('#selectByDateRangeDiv').hide();
    });

    $('#selectByCalendarRange').on('change', function() {
        $('#selectByWorkOrderDiv').hide();
        $('#selectByCalendarRangeDiv').show();
        $('#selectByDateRangeDiv').hide();
    });

    $('#selectByDateRange').on('change', function() {
        $('#selectByWorkOrderDiv').hide();
        $('#selectByCalendarRangeDiv').hide();
        $('#selectByDateRangeDiv').show();
    });


    // Pagination for results table
    var num_rows = $('#view-time-table').find('tbody tr:has(td)').length;
    var rows_per_page = 10;
    var num_pages = Math.ceil(num_rows / rows_per_page);

    console.log(num_rows);

    // Fill pagination with correct number of pages
    for (i = 0; i < num_pages; i++) {
        // if (i < 4 || i > num_pages - 4) {
        //     $('<li class="page-item" id="' + (i + 1) +'"><a class="page-link">' + (i + 1) + '</a></li>').appendTo('#pagination');
        // }
        $('<li class="page-item" id="' + (i + 1) +'"><a class="page-link">' + (i + 1) + '</a></li>').appendTo('#pagination');
    }
    $('<li class="page-item" id="next"><a class="page-link" id="next-tab">Next</a></li>').appendTo('#pagination');

    // Fill table initially
    $('#view-time-table').find('tbody tr:has(td)').hide();
    var tr = $('#view-time-table tbody tr:has(td)');
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

    // Validation on submit
    $('#view-time-search').on('click', function() {
        valid = validate_submit();
        if (valid) {
            $('#view-times-form').submit();
        }
        else {
            $('#validate-error').removeAttr('hidden');
        }
    })
})

// Pagination
function paginate(page, rows_per_page, current_page, tr) {
    $('#view-time-table').find('tbody tr:has(td)').hide();
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

// Next/previous functionality for pagination
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

// Validation before search
function validate_submit() {
    // Tech ID
    if ($('#techSearch').val() === '') {
        $('#validate-error').html('Please enter a tech ID.');
        return(false);
    }

    else if (!$('#selectByWorkOrder').is(':checked') &&
             !$('#selectByCalendarRange').is(':checked') &&
             !$('#selectByDateRange').is(':checked')) {
        $('#validate-error').html('Please select another search option.');
        return(false);
    }

    // Additional search criteria
    else if ($('#selectByWorkOrder').is(':checked') && $('#workOrderSearch').val() === '') {
        $('#validate-error').html('Please enter a work order.');
        return(false);
    }
    // Calendar range
    else if ($('#selectByCalendarRange').is(':checked')) {
        // Missing start date
        if ($('#calendarRangeStart').val() === '') {
            $('#validate-error').html('Please enter a start date.');
            return(false);
        }
        // Missing end date
        else if ($('#calendarRangeEnd').val() === '') {
            $('#validate-error').html('Please enter an end date.');
            return(false);
        }
        // Invalid range
        else if ($('#calendarRangeStart').val() > $('#calendarRangeEnd').val()) {
            $('#validate-error').html('Please enter an end date past the start date.');
            return(false);
        }
    }
    // Date range
    else if ($('#selectByDateRange').is(':checked') && $('#dateRangeSelect').val() === '') {
        $('#validate-error').html('Please select a date range.');
        return(false);
    }

    return(true);
}
