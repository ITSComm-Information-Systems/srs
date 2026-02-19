// Split duration into hours and mins
function split_duration(duration, part) {
    var split = duration.split(':');
    if (part === 'hours') {
        return split[0] ? split[0] : '0';
    } else {
        return split[1] ? split[1] : '0';
    }
}
// Central source of truth for all entries (global scope)
var entries = [];

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
            // Clear and rebuild the input table and hidden inputs from current visible rows
            var rows = [];
            $('#single-input-table > tbody').empty();
            // Gather all current hidden input values (non-deleted)
            var entry = 1;
            while (true) {
                var wo = $("input[name='" + entry + "_work_order']").val();
                var rate = $("input[name='" + entry + "_rate']").val();
                var date = $("input[name='" + entry + "_assigned_date']").val();
                var duration = $("input[name='" + entry + "_duration']").val();
                var notes = $("input[name='" + entry + "_notes']").val();
                if (typeof wo === 'undefined') break;
                if (wo !== 'Deleted') {
                    rows.push({wo: wo, rate: rate, date: date, duration: duration, notes: notes});
                }
                entry++;
            }
            // Remove all old hidden inputs
            $('#single-input-form input[type="text"][name$="_work_order"], #single-input-form input[type="text"][name$="_rate"], #single-input-form input[type="date"][name$="_assigned_date"], #single-input-form input[type="text"][name$="_duration"], #single-input-form input[type="text"][name$="_notes"]').remove();
            // Rebuild table and hidden inputs from rows
            for (var i = 0; i < rows.length; i++) {
                var idx = i + 1;
                var html = '<tr id="row-' + idx + '">' +
                    '<td>' + rows[i].wo + '</td>' +
                    '<td>' + (rows[i].rate || '') + '</td>' +
                    '<td>' + (rows[i].date || '') + '</td>' +
                    '<td id="row-' + idx + '-date">' + (rows[i].duration || '') + '</td>' +
                    '<td id="row-' + idx + '-notes">' + (rows[i].notes || '') + '</td>' +
                    '<td style="padding-right: 0px;" class="delete-col"><div style="float:right;">'+
                    '<button style="float: left;" class="btn btn-success" id="single-copy" onClick="copier(' + idx + ')" >Copy</button>' +
                    '<button style="float: right;" class="btn btn-danger delete_row" id="' + idx + '">Delete</button></div></td>' +
                    '</tr>';
                $('#single-input-table > tbody:last-child').append(html);
                // Add hidden inputs
                var form_html = '<input type="text" name="' + idx + '_work_order" value="' + rows[i].wo + '" hidden>' +
                    '<input type="text" name="' + idx + '_rate" value="' + (rows[i].rate || '') + '" hidden>' +
                    '<input type="date" name="' + idx + '_assigned_date" value="' + (rows[i].date || '') + '" hidden>' +
                    '<input type="text" name="' + idx + '_duration" value="' + (rows[i].duration || '') + '" hidden>' +
                    '<input type="text" name="' + idx + '_notes" value="' + (rows[i].notes || '') + '" hidden>';
                $('#single-input-form').append(form_html);
            }
            // Reset num_entries and total_entries_single to match the rebuilt rows
            num_entries = rows.length;
            total_entries_single = rows.length;
            $('#total-hours').text(calculate_duration());
        }
        // Transition to review/submit tab
        if (current_tab == 3) {
            wo_to_review();
        }
    });


    // Submit entries
    $('.single-submit').on('click', function() {
        var form_html = '<input name="num_entries" type="text" value="' + total_entries_single + '" hidden>';
        $('#single-input-form').append(form_html);
        $('#single-input-form').submit();
    })

    // Add new row to input table
    $('#single-add').on('click', function() {
        if (validate_add()) {
            if (entries.length < 15) {
                entries.push({
                    wo: $('#workOrderSearch').val(),
                    rate: $('#rateSelect').val(),
                    date: $('#assigned_date').val(),
                    duration: format_duration($('#duration-hours').val(), $('#duration-mins').val()),
                    notes: $('#notes').val()
                });
                rebuild_table_and_inputs();
                $('#add-error').addClass('hidden');
            } else {
                $('#max-entries').removeClass('hidden');
            }
        }
    });

    $('.form-group').on('keyup', function (e) {
        var key = e.which;
        if (key === 13) {
            if (validate_add()) {
                if (entries.length < 15) {
                    entries.push({
                        wo: $('#workOrderSearch').val(),
                        rate: $('#rateSelect').val(),
                        date: $('#assigned_date').val(),
                        duration: format_duration($('#duration-hours').val(), $('#duration-mins').val()),
                        notes: $('#notes').val()
                    });
                    rebuild_table_and_inputs();
                    $('#add-error').addClass('hidden');
                } else {
                    $('#max-entries').removeClass('hidden');
                }
            }
        }
    });

    $('#single-input-table').on('click', '.delete_row', function() {
        var idx = parseInt($(this).attr('id')) - 1;
        if (idx >= 0 && idx < entries.length) {
            entries.splice(idx, 1);
            rebuild_table_and_inputs();
        }
    });
