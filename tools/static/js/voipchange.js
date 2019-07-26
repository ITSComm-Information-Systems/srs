$(document).ready(function() {
	$("#vlc-1").removeClass('disabled');  // Enable first pill, that is how it all starts.

  currStep = 1;
    lastStep = 3; //document.getElementsByClassName("tab-pane").length;
    $("#buildingFields").hide();
    $("#buildingTable").hide();
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
  
  function getPathFromUrl(url) {
    return url.split("?")[0];
  }
});



function nextPrev(n) {

    //if (n == 1 && !validateForm()) return false;
  
    currStep = currStep + n;
    $('#vlc-'+currStep).removeClass('disabled');
    $('#voiplocation_nav li:nth-child(' + currStep + ') a').tab('show');
  
    // Details up top
    if (currStep == 1) {
        $('#phoneselect').show();
        document.getElementById("vl-1").className = "";
        document.getElementById("vl-2").className = "tab-pane fade";
        document.getElementById("vl-3").className = "tab-pane fade";
    }
    if (currStep == 2) {
        $('#phoneselect').hide();
        document.getElementById("vl-1").className = "tab-pane fade";
        document.getElementById("vl-2").className = "";
        document.getElementById('vl-3').className = "tab-pane fade"
    }
    if (currStep == 3) {
        $('#phoneselect').hide();
        document.getElementById("vl-1").className = "tab-pane fade";
        document.getElementById("vl-2").className = "tab-pane fade";
        document.getElementById('vl-3').className = ""
    }  
  
    // Next->submit
    $('a[data-toggle="tab"]').on('shown.bs.tab', function(e) {
      if (currStep == lastStep) {
          $('#vlNextBtn').html('Submit');
      } else {
          $('#vlNextBtn').html('Next');
      }
      $('#vlNextBtn').prop('disabled', false);
    });

    if (currStep > lastStep) {
      $('#voipLocationForm').submit();
      return false;
  }
}

function tab_func1() {
	currStep = 1;
	// $('#vlc_desc').show();
 //  	$('#dept_details').show();
  
  $('#phoneselect').show();
  $('#phoneselect').show();
  document.getElementById("vl-1").className = "";
  document.getElementById("vl-2").className = "tab-pane fade";
    document.getElementById("vl-3").className = "tab-pane fade";

}

function tab_func2() {
	var test = $('#vlc-2');
	if (!$('#vlc-2').hasClass('disabled')) {
		currStep = 2;
		// $('#vlc_desc').hide();
	 //  	$('#dept_details').hide();
	}
  $('#phoneselect').hide();
  document.getElementById("vl-1").className = "tab-pane fade";
  document.getElementById("vl-2").className = "";
  document.getElementById('vl-3').className = "tab-pane fade"
}

function tab_func3() {
	if (!$('#vlc-3').hasClass('disabled')) {
		currStep = 3;
		// $('#vlc_desc').hide();
	 //  	$('#dept_details').hide();
	  }
  $('#phoneselect').hide();
  document.getElementById("vl-1").className = "tab-pane fade";
  document.getElementById("vl-2").className = "tab-pane fade";
  document.getElementById('vl-3').className = ""
}


  