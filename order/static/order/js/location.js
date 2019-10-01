$(document).ready(function() {

    $("#buildingFields").hide();
    $("#buildingTable").hide();
    $("#NewLocationDiv").hide();

    $("#buildingSearch").on("keyup", function() {
        $("#NewLocationDiv").show();
        $("#buildingTable").show();
        var value = $(this).val().toLowerCase();
        $("#buildingTable tr").filter(function() {
        $(this).toggle($(this).text().toLowerCase().indexOf(value) > -1)
        });
    });

    $('#buildingTable tr').click(function() {
        var building = $(this).find("td").eq(1).html();   
        var buildingCode = $(this).find("td").eq(0).html();   
        $('#id_new_building_name').val(building);
        $('#id_new_building_code').val(buildingCode);
        $("#buildingTable").hide();
        $("#buildingFields").show();
        $("#NewLocationDiv").hide();
    });

     $('#NewLocationDiv button').click(function() {
        $("#buildingTable").hide();
        $("#buildingFields").show();
        $("#NewLocationDiv").hide();
    });
    

    $('#buildingTable tr').on("keyup",function(e) {
        if((e.keyCode === 13)){
            var building = $(this).find("td").eq(1).html();   
            var buildingCode = $(this).find("td").eq(0).html();   
            $('#id_new_building_name').val(building);
            $('#id_new_building_code').val(buildingCode);
            $("#buildingTable").hide();
            $("#buildingFields").show();
            $("#NewLocationDiv").hide();
        }
    });

});