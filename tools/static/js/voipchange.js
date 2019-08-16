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
      var buildingCampus = $(this).find('td').eq(2).html();  

      //$('#new_loc_table').removeAttr('hidden');
      $('#buildingID').val(buildingCode);
      $('#buildingName').val(building);
      $('#campus').val(buildingCampus);
      $('#buildingSearch').val('');
      
      $("#buildingTable").hide();
      $('#buildingFields').show();
      $("#roomselect").hide();
      $("#jackselect").hide();
      $('#buildingFloor').val('');
      $('#buildingRoom').val('');
      $('#buildingJack').val('');
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
    var message = validateForm();
    if (n == 1 && message != 'valid') {
      if (currStep == 1) {
        $('#old_error').html(message); 
      }
      if (currStep == 2) {
        $('#new_error').html(message);
      }
      return false;
    }
  
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
  if (!$('#vlc-1').hasClass('disabled')) {
  	currStep = 1;
  	// $('#vlc_desc').show();
   //  	$('#dept_details').show();
    
    $('#old_error').hide();
    $('#phoneselect').show();
    $('#phoneselect').show();
    document.getElementById("vl-1").className = "";
    document.getElementById("vl-2").className = "tab-pane fade";
    document.getElementById("vl-3").className = "tab-pane fade";
  }

}

function tab_func2() {
  if (!$('#vlc-2').hasClass('disabled')) {
    $('#new_error').hide();
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
}

function tab_func3() {
	if (!$('#vlc-3').hasClass('disabled')) {
		currStep = 3;
		// $('#vlc_desc').hide();
	 //  	$('#dept_details').hide();
   $('#phoneselect').hide();
  document.getElementById("vl-1").className = "tab-pane fade";
  document.getElementById("vl-2").className = "tab-pane fade";
  document.getElementById('vl-3').className = ""
	  }
}

function validateForm() {
  if (currStep == 1) {
    var valid = false;
    $('#curr_loc_table tr').each(function() {
      if($(this).find('td:first-child').find(':input').is(':checked')) {
        valid = true;
      }
    })
    if (valid) {
      return 'valid';
    }
    else {
      return 'Please select the current phone location.';
    }
  }
  // Make sure floor, room, and jack are supplied
  if (currStep == 2) {
    old_strings = ['campus', 'buildingName', 'buildingID', 'buildingFloor', 'buildingRoom', 'buildingJack'];

    for (i = 0; i < old_strings.length; ++i) {
      if (!$('#' + old_strings[i]).val()) {
        return 'Please provide the required information.';
      }
      else {
        var new_string = '#new-' + old_strings[i];
        $(new_string).html($('#' + old_strings[i]).val());
      }
    }
    return 'valid';
  }
  return 'valid';
}


  