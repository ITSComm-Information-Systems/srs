$(document).ready(function() {
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
})