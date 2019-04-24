$(document).ready(function() {

  var x, i;
  x = document.getElementsByTagName("input");
  for (i = 0; i < x.length; i++) {
      x[i].className += " form-control";
  }


  $('#pills-step1').removeClass('disabled');  // Enable first pill, that is how it all starts.

  console.log('ready');
  currStep = 1;
  lastStep = document.getElementsByClassName("tab-pane").length;

  $('#pills-tab li:first-child a').tab('show'); // Select first tab

  $("#Conduit").hide();
  $("#PurchasePhone").hide();
  $("#ModelInfo").hide();
  $("#PhoneSetType").hide();
  $("#JackNumber").hide();

  

  // Phone Type Tab
  $("#Jack_Yes").click(function() {
    $("#JackNumber").show();
    $("#Conduit").hide();
  });

  $("#Jack_No").click(function() {
    $("#JackNumber").hide();
    $("#Conduit").show();
  });

  $("#Conduit_Yes").click(function() {
    $("#PurchasePhone").show();
  });

  $("#Conduit_No").click(function() {
    $("#PurchasePhone").show();
  });

  $("#PurchasePhone_Yes").click(function() {
    $("#PhoneSetType").show();
    $("#ModelInfo").hide();
  });

  $("#PurchasePhone_No").click(function() {
    $("#ModelInfo").show();
    $("#PhoneSetType").hide();
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
    if (!inp[i].checkValidity()) {
      inp[i].className += " invalid";
      valid = false;
    }
  }

  if (valid) {
    document.getElementsByClassName("tab-pane")[currStep-1].className += " finish";
    $("#workflowForm").removeClass('was-validated');
  } else {
    $("#workflowForm").addClass('was-validated');
  }
  return valid; // return the valid status
}