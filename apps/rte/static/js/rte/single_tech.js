$(document).ready(function() {
    // Table pop up on search
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

    // Hide input table on load
    $('#single-input').hide();

    // Transfer data from one tab to the next
    $('.single-next').on('click', function() {
        // Transition to work order input
        if (current_tab == 2) {
            techid_to_wo();
        }
        // Transition to review/submit tab
        if (current_tab == 3) {
            wo_to_review();
        }
    });

    // Keep track of number of rows in table
    num_entries = 0;

    // Submit entries
    $('.single-submit').on('click', function() {
        var form_html = '<input name="num_entries" type="text" value="' + num_entries + '" hidden>';
        $('#single-input-form').append(form_html);
        $('#single-input-form').submit();
    })

    // Add new row to input table
    $('#single-add').on('click', function() {
        if (validate_add()) {
            num_entries = add_to_table(num_entries);
            $('#add-error').addClass('hidden');
        }
    });

    $('#single-input-table').on('click', '.delete_row', function() {
        num_entries = delete_row($(this).attr('id'), num_entries);
    });
});

function validate_search() {
    if ($('#techSearch').val() === '') {
        $('#error-tech-id').show();
        return false;
    }
    return true;
}

// Transition from tech ID select to work order select
function techid_to_wo() {
    $('.tech_id').html($('#tech_id').val());
    $('.tech_id').val($('#tech_id').val());
    $('.tech_name').html($('#tech_name').val());
    $('.assigned_group').html($('#agSelect').val());
    $('.assigned_group').val($('#agSelect').val());
}

// Transition from work order select to review/submit
function wo_to_review() {
    $('#single-review').html('');
    $('#tech-info-review').html('');
    $('#single-review').append($("#single-input").html());
    $('#single-review tr').find('.delete-col').remove();
    $('#tech-info-review').append($("#tech-info-input").html());
}

// Add row to input table
function add_to_table(num_entries) {
    if (num_entries < 10) {
        num_entries = num_entries + 1; 
        var html = '<tr id="row-' + num_entries + '">' + 
                        '<th>' + $('#workOrderSearch').val() + '</th>' +
                        '<th>' + $('#rateSelect').val() + '</th>' +
                        '<th>' + $('#assigned_date').val() + '</th>' +
                        '<th>' + format_duration($('#duration-hours').val(), $('#duration-mins').val()) + '</th>' +
                        '<th>' + $('#notes').val() + '</th>' +
                        '<th class="delete-col"><button class="btn btn-danger delete_row" id="' + num_entries + '">Delete</button>' +
                    '</tr>';
        var form_html = '<input type="text" name="' + num_entries + '_work_order" value="' + $('#workOrderSearch').val() + '" hidden>' +
                        '<input type="text" name="' + num_entries + '_rate" value="' + $('#rateSelect').val() + '" hidden>' +
                        '<input type="date" name="' + num_entries + '_assigned_date" value="' + $('#assigned_date').val() + '" hidden>' +
                        '<input type="text" name="' + num_entries + '_duration" value="' + format_duration($('#duration-hours').val(), $('#duration-mins').val()) + '" hidden>' +
                        '<input type="text" name="' + num_entries + '_notes" value="' + $('#notes').val() + '" hidden>';
        $('#single-input-form').append(form_html);
        $('#single-input-table > tbody:last-child').append(html);
        $("#single-input").show();

        // Reset all input values
        $('#workOrderSearch').val('');
        $('#rateSelect').val('Regular');
        $('#assigned_date').val('');
        $('#duration-hours').val('');
        $('#duration-mins').val('');
        $('#notes').val('');
    }
    else {
        $('#max-entries').removeClass('hidden');
    }
    return(num_entries);
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

// Delete row in table
function delete_row(row_num, num_entries) {
    $('#row-' + row_num).remove();
    num_entries = num_entries - 1;
    $('#max-entries').addClass('hidden');

    if (num_entries == 0) {
        $('#single-input').hide();
    }
    return(num_entries);
}

// Make sure user enters tech ID
function validate_tech() {
    if (!$('#tech_id').val()) {
        console.log('here????');
        $('#tech-error').html('Please enter a tech ID.');
        $('#tech-error').removeAttr('hidden');
        return(false);
    }
    if (!$('#agSelect').val()) {
        $('#tech-error').html('Please select an assigned group.');
        $('#tech-error').removeAttr('hidden');
        return(false);
    } 
    return(true);
}

// Make sure all entry fields are filled
function validate_add() {
    console.log('validate add single');
    
    if (!$('#workOrderSearch').val()) {
        $('#add-error').html('Please enter a work order.');
        $('#add-error').removeClass('hidden');
        return(false);
    }

    if (!$('#assigned_date').val()) {
        $('#add-error').html('Please enter an assigned date.');
        $('#add-error').removeClass('hidden');
        return(false);
    }

    var regex = new RegExp('([12]\\d{3}-(0[1-9]|1[0-2])-(0[1-9]|[12]\\d|3[01]))');
    if (!regex.test($('#assigned_date').val())) {
        $('#add-error').html('Please enter a valid date. You entered: ' + $('#assigned_date').val() + '.');
        $('#add-error').removeClass('hidden');
        return(false);
    }

    if (!$('#duration-hours').val() && !$('#duration-mins').val()) {
        $('#add-error').html('Please enter time worked.');
        $('#add-error').removeClass('hidden');
        return(false);
    }

    if ($('#duration-hours').val() > 23 || $('#duration-hours').val() < 0) {
        $('#add-error').html('Please enter a value for hours between 0 and 23.');
        $('#add-error').removeClass('hidden');
        return(false);
    }

    if ($('#duration-mins').val() > 59 || $('#duration-mins').val() < 0) {
        $('#add-error').html('Please enter a value for minutes between 0 and 59.');
        $('#add-error').removeClass('hidden');
        return(false);
    }
    $('#entries-error').addClass('hidden');
    return(true);
}

// Make sure user has entered time
function validate_single_entries() {
    if ($('#single-input-table > tbody > tr').length === 0) {
        $('#entries-error').html('Please enter time before proceeding.');
        $('#entries-error').removeClass('hidden');
        return(false);
    }
    return(true);
}

// Validate moving on in workflow
function validate_single(current_tab) {
    if (current_tab === 1) {
        console.log('validate tech');
        return(validate_tech());
    }
    if (current_tab === 2) {
        console.log('validate single entries');
        return(validate_single_entries());
    }
}
