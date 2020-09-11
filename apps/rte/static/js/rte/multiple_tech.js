$(document).ready(function() {
    // Table pop up on search
    $("#techTableMultiple").hide();

    $("#techSearchMultiple").on("keyup", function() {
        $("#techTableMultiple").show();
        var value = $(this).val().toLowerCase();
        $("#techTableMultiple tr").filter(function() {
        $(this).toggle($(this).text().toLowerCase().indexOf(value) > -1)
        });
    });

    $('#techTableMultiple tr').click(function() {
        var tech_name = $(this).find("td").eq(1).html();   
        var tech_id = $(this).find("td").eq(0).html(); 
        $("#techSearchMultiple").val(tech_id);  
        $('#techTableMultiple').hide();

        load_assigned_groups(tech_id);

        $('#assignedGroupSelectMultiple').removeAttr('disabled');
        $('#rateSelectMultiple').removeAttr('disabled');
        $('#assigned_date_multiple').removeAttr('readonly');
        $('#duration-hours-multiple').removeAttr('readonly');
        $('#duration-mins-multiple').removeAttr('readonly');
        $('#notes-multiple').removeAttr('readonly');
    });

    $("#workOrderTableMultiple").hide();

    $("#workOrderSearchMultiple").on("keyup", function() {
        $("#workOrderTableMultiple").show();
        var value = $(this).val().toLowerCase();
        $("#workOrderTableMultiple tr").filter(function() {
        $(this).toggle($(this).text().toLowerCase().indexOf(value) > -1)
        });
    });

    $('#workOrderTableMultiple tr').click(function() {
        var work_order = $(this).find("td").eq(0).html();
        var work_order_desc = $(this).find("td").eq(1).html(); 
        $("#workOrderSearchMultiple").val(''); 
        $('#work_order').val(work_order);
        $('#work_order_text').html(work_order_desc);
        $('#selected-wo').removeClass('hidden');
        $('#workOrderTableMultiple').hide();

        $('#wo-error').addClass('hidden');
    });

    // Hide input table on load
    $('#multiple-input').hide();

    // Transfer data from one tab to the next
    $('.multiple-next').on('click', function() {
        // Transition to work order input
        if (current_tab == 2) {
            wo_to_techid();
        }
        // Transition to review/submit tab
        if (current_tab == 3) {
            techid_to_review();
        }
    });

    // Keep track of number of rows in table
    num_entries_multiple = 0;
    total_entries = 0;

    // Submit entries
    $('.multiple-submit').on('click', function() {
        var form_html = '<input name="num_entries" type="text" value="' + total_entries + '" hidden>';
        $('#multiple-input-form').append(form_html);
        $('#multiple-input-form').submit();
    })

    // Add new row to input table
    $('#multiple-add').on('click', function() {
        if (validate_add_multiple()) {
            num_entries_multiple = add_to_multiple_table(num_entries_multiple);
            total_entries = total_entries + 1;
            $('#add-error').addClass('hidden');
        }
    });

    $('#multiple-input-table').on('click', '.delete_row_multiple', function() {
        num_entries_multiple = delete_row_multiple($(this).attr('id'), num_entries_multiple);
    });
});

// Add row to input table
function add_to_multiple_table(num_entries) {
    if (num_entries < 10) {
        num_entries = num_entries + 1; 
        var html = '<tr id="row-' + num_entries + '">' + 
                        '<td>' + $('#techSearchMultiple').val() + '</td>' +
                        '<td>' + $('#assignedGroupSelectMultiple').val() + '</td>' +
                        '<td>' + $('#rateSelectMultiple').val() + '</td>' +
                        '<td>' + $('#assigned_date_multiple').val() + '</td>' +
                        '<td>' + format_duration($('#duration-hours-multiple').val(), $('#duration-mins-multiple').val()) + '</td>' +
                        '<td>' + $('#notes-multiple').val() + '</td>' +
                        '<td class="delete-col"><button class="btn btn-danger delete_row_multiple" id="' + num_entries + '">Delete</button></td>' +
                    '</tr>';
        var form_html = '<input type="text" name="' + num_entries + '_techid" value="' + $('#techSearchMultiple').val() + '" hidden>' +
                        '<input type="text" name="' + num_entries + '_assigned_group" value="' + $('#assignedGroupSelectMultiple').val() + '" hidden>' +
                        '<input type="text" name="' + num_entries + '_rate" value="' + $('#rateSelectMultiple').val() + '" hidden>' +
                        '<input type="date" name="' + num_entries + '_assigned_date" value="' + $('#assigned_date_multiple').val() + '" hidden>' +
                        '<input type="text" name="' + num_entries + '_duration" value="' + format_duration($('#duration-hours-multiple').val(), $('#duration-mins-multiple').val()) + '" hidden>' +
                        '<input type="text" name="' + num_entries + '_notes" value="' + $('#notes-multiple').val() + '" hidden>';
        $('#multiple-input-form').append(form_html);
        $('#multiple-input-table > tbody:last-child').append(html);
        $("#multiple-input").show();

        $('#total-hours').text(calculate_duration_multiple());

        // Reset all input values
        $('#techSearchMultiple').val('');
        $('#assignedGroupSelectMultiple').val('');
        $('#rateSelectMultiple').val('Regular');
        $('#assigned_date_multiple').val('');
        $('#duration-hours-multiple').val('');
        $('#duration-mins-multiple').val('');
        $('#notes-multiple').val('');

        // Gray out inputs again
        $('#assignedGroupSelectMultiple').attr('disabled', 'disabled');
        $('#rateSelectMultiple').attr('disabled', 'disabled');
        $('#assigned_date_multiple').attr('readonly', 'readonly');
        $('#duration-hours-multiple').attr('readonly', 'readonly');
        $('#duration-mins-multiple').attr('readonly', 'readonly');
        $('#notes-multiple').attr('readonly', 'readonly');
    }
    else {
        $('#max-entries-multiple').removeClass('hidden');
    }
    return(num_entries);
}

