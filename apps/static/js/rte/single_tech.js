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
    })
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
    $('.tech_id').html($('#tech_id').text());
    $('.tech_name').html($('#tech_name').text());
    $('.assigned_group').html($('#agSelect').val());
}

// Transition from work order select to review/submit
// function wo_to_review() {
//     $.ajax({
//         url: 'tech_id_to_wo/',
//         data: {
//             'techid': 'choose cf',
//             'tech_name':,
//             'assigned_group':
//         },
//         dataType:'json',
//         // Carry tech ID over to next tab
//         success: function(data) {
//             console.log('success');
//         }
//     })
// }