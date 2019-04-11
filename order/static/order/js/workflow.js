$( document ).ready(function() {

    currStep = 1;
    lastStep = document.getElementsByClassName("tab-pane").length;
    $('#pills-tab li:first-child a').tab('show'); // Select first tab

    //$('#nextBtn').disable();
    $('#nextBtn').prop('disabled', true);
});

// Workflow stuff
$('a[data-toggle="tab"]').on('shown.bs.tab', function (e) {
  currStep = $(this)[0].id.substring(10,12) *1;
  console.log(lastStep)
  if (currStep == lastStep) {
    document.getElementById("nextBtn").innerHTML = "Add to Cart";
  }
})

function nextPrev(n) {
  currStep = currStep + n;
  $('#pills-tab li:nth-child(' + currStep + ') a').tab('show') ;

  if (currStep > lastStep) {
    document.getElementById("workflowForm").submit();
    return false;
  }
}