// Delete row in table
function delete_row_multiple(row_num, num_entries) {
    $('#row-' + row_num).remove();
    num_entries = num_entries - 1;

    $('[name="' + row_num + '_techid"]').val('Deleted');

    if (num_entries == 0) {
        $('#multiple-input').hide();
    }

    $('#total-hours').text(calculate_duration_multiple());
    return(num_entries);
}


// Transition to time input tab
function wo_to_techid() {
    $('.work_order').html($('#work_order').val());
    $('.work_order').val($('#work_order').val());
    $('.comment_text').html($('#work_order_text').text());
}

// Transition to review page
function techid_to_review() {
    $('#multiple-review').html('');
    $('#wo-info-review').html('');
    $('#multiple-review').append($("#multiple-input").html());
    $('#multiple-review tr').find('.delete-col').remove();
    $('#wo-info-review').append($("#wo-info-input").html());
}

// Get assigned groups for selected tech ID
function load_assigned_groups(techid) {
    $.ajax({
        url: 'get-assigned-group/',
        data: {
            "techid": techid
        },
        dataType:'json',
        // Reset chartfield options when department changes
        success: function(data) {
            $('#assignedGroupSelectMultiple').empty();
            for (i = 0; i < data.length; ++i) {
                var drp = document.getElementById('assignedGroupSelectMultiple');
                var option = document.createElement("OPTION");
                option.value = data[i].wo_group_name;
                option.text = data[i].wo_group_name;
                drp.add(option);
            }
        },
        error: function(XMLHttpRequest, textStatus, errorThrown) {
            console.log(errorThrown);
        }
    })
}

function validate_search_multiple() {
    if ($('#workOrderSearch').val() === '') {
        $('#error-work-order').show();
        return false;
    }
    return true;
}

// Validate work order before advancing
function validate_wo() {
    if (!$('#work_order').val()) {
        $('#wo-error').html('Please enter a work order.');
        $('#wo-error').removeAttr('hidden');
        return(false);
    }
    return(true);
}

// Validate entries before advancing
function validate_multiple_entries() {
    if ($('#multiple-input-table > tbody > tr').length === 0) {
        $('#entries-error').html('Please enter time before proceeding.');
        $('#entries-error').removeClass('hidden');
        return(false);
    }
    return(true);
}

// Make sure all entry fields are filled
function validate_add_multiple() {
    $('#entries-error').addClass('hidden');

    if (!$('#techSearchMultiple').val()) {
        $('#add-error').html('Please enter a tech ID.');
        $('#add-error').removeClass('hidden');
        return(false);
    }

    if (!$('#assignedGroupSelectMultiple').val()) {
        $('#add-error').html('Please select an assigned group.');
        $('#add-error').removeClass('hidden');
        return(false);
    }

    if (!$('#assigned_date_multiple').val()) {
        $('#add-error').html('Please enter an assigned date.');
        $('#add-error').removeClass('hidden');
        return(false);
    }

    var regex = new RegExp('([12]\\d{3}-(0[1-9]|1[0-2])-(0[1-9]|[12]\\d|3[01]))');
    if (!regex.test($('#assigned_date_multiple').val())) {
        $('#add-error').html('Please enter a valid date. You entered: ' + $('#assigned_date_multiple').val() + '.');
        $('#add-error').removeClass('hidden');
        return(false);
    }

    if (!$('#duration-hours-multiple').val() && !$('#duration-mins-multiple').val()) {
        $('#add-error').html('Please enter time worked.');
        $('#add-error').removeClass('hidden');
        return(false);
    }

    if ($('#duration-hours-multiple').val() > 23 || $('#duration-hours-multiple').val() < 0 || $('#duration-hours-multiple').val() % 1 !=0) {
        $('#add-error').html('Please enter a value for hours between 0 and 23.');
        $('#add-error').removeClass('hidden');
        return(false);
    }

    mins = $('#duration-mins').val()
    console.log(mins, mins % 1)

    if ($('#duration-mins-multiple').val() > 59 || $('#duration-mins-multiple').val() < 0 ||  $('#duration-mins-multiple').val() % 1 !=0 ) {
        $('#add-error').html('Please enter a value for minutes between 0 and 59.');
        $('#add-error').removeClass('hidden');
        return(false);
    }
    $('#entries-error').addClass('hidden');
    return(true);
}

// Validate moving on in workflow
function validate_multiple() {
    if (current_tab === 1) {
        return(validate_wo());
    }
    if (current_tab === 2) {
        return(validate_multiple_entries());
    }
    return(true);
}

// Calculate total hours worked
function calculate_duration_multiple() {
    var hours = 0;
    var mins = 0;

    $('#multiple-input-table tbody tr').each(function() {
        var row = $(this);
        var duration = row.find('td:nth-child(5)').text();
        row_hours = split_duration(duration, 'hours');
        row_mins = split_duration(duration, 'mins');

        hours = hours + parseInt(row_hours);
        mins = mins + parseInt(row_mins);
    })

    hours = hours + Math.floor(mins / 60);
    mins = mins % 60;

    return format_duration(hours.toString(), mins.toString()); 
}