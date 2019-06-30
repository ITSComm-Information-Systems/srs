$(document).ready(function() {
	$("#vlc-1").removeClass('disabled');  // Enable first pill, that is how it all starts.

	currStep = 1;
    lastStep = 3; //document.getElementsByClassName("tab-pane").length;
    
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

    $('#voiplocation_nav li:first-child a').tab('show'); // Select first tab
    document.getElementById("vl-1").className = "";

	$("#vlNextBtn").click(function(event) {
		nextPrev(1);
	});

	$("#vlPrevBtn").click(function(event) {
		nextPrev(-1);
	});

});

function nextPrev(n) {

    //if (n == 1 && !validateForm()) return false;
  
    currStep = currStep + n;
    $('#vlc-'+currStep).removeClass('disabled');
    $('#voiplocation_nav li:nth-child(' + currStep + ') a').tab('show');
  
    // Details up top
    if (currStep == 1) {
        $('#phoneselect').show();
        $('#current').show();
        $('#locations').show();
        $('#available').show();
        document.getElementById("vl-1").className = "";
        document.getElementById("vl-2").className = "tab-pane fade";
        document.getElementById("vl-3").className = "tab-pane fade";
    }
    if (currStep == 2) {
        $('#phoneselect').hide();
        $('#current').hide();
        $('#locations').hide();
        $('#available').hide();
        document.getElementById("vl-1").className = "tab-pane fade";
        document.getElementById("vl-2").className = "";
        document.getElementById('vl-3').className = "tab-pane fade"
    }
    if (currStep == 3) {
        $('#phoneselect').hide();
        $('#current').hide();
        $('#locations').hide();
        $('#available').hide();
        document.getElementById("vl-1").className = "tab-pane fade";
        document.getElementById("vl-2").className = "tab-pane fade";
        document.getElementById('vl-3').className = ""
    }  
  
    if (currStep > lastStep) {
        //$('#workflowForm').submit();
        return false;
    }
  }

  