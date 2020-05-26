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
        // Submit info
        if (current_tab == 3 && $(this).html() === 'Submit') {
            submit_entry();
        }
        // Transition to review/submit tab
        if (current_tab == 3) {
            wo_to_review();
        }
    });

    // Add new row to input table
    $('#single-add').on('click', function() {
        add_to_table();
    });
});

function validate_search() {
    if ($('#techSearch').val() === '') {
        $('#error-tech-id').show();
        return false;
    }
    return true;
}

// function single_validate_next(current_page) {

// }

// function single_validate_prev(current_page) {

// }

// Transition from tech ID select to work order select
function techid_to_wo() {
    $('.tech_id').html($('#tech_id').val());
    $('.tech_name').html($('#tech_name').val());
    $('.assigned_group').html($('#agSelect').val());
}

// Transition from work order select to review/submit
function wo_to_review() {
    $('#single-review').append($("#single-input").html());
    $('#tech-info-review').append($("#tech-info-input").html());
}

// Transition from work order select to review/submit
function submit_entry() {
    $.ajax({
        url: 'submitted/',
        data: {
            // 'techid': 'choose cf',
            // 'tech_name':,
            // 'assigned_group':
            'test': ''
        },
        dataType:'json',
        // Carry tech ID over to next tab
        success: function(data) {
            console.log('success');
        }
    })
}

// Add row to input table
function add_to_table() {
    var html = '<tr>' + 
                    '<th>' + $('#workOrderSearch').val() + '</th>' +
                    '<th>' + $('#rateSelect').val() + '</th>' +
                    '<th>' + $('#assigned_date').val() + '</th>' +
                    '<th>' + format_date($('#duration-hours').val(), $('#duration-mins').val()) + '</th>' +
                    '<th>' + $('#notes').val() + '</th>' +
                '</tr>'
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

// Format input date to HH:MM
function format_date(hours, mins) {
    if (hours.length == 1) {
        hours = '0' + hours;
    }
    if (mins.length == 1){
        mins = '0' + mins;
    }
    return(hours + ':' + mins);
}