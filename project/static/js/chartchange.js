$(document).ready(function() {
	$("#cfc-1").removeClass('disabled');  // Enable first pill, that is how it all starts.

	currStep = 1;
	lastStep = document.getElementsByClassName("tab-pane").length;

	$('#chartchange_nav li:first-child a').tab('show'); // Select first tab

	$("#cfNextBtn").click(function(event) {
		nextPrev(1);
	});

	$("#cfPrevBtn").click(function(event) {
		nextPrev(-1);
	});

});

// // Workflow stuff
// $('a[data-toggle="tab"]').on('shown.bs.tab', function(e) {
//   currStep = $(this)[0].id.substring(10, 12) * 1;
//   if (currStep == lastStep) {
//       $('#cfNextBtn').html('Submit');
//   } else {
//       $('#cfNextBtn').html('Next');
//   }
//   $('#cfNextBtn').prop('disabled', false);
// })


function nextPrev(n) {

  //if (n == 1 && !validateForm()) return false;

  currStep = currStep + n;
  $('#cfc-'+currStep).removeClass('disabled');
  $('#chartchange_nav li:nth-child(' + currStep + ') a').tab('show');

  // Details up top
  if (n == 1 && currStep == 2) {
  	$('#cfc_desc').hide();
  	$('#dept_details').hide();
  	$('#select_dept').hide();
  }
  if (n == -1 && currStep == 1) {
  	$('#cfc_desc').show();
  	$('#dept_details').show();
  	$('#select_dept').show();
  }

  if (currStep > lastStep) {
      //$('#workflowForm').submit();
      return false;
  }
}


// function validateForm() {
//   inp = $("#step" + currStep + " :input:visible");
//   valid = true;
//   for (i = 0; i < inp.length; i++) {
//     id = "#" + $(inp[i]).attr('id') + "_review";
//     $(id).html($(inp[i]).val());
//     if (!inp[i].checkValidity()) {
//       inp[i].className += " invalid";
//       valid = false;
//     }
//   }

//     $("input[type='radio']:checked").each(function() { // Update review form with radio data
//         var idVal = $(this).attr("id");
//         id = "#id_" + $(this).attr("name") + "_review";
//         $(id).html($("label[for='"+idVal+"']").text());
//     });

  
  
//   if (valid) {
//     document.getElementsByClassName("tab-pane")[currStep-1].className += " finish";
//     $("#workflowForm").removeClass('was-validated');
//   } else {
//     $("#workflowForm").addClass('was-validated');
//   }
//   return valid; // return the valid status