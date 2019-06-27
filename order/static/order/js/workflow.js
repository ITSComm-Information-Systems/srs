$(document).ready(function() {

  var x, i;
  x = $('input:not(:checkbox)');
  for (i = 0; i < x.length; i++) {
      x[i].className += " form-control";
  }

  $('#pills-step1').removeClass('disabled');  // Enable first pill, that is how it all starts.

  currStep = 1;
  lastStep = document.getElementsByClassName("tab-pane").length;


  if ( $("h1").html() === 'TestWorkflows' ) {
    for (i = 1; i < lastStep+1; i++) {
      $('#pills-step'+ i).removeClass('disabled'); 
    }
  }

  $('#pills-tab li:first-child a').tab('show'); // Select first tab


  $("#buildingFields").hide();
  $("#phLocationFields").hide();
  $("#buildingTable").hide();
  $("#Conduit").hide();
  $("#PurchasePhone").hide();
  $("#ModelInfo").hide();
  $("#PhoneSetType").hide();
  $("#JackNumber").hide();
  $("#PhoneModelNum").hide();

  //Data
  $("#activePhone").hide();
  $("#jackNumber").hide();
  $("#conduit").hide();
  $("#linesToInstall").hide();

  $("#jack_Y").click(function() {
    $("#activePhone").show();
    $("#conduit").hide();
  });

  $("#jack_N").click(function() {
    $("#conduit").show();
    $("#activePhone").hide();
    $("#jackNumber").hide();
  });

  $("#jackNumber").keypress(function() {
    $("#activePhone").show();
  });

  $("#activePhone_Y").click(function() {
    $("#linesToInstall").show();
  });

  $("#activePhone_N").click(function() {
    $("#linesToInstall").show();
    $('#pills-step2').addClass(' hidden');
  });

  $("#conduit_Y").click(function() {
    $("#linesToInstall").show();
  });

  $("#conduit_N").click(function() {
    $("#linesToInstall").show();
  });

  // Addl info
  $('#contact_id').hide();
  $('#contact_name').hide();
  $('#contact_number').hide();

  //Phone
  $("#PhoneSetType_B").click(function() {
    basicPhone();
    $("#equip2").hide();
    $("#equip1").show();
  });

  $("#PhoneSetType_A").click(function() {
    advancedPhone();
  });

  $("#PhoneSetType_V").click(function() {
    voipPhone();
    $("#equip1").hide();
    $("#equip2").show();
  });

  $("#ModelInfo_V").click(function() {
    voipPhone();
    $("#PhoneModelNum").show();
  });
  
  $("#ModelInfo_A").click(function() {
    advancedPhone();
    $("#PhoneModelNum").show();
  });

  $("#ModelInfo_B").click(function() {
    basicPhone();
    $("#PhoneModelNum").show();
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
    $("#PhoneModelNum").hide();
    $('#pills-step3').removeClass(' hidden');
  });

  $("#PurchasePhone_N").click(function() {
    $("#ModelInfo").show();
    $("#ModelInfo_review").show();
    $("#PhoneSetType").hide();
    $("#PhoneSetType_review").hide();
    $('#pills-step3').addClass(' hidden');
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

  $("#contact_yn_False").click(function(event) {
    $('#contact_id').show();
    $('#contact_name').show();
    $('#contact_number').show();
  });

  $("#contact_yn_True").click(function(event) {
    $('#contact_id').hide();
    $('#contact_name').hide();
    $('#contact_number').hide();
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

  while ( $('#pills-step'+currStep).hasClass('hidden')) {
    currStep = currStep + n;
  }

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
    selected_text = $( "#" + inp[i].id + " option:selected" ).text()

    if (selected_text) {
      $(id).html(selected_text);
    } else {
      $(id).html($(inp[i]).val());
    }

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


// Features & Restrictions
function basicPhone() {
  $("#cat3").show();
  $("#cat2").hide();
  $("#cat1").hide();
  $("#rescat3").show();
  $("#rescat2").hide();
  $("#rescat1").hide();
}

function advancedPhone() {
    $("#cat2").show();
    $("#cat1").hide();
    $("#cat3").hide();
    $("#rescat2").show();
    $("#rescat1").hide();
    $("#rescat3").hide();
  }

  function voipPhone() {
    $("#cat1").show();
    $("#cat2").hide();
    $("#cat3").hide();
    $("#rescat1").show();
    $("#rescat2").hide();
    $("#rescat3").hide();
  }