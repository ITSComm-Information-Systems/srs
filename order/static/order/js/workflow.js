$(document).ready(function() {
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
    console.log('test');
    if ($('#phone_type option:selected') > 1) {
      $('#nextBtn').prop('disabled', false);
    }
  });
  


});

// Workflow stuff
$('a[data-toggle="tab"]').on('shown.bs.tab', function(e) {
  currStep = $(this)[0].id.substring(10, 12) * 1;
  console.log(lastStep)
  if (currStep == lastStep) {
      document.getElementById("nextBtn").innerHTML = "Add to Cart";
  }
  $('#nextBtn').prop('disabled', false);
})

function nextPrev(n) {
  currStep = currStep + n;
  $('#pills-tab li:nth-child(' + currStep + ') a').tab('show');

  if (currStep > lastStep) {
      document.getElementById("workflowForm").submit();
      return false;
  }
}