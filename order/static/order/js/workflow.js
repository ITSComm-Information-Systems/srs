$(document).ready(function() {

  var x, i;
  x = $('input:not(:checkbox)');
  for (i = 0; i < x.length; i++) {
      x[i].className += " form-control";
  }

  $('#cfc1').removeClass('disabled');  // Enable first pill, that is how it all starts.

  currStep = 1;
  lastStep = document.getElementsByClassName("tab-pane").length;


  if ( $("h1").html() === 'TestWorkflows' ) {
    for (i = 1; i < lastStep+1; i++) {
      $('#pills-step'+ i).removeClass('disabled'); 
    }
  }

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

  $('#pills-tab li:first-child a').tab('show'); // Select first tab

  
  $("#buildingFields").hide();
  $("#buildingTable").hide();
  $("#Conduit").hide();
  $("#PurchasePhone").hide();
  $("#ModelInfo").hide();
  $("#PhoneSetType").hide();
  $("#JackNumber").hide();


  $("#PhoneSetType_B").click(function() {
    $("#cat3").show();
    $("#cat2").hide();
    $("#cat1").hide();
    $("#rescat3").show();
    $("#rescat2").hide();
    $("#rescat1").hide();
  });

  $("#PhoneSetType_A").click(function() {
    $("#cat2").show();
    $("#cat1").hide();
    $("#cat3").hide();
    $("#rescat2").show();
    $("#rescat1").hide();
    $("#rescat3").hide();
  });

  $("#PhoneSetType_V").click(function() {
    $("#cat1").show();
    $("#cat2").hide();
    $("#cat3").hide();
    $("#rescat1").show();
    $("#rescat2").hide();
    $("#rescat3").hide();
  });

  // Phone Type Tab
  $("#Jack_Y").click(function() {
    $("#JackNumber").show();
    $("#JackNumber_review").show();
    $("#Conduit").hide();
    $("#Conduit_review").hide();
  });

  $("#Jack_N").click(function() {
    $("#JackNumber").hide();
    $("#JackNumber_review").hide();
    $("#Conduit").show();
    $("#Conduit_review").show();
  });

  $("#JackNumber").keypress(function() {
    $("#PurchasePhone").show();
    $("#PurchasePhone_review").show();
  });

  $("#Conduit_Y").click(function() {
    $("#PurchasePhone").show();
    $("#PurchasePhone_review").show();
  });

  $("#Conduit_N").click(function() {
    $("#PurchasePhone").show();
    $("#PurchasePhone_review").show();
  });

  $("#PurchasePhone_Y").click(function() {
    $("#PhoneSetType").show();
    $("#PhoneSetType_review").show();
    $("#ModelInfo").hide();
    $("#ModelInfo_review").hide();
  });

  $("#PurchasePhone_N").click(function() {
    $("#ModelInfo").show();
    $("#ModelInfo_review").show();
    $("#PhoneSetType").hide();
    $("#PhoneSetType_review").hide();
  });


  $("#phone_type").click(function() {
    if ($('#phone_type option:selected') > 1) {
      $('#nextBtn').prop('disabled', false);
    }
  });

  $("#nextBtn").click(function(event) {
    nextPrev(1);
  });

  $("#prevBtn").click(function(event) {
    nextPrev(-1);
  });




});

// Workflow stuff
$('a[data-toggle="tab"]').on('shown.bs.tab', function(e) {
  currStep = $(this)[0].id.substring(10, 12) * 1;
  if (currStep == lastStep) {
      $('#nextBtn').html('Add to Cart');
  } else {
      $('#nextBtn').html('Next');
  }
  $('#nextBtn').prop('disabled', false);
})


function nextPrev(n) {

  if (n == 1 && !validateForm()) return false;

  currStep = currStep + n;
  $('#pills-step'+currStep).removeClass('disabled');
  $('#pills-tab li:nth-child(' + currStep + ') a').tab('show');
  if (currStep > lastStep) {
      $('#workflowForm').submit();
      return false;
  }
}


function validateForm() {
  inp = $("#step" + currStep + " :input:visible");
  valid = true;
  for (i = 0; i < inp.length; i++) {
    id = "#" + $(inp[i]).attr('id') + "_review";
    $(id).html($(inp[i]).val());
    if (!inp[i].checkValidity()) {
      inp[i].className += " invalid";
      valid = false;
    }
  }

    $("input[type='radio']:checked").each(function() { // Update review form with radio data
        var idVal = $(this).attr("id");
        id = "#id_" + $(this).attr("name") + "_review";
        $(id).html($("label[for='"+idVal+"']").text());
    });

  
  
  if (valid) {
    document.getElementsByClassName("tab-pane")[currStep-1].className += " finish";
    $("#workflowForm").removeClass('was-validated');
  } else {
    $("#workflowForm").addClass('was-validated');
  }
  return valid; // return the valid status
}