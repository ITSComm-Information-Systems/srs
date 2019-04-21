$(document).ready(function() {

  var x, i;
  x = document.getElementsByTagName("input");
  for (i = 0; i < x.length; i++) {
      x[i].className += " form-control";
      console.log('add class');
  }

  console.log('ready');
  currStep = 1;
  lastStep = document.getElementsByClassName("tab-pane").length;

  $('#pills-tab li:first-child a').tab('show'); // Select first tab

  //$('#nextBtn').prop('disabled', true);

  // Phone Type Tab
  $("#purchaseYes").click(function() {
      $("#byod").hide();
      $("#phone_type").show();
  });

  $("#purchaseNo").click(function() {
    $("#byod").show();
    $("#phone_type").hide();
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
  console.log('shown tab event: ' + currStep + " of " + lastStep);
  if (currStep == lastStep) {
      document.getElementById("nextBtn").innerHTML = "Add to Cart";
  } else {
    document.getElementById("nextBtn").innerHTML = "Next";
  }
  $('#nextBtn').prop('disabled', false);
})

function nextPrev(n) {

  if (n == 1 && !validateForm()) return false;

  currStep = currStep + n;
  $('#pills-tab li:nth-child(' + currStep + ') a').tab('show');
  if (currStep > lastStep) {
      console.log('test');
      document.getElementById("workflowForm").submit();
      console.log('two');
      return false;
  }
}



function validateForm() {
  // This function deals with validation of the form fields
  var x, y, i, valid = true;
  x = document.getElementsByClassName("tab-pane");
  console.log('validateForm:' + currStep + ' of ' + x.length);
  y = x[currStep-1].getElementsByTagName("input");
  // A loop that checks every input field in the current tab:
  for (i = 0; i < y.length; i++) {
    // If a field is empty...

    //if (y[i].value == "") {
    if (y[i].checkValidity()) {
      console.log('valid:' + y[i].name);
    } else {

      // add an "invalid" class to the field:
      y[i].className += " invalid";
      console.log('invalid:' + y[i].name);
      // and set the current valid status to false:
      valid = false;

    }
  }
  // If the valid status is true, mark the step as finished and valid:
  var form = $("#workflowForm");
  if (valid) {
    document.getElementsByClassName("tab-pane")[currStep-1].className += " finish";
    form.removeClass('was-validated');
  } else {
    form.addClass('was-validated');
  }
  return valid; // return the valid status
}