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

});

function validate_search() {
    if ($('#techSearch').val() === '') {
        $('#error-tech-id').show();
        return false;
    }
    return true;
}