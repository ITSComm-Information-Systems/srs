$(document).ready(function() {

    $("#buildingSearch").on("keyup", function() {
        $("#buildingTable").show();
        var value = $(this).val().toLowerCase();
        $("#buildingTable tr").filter(function() {
        $(this).toggle($(this).text().toLowerCase().indexOf(value) > -1)
        });
    });

    $('#buildingTable tr').click(function() {
        var building = $(this).find("td").eq(1).html();   
        var buildingCode = $(this).find("td").eq(0).html();   
        $('#buildingName').val(building);
        $('#buildingID').val(buildingCode);
        $("#buildingTable").hide();
        $("#buildingFields").show();
    });

});