// Helper to rebuild table and hidden inputs from entries array
function rebuild_table_and_inputs() {
    $('#single-input-table > tbody').empty();
    $('#single-input-form input[type="text"][name$="_work_order"], #single-input-form input[type="text"][name$="_rate"], #single-input-form input[type="date"][name$="_assigned_date"], #single-input-form input[type="text"][name$="_duration"], #single-input-form input[type="text"][name$="_notes"]').remove();
    for (var i = 0; i < entries.length; i++) {
        var idx = i + 1;
        var html = '<tr id="row-' + idx + '">' +
            '<td>' + entries[i].wo + '</td>' +
            '<td>' + (entries[i].rate || '') + '</td>' +
            '<td>' + (entries[i].date || '') + '</td>' +
            '<td id="row-' + idx + '-date">' + (entries[i].duration || '') + '</td>' +
            '<td id="row-' + idx + '-notes">' + (entries[i].notes || '') + '</td>' +
            '<td style="padding-right: 0px;" class="delete-col"><div style="float:right;">'+
            '<button style="float: left;" class="btn btn-success" id="single-copy" onClick="copier(' + idx + ')" >Copy</button>' +
            '<button style="float: right;" class="btn btn-danger delete_row" id="' + idx + '">Delete</button></div></td>' +
            '</tr>';
        $('#single-input-table > tbody:last-child').append(html);
        var form_html = '<input type="text" name="' + idx + '_work_order" value="' + entries[i].wo + '" hidden>' +
            '<input type="text" name="' + idx + '_rate" value="' + (entries[i].rate || '') + '" hidden>' +
            '<input type="date" name="' + idx + '_assigned_date" value="' + (entries[i].date || '') + '" hidden>' +
            '<input type="text" name="' + idx + '_duration" value="' + (entries[i].duration || '') + '" hidden>' +
            '<input type="text" name="' + idx + '_notes" value="' + (entries[i].notes || '') + '" hidden>';
        $('#single-input-form').append(form_html);
    }
    if (entries.length > 0) {
        $("#single-input").show();
    } else {
        $("#single-input").hide();
    }
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
    // Clear review tables to prevent duplication
    $('#single-review').empty();
    $('#tech-info-review').empty();
    // Remove any previously appended hidden inputs to prevent duplication
    $('#single-input-form input[type="text"][name$="_work_order"], #single-input-form input[type="text"][name$="_rate"], #single-input-form input[type="date"][name$="_assigned_date"], #single-input-form input[type="text"][name$="_duration"], #single-input-form input[type="text"][name$="_notes"]').remove();
    // Re-append the current table and info
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
    // Gather all current entries from hidden inputs
    var rows = [];
    var entry = 1;
    while (true) {
        var wo = $("input[name='" + entry + "_work_order']").val();
        var rate = $("input[name='" + entry + "_rate']").val();
        var date = $("input[name='" + entry + "_assigned_date']").val();
        var duration = $("input[name='" + entry + "_duration']").val();
        var notes = $("input[name='" + entry + "_notes']").val();
        if (typeof wo === 'undefined') break;
        if (wo !== 'Deleted') {
            rows.push({wo: wo, rate: rate, date: date, duration: duration, notes: notes});
        }
        entry++;
    }
    // Add the new entry
    if (rows.length < 15) {
        rows.push({
            wo: $('#workOrderSearch').val(),
            rate: $('#rateSelect').val(),
            date: $('#assigned_date').val(),
            duration: format_duration($('#duration-hours').val(), $('#duration-mins').val()),
            notes: $('#notes').val()
        });
    } else {
        $('#max-entries').removeClass('hidden');
        return rows.length;
    }
    // Rebuild table and hidden inputs
    $('#single-input-table > tbody').empty();
    $('#single-input-form input[type="text"][name$="_work_order"], #single-input-form input[type="text"][name$="_rate"], #single-input-form input[type="date"][name$="_assigned_date"], #single-input-form input[type="text"][name$="_duration"], #single-input-form input[type="text"][name$="_notes"]').remove();
    for (var i = 0; i < rows.length; i++) {
        var idx = i + 1;
        var html = '<tr id="row-' + idx + '">' +
            '<td>' + rows[i].wo + '</td>' +
            '<td>' + (rows[i].rate || '') + '</td>' +
            '<td>' + (rows[i].date || '') + '</td>' +
            '<td id="row-' + idx + '-date">' + (rows[i].duration || '') + '</td>' +
            '<td id="row-' + idx + '-notes">' + (rows[i].notes || '') + '</td>' +
            '<td style="padding-right: 0px;" class="delete-col"><div style="float:right;">'+
            '<button style="float: left;" class="btn btn-success" id="single-copy" onClick="copier(' + idx + ')" >Copy</button>' +
            '<button style="float: right;" class="btn btn-danger delete_row" id="' + idx + '">Delete</button></div></td>' +
            '</tr>';
        $('#single-input-table > tbody:last-child').append(html);
        var form_html = '<input type="text" name="' + idx + '_work_order" value="' + rows[i].wo + '" hidden>' +
            '<input type="text" name="' + idx + '_rate" value="' + (rows[i].rate || '') + '" hidden>' +
            '<input type="date" name="' + idx + '_assigned_date" value="' + (rows[i].date || '') + '" hidden>' +
            '<input type="text" name="' + idx + '_duration" value="' + (rows[i].duration || '') + '" hidden>' +
            '<input type="text" name="' + idx + '_notes" value="' + (rows[i].notes || '') + '" hidden>';
        $('#single-input-form').append(form_html);
    }
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
    num_entries = rows.length;
    total_entries_single = rows.length;
    return num_entries;
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
    // Remove the row from the table and hidden inputs, then rebuild both
    var rows = [];
    var entry = 1;
    while (true) {
        var wo = $("input[name='" + entry + "_work_order']").val();
        var rate = $("input[name='" + entry + "_rate']").val();
        var date = $("input[name='" + entry + "_assigned_date']").val();
        var duration = $("input[name='" + entry + "_duration']").val();
        var notes = $("input[name='" + entry + "_notes']").val();
        if (typeof wo === 'undefined') break;
        if (entry != row_num && wo !== 'Deleted') {
            rows.push({wo: wo, rate: rate, date: date, duration: duration, notes: notes});
        }
        entry++;
    }
    $('#single-input-table > tbody').empty();
    $('#single-input-form input[type="text"][name$="_work_order"], #single-input-form input[type="text"][name$="_rate"], #single-input-form input[type="date"][name$="_assigned_date"], #single-input-form input[type="text"][name$="_duration"], #single-input-form input[type="text"][name$="_notes"]').remove();
    for (var i = 0; i < rows.length; i++) {
        var idx = i + 1;
        var html = '<tr id="row-' + idx + '">' +
            '<td>' + rows[i].wo + '</td>' +
            '<td>' + (rows[i].rate || '') + '</td>' +
            '<td>' + (rows[i].date || '') + '</td>' +
            '<td id="row-' + idx + '-date">' + (rows[i].duration || '') + '</td>' +
            '<td id="row-' + idx + '-notes">' + (rows[i].notes || '') + '</td>' +
            '<td style="padding-right: 0px;" class="delete-col"><div style="float:right;">'+
            '<button style="float: left;" class="btn btn-success" id="single-copy" onClick="copier(' + idx + ')" >Copy</button>' +
            '<button style="float: right;" class="btn btn-danger delete_row" id="' + idx + '">Delete</button></div></td>' +
            '</tr>';
        $('#single-input-table > tbody:last-child').append(html);
        var form_html = '<input type="text" name="' + idx + '_work_order" value="' + rows[i].wo + '" hidden>' +
            '<input type="text" name="' + idx + '_rate" value="' + (rows[i].rate || '') + '" hidden>' +
            '<input type="date" name="' + idx + '_assigned_date" value="' + (rows[i].date || '') + '" hidden>' +
            '<input type="text" name="' + idx + '_duration" value="' + (rows[i].duration || '') + '" hidden>' +
            '<input type="text" name="' + idx + '_notes" value="' + (rows[i].notes || '') + '" hidden>';
        $('#single-input-form').append(form_html);
    }
    if (rows.length == 0) {
        $('#single-input').hide();
    }
    $('#max-entries').addClass('hidden');
    $('#total-hours').text(calculate_duration());
    num_entries = rows.length;
    total_entries_single = rows.length;
    return num_entries;
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
    for (var i = 0; i < entries.length; i++) {
        var duration = entries[i].duration || '00:00';
        var row_hours = split_duration(duration, 'hours');
        var row_mins = split_duration(duration, 'mins');
        hours += parseInt(row_hours);
        mins += parseInt(row_mins);
    }
    hours = hours + Math.floor(mins / 60);
    mins = mins % 60;
    return format_duration(hours.toString(), mins.toString());
}

