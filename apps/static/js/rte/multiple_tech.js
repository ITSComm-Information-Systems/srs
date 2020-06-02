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
        var work_order = $(this).find("td").eq(0).html();; 
        $("#workOrderSearchMultiple").val(work_order);  
        $('#workOrderTableMultiple').hide();
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

    // Submit entries
    $('.multiple-submit').on('click', function() {
        var form_html = '<input name="num_entries" type="text" value="' + num_entries + '" hidden>';
        $('multiple-input-form').append(form_html);
        $('#multiple-input-form').submit();
    })

    // Add new row to input table
    $('#multiple-add').on('click', function() {
        num_entries_multiple = add_to_multiple_table(num_entries_multiple);
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
                        '<th>' + $('#techSearchMultiple').val() + '</th>' +
                        '<th>' + $('#assignedGroupSelectMultiple').val() + '</th>' +
                        '<th>' + $('#rateSelectMultiple').val() + '</th>' +
                        '<th>' + $('#assigned_date_multiple').val() + '</th>' +
                        '<th>' + format_duration($('#duration-hours-multiple').val(), $('#duration-mins-multiple').val()) + '</th>' +
                        '<th>' + $('#notes-multiple').val() + '</th>' +
                        '<th><button class="btn btn-danger delete_row_multiple" id="' + num_entries + '">Delete</button>' +
                    '</tr>';
        var form_html = '<input type="text" name="' + num_entries + '_work_order" value="' + $('#workOrderSearchMultiple').val() + '" hidden>' +
                        '<input type="text" name="' + num_entries + '_assigned_group" value="' + $('#assignedGroupSelectMultiple').val() + '" hidden>' +
                        '<input type="text" name="' + num_entries + '_rate" value="' + $('#rateSelectMultiple').val() + '" hidden>' +
                        '<input type="date" name="' + num_entries + '_assigned_date" value="' + $('#assigned_date_multiple').val() + '" hidden>' +
                        '<input type="text" name="' + num_entries + '_duration" value="' + format_duration($('#duration-hours-multiple').val(), $('#duration-mins-multiple').val()) + '" hidden>' +
                        '<input type="text" name="' + num_entries + '_notes" value="' + $('#notes-multiple').val() + '" hidden>';
        $('#multiple-input-form').append(form_html);
        $('#multiple-input-table > tbody:last-child').append(html);
        $("#multiple-input").show();

        // Reset all input values
        $('#techSearchMultiple').val('');
        $('#assignedGroupSelectMultiple').val('');
        $('#rateSelectMultiple').val('Regular');
        $('#assigned_date_multiple').val('');
        $('#duration-hours-multiple').val('');
        $('#duration-mins-multiple').val('');
        $('#notes-multiple').val('');
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
    $('#max-entries-multiple').addClass('hidden');

    if (num_entries == 0) {
        $('#multiple-input').hide();
    }
    return(num_entries);
}


// Transition to time input tab
function wo_to_techid() {
    $('.work_order').html($('#work_order').val());
    $('.woek_order').val($('#work_order').val());
}

// Transition to review page
function techid_to_review() {
    $('#multiple-review').html('');
    $('#wo-info-review').html('');
    $('#multiple-review').append($("#multiple-input").html());
    $('#wo-info-review').append($("#wo-info-input").html());
}

// Get assigned groups for selected tech ID
function load_assigned_groups(techid) {
    console.log(techid);
    $.ajax({
        url: 'get-assigned-group/',
        data: {
            "techid": techid
        },
        dataType:'json',
        // Reset chartfield options when department changes
        success: function(data) {
            console.log(data);
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