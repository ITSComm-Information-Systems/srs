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
        $('#techTable').hide();
        get_assigned_groups(tech_id);
        $('#tech_name').val(tech_name);
        $('#tech_id').val(tech_id);
        $('#techSearch').val('');
        $('#tech-error').addClass('hidden');
    });

    $('#workOrderSearch').on('change', function() {
        $('#rateSelect').removeAttr('disabled');
        $('#assigned_date').removeAttr('readonly');
        $('#duration-hours').removeAttr('readonly');
        $('#duration-mins').removeAttr('readonly');
        $('#notes').removeAttr('readonly');
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
    total_entries_single = 0;

    // Submit entries
    $('.single-submit').on('click', function() {
        var form_html = '<input name="num_entries" type="text" value="' + total_entries_single + '" hidden>';
        $('#single-input-form').append(form_html);
        $('#single-input-form').submit();
    })

    // Add new row to input table
    $('#single-add').on('click', function() {
        if (validate_add()) {
            num_entries = add_to_table(num_entries);
            total_entries_single = total_entries_single + 1;
            $('#add-error').addClass('hidden');
        }
    });

    $('.form-group').on('keyup', function (e) {
        var key = e.which;
        if (key === 13) {
            if (validate_add()) {
                num_entries = add_to_table(num_entries);
                total_entries_single = total_entries_single + 1;
                $('#add-error').addClass('hidden');
            }
        }
      });

    $('#single-input-table').on('click', '.delete_row', function() {
        num_entries = delete_row($(this).attr('id'), num_entries);
    });

    $('#techSelect').on('change', function(){
        full_selection = $(this).val().split('(');
        tech_id = full_selection[0].replace(' ', '');
        tech_name = full_selection[1].replace(')', '');

        $('#tech_id').val(tech_id);
        $('#tech_name').val(tech_name);
        get_assigned_groups(tech_id);
    })
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

// Copy row
function copier(num){
    $('#workOrderSearch').val($('input[name="' + num + '_work_order"').val()).change();
    $('#rateSelect').val($('input[name="' + num + '_rate"').val())
    $('#duration-hours').val($('input[name="' + num + '_duration"').val().split(':')[0])
    $('#duration-mins').val($('input[name="' + num + '_duration"').val().split(':')[1])
}

// Add row to input table
function add_to_table(num_entries) {
    if (num_entries < 15) {
        num_entries = num_entries + 1; 
        var html = '<tr id="row-' + num_entries + '">' + 
                        '<td>' + $('#workOrderSearch').val() + '</td>' +
                        '<td>' + $('#rateSelect').val() + '</td>' +
                        '<td>' + $('#assigned_date').val() + '</td>' +
                        '<td id="row-' + num_entries + '-date" hour="' + $('#duration-hours').val() + 'minute="'+$('#duration-minute').val()+'">' + format_duration($('#duration-hours').val(), $('#duration-mins').val()) + '</td>' +
                        '<td id="row-' + num_entries + '-notes">' + $('#notes').val() + '</td>' +
                        '<td style="padding-right: 0px;" class="delete-col"><div style="float:right;">'+
                        '<button style="float: left;" class="btn btn-success" id="single-copy" onClick="copier('+num_entries+')" >Copy</button>' +
                        '<button style="float: right;" class="btn btn-danger delete_row" id="' + num_entries + '">Delete</button></div></td>' +
                    '</tr>';
        var form_html = '<input type="text" name="' + num_entries + '_work_order" value="' + $('#workOrderSearch').val() + '" hidden>' +
                        '<input type="text" name="' + num_entries + '_rate" value="' + $('#rateSelect').val() + '" hidden>' +
                        '<input type="date" name="' + num_entries + '_assigned_date" value="' + $('#assigned_date').val() + '" hidden>' +
                        '<input type="text" name="' + num_entries + '_duration" value="' + format_duration($('#duration-hours').val(), $('#duration-mins').val()) + '" hidden>' +
                        '<input type="text" name="' + num_entries + '_notes" value="' + $('#notes').val() + '" hidden>';
        $('#single-input-form').append(form_html);
        $('#single-input-table > tbody:last-child').append(html);
        $("#single-input").show();

        $('#total-hours').text(calculate_duration());

        // Reset all input values
        $("#workOrderSearch").val(null).trigger('change');
        $('#rateSelect').val('Regular');
        $('#assigned_date').val('');
        $('#duration-hours').val('');
        $('#duration-mins').val('');
        $('#notes').val('');

        // Reset grayed out input fields
        $('#rateSelect').attr('disabled', 'disabled');
        $('#assigned_date').attr('readonly', 'readonly');
        $('#duration-hours').attr('readonly', 'readonly');
        $('#duration-mins').attr('readonly', 'readonly');
        $('#notes').attr('readonly', 'readonly');
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
    //num_entries = num_entries - 1;
    $('#max-entries').addClass('hidden');

    $('[name="' + row_num + '_work_order"]').val('Deleted');

    if (num_entries == 0) {
        $('#single-input').hide();
    }
    $('#total-hours').text(calculate_duration());
    return(num_entries);
}

// Make sure user enters tech ID
function validate_tech() {
    if (!$('#tech_id').val()) {
        $('#tech-error').html('Please select a valid tech ID.');
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

    var regex = new RegExp('^([01]?[0-9]|2[0-3])$');
    if (!regex.test($('#duration-hours').val()) && $('#duration-hours').val() != '') {
        $('#add-error').html('Please enter a value for hours between 0 and 23.');
        $('#add-error').removeClass('hidden');
        return(false);
    }

    var regex = new RegExp('^([01]?[0-9]|[2-5][0-9])$');
    if (!regex.test($('#duration-mins').val()) && $('#duration-mins').val() != '') {
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
        return(validate_tech());
    }
    if (current_tab === 2) {
        return(validate_single_entries());
    }
}

// Get assigned groups based on tech ID
function get_assigned_groups(techid) {
    $.ajax({
        url: 'get-assigned-group/',
        data: {
            "techid": techid
        },
        dataType:'json',
        // Reset chartfield options when department changes
        success: function(data) {
            $('#agSelect').empty();
            for (i = 0; i < data.length; ++i) {
                var drp = document.getElementById('agSelect');
                var option = document.createElement("OPTION");
                option.value = data[i].wo_group_name;
                option.text = data[i].wo_group_name;
                drp.add(option);
            }
            $('#chosen_techid').removeAttr('hidden');
        },
        error: function(XMLHttpRequest, textStatus, errorThrown) {
            console.log(errorThrown);
        }
    })
}

// Calculate total hours worked
function calculate_duration() {
    var hours = 0;
    var mins = 0;

    $('#single-input-table tbody tr').each(function() {
        var row = $(this);
        var duration = row.find('td:nth-child(4)').text();
        row_hours = split_duration(duration, 'hours');
        row_mins = split_duration(duration, 'mins');

        hours = hours + parseInt(row_hours);
        mins = mins + parseInt(row_mins);
    })

    hours = hours + Math.floor(mins / 60);
    mins = mins % 60;

    return format_duration(hours.toString(), mins.toString()); 
}

