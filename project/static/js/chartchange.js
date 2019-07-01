$(document).ready(function() {
	var ph_count = 0;

// Enable first pill, that is how it all starts
	$("#cfc-1").removeClass('disabled');


	// Select first tab
	currStep = 1;
	lastStep = document.getElementsByClassName("tab-pane").length;
	$('#chartchange_nav li:first-child a').tab('show');


	// Next/prev functionality
	$("#cfNextBtn").click(function(event) {
		nextPrev(1);
	});
	$("#cfPrevBtn").click(function(event) {
		nextPrev(-1);
	});


	// Create paginated tables
	var table = $('#cf_users_table').DataTable({
		"lengthChange": false,
		"dom": 'rtp'
	});

	var cf_change_table = $('#cf_change_table').DataTable({
		"lengthChange": false,
		"bFilter": false,
		"dom": 'rtp'
	});

	$('#review_table').DataTable({
		"lengthChange": false,
		"bFilter": false,
		"dom": 'rtp'
	});


	// Create search feature for Choose User IDs table
	$('#search_test').on( 'keyup', function () {
    	table.search($('#search_test').val()).draw();
  	});

  	
	// Select all button - choose users
  	$("#select_all").on( "change", function() {
  		isChecked = false;
	 	if (document.getElementById('select_all').checked) {
	 		isChecked = true;
	 	}

	 	table.rows().every(function(index, element) {
			var row = $(this.node());
			var col0 = row.find('td:first-child input[type="checkbox"]');
			 
			insideChecked = false;
			if (col0.is(':checked')) {
			    insideChecked = true;
			}

			if (isChecked != insideChecked) {
				col0.click();
			}
		});
	});


	// Select all button - assign new
  	$("#select_all_an").on( "change", function() {
  		isChecked = false;
	 	if (document.getElementById('select_all_an').checked) {
	 		isChecked = true;
	 	}

	 	cf_change_table.rows().every(function(index, element) {
			var row = $(this.node());
			var col0 = row.find('td:first-child input[type="checkbox"]');
			 
			insideChecked = false;
			if (col0.is(':checked')) {
			    insideChecked = true;
			}

			if (isChecked != insideChecked) {
				col0.click();
			}
		});
	});


  	// Applies changes to table
	$('#apply').on("click", function() {
		selected = $("#select_cf option:selected").text();

		cf_change_table.rows().every(function(index, element) {
			var row = $(this.node());
			var col0 = row.find('td:first-child input[type="checkbox"]'); // checkbox
			var col1 = row.find('td:nth-child(2)').val(); // User ID
			var col2 = row.find('td:nth-child(3)'); // building
			var col3 = row.find('td:nth-child(4)'); // MRC
			var col4 = row.find('td:nth-child(5)'); // toll
			var col5 = row.find('td:nth-child(6)'); // local

			var mrc, toll, local = false;
			 
			if (col0.is(':checked')) {
			    // If PH
			    if (col1.startsWith("PH") == 0) {
			    	// Set MRC - DONT FORGET TO SET VALUE
			    	if ($('#mrc').is(':checked')) {
			    		mrc = true;
			    		col3.html(selected);
			    		//col3.html('test');
			    	}

			    	// Set toll - DONT FORGET TO SET VALUE
			    	if ($('#toll').is(':checked')) {
			    		toll = true;
			    		col4.html(selected);
			    		$('#toll').click();
			    	}

			    	// Set local - DONT FORGET TO SET VALUE
			    	if ($('#local').is(':checked')) {
			    		local = true;
			    		col5.html(selected);
			    		$('#local').click();
			    	}
			    }
			    // Non-PH
			    else {
			    	// Set MRC charges
			    	col3.html(selected);
			    }
			    col0.click();
			}
		})

		// Uncheck when necessary
		if (mrc) {
			document.getElementById('mrc').click();
		}
		if (toll) {
			document.getElementById('toll').click();
		}
		if (local) {
			document.getElementById('local').click();
		}
		if (document.getElementById('select_all_an').checked) {
	    	document.getElementById('select_all_an').click();
	    }
	})

	
	// Update department for page 1
	$('#chart_deptids').on('change', function() {
		var sel = document.getElementById("chart_deptids");
		var selected = sel.options[sel.selectedIndex].value;
		$.ajax({
			url: '/chartchange/',
			type: "POST",
			data: {
				'deptids':selected
			},
			dataType:'json',
			success: function(data) {
				alert('Congratulations, Rachel! You were successful.');
			}
		})
	})

});

// Next->submit
$('a[data-toggle="tab"]').on('shown.bs.tab', function(e) {
  if (currStep == lastStep) {
      $('#cfNextBtn').html('Submit');
  } else {
      $('#cfNextBtn').html('Next');
  }
  $('#cfNextBtn').prop('disabled', false);
})


// Next/prev functionality
function nextPrev(n) {

  //if (n == 1 && !validateForm()6) return false;

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

  // Load third page correctly
  // if (n == 1 && currStep == 3) {
  // 	load_3();
  // }

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


function tab_func1() {
	currStep = 1;
	// $('#cfc_desc').show();
 //  	$('#dept_details').show();
  	$('#select_dept').show();
}

function tab_func2() {
	var test = $('#cfc-2');
	if (!$('#cfc-2').hasClass('disabled')) {
		currStep = 2;
		// $('#cfc_desc').hide();
	 //  	$('#dept_details').hide();
	}
	$('#select_dept').hide();
}

function tab_func3() {
	if (!$('#cfc-3').hasClass('disabled')) {
		currStep = 3;
		// $('#cfc_desc').hide();
	 //  	$('#dept_details').hide();
	  }
	  $('#select_dept').hide();
}

function tab_func4() {
	if (!$('#cfc-4').hasClass('disabled')) {
		currStep = 4;
		// $('#cfc_desc').hide();
	 //  	$('#dept_details').hide();
	  }
	  $('#select_dept').hide();
}

function maintain_checks(row_id) {
	//var tr = $(this).closest('tr');
	//var row = cf_change_table.rows('#' + row_id);
	var row = cf_change_table.row( $(this).parents('tr') ).data();
	var col = row.find('td:first-child input[type="checkbox"]'); // checkbox
	var toll = $('#toll');
	var local = $('#local');
	var user_id = row.find('td:nth-child(1)');

	// Enable toll and local if necessary
	if (col.is(':checked') && user_id.startsWith('PH')) {
		ph_count = ph_count + 1;
		if (toll.hasClass(disabled)) {
			toll.removeClass('disabled');
			local.removeClass('disabled');
		}

	}
	// Disable toll and local if necessary
	else if (!col.is(':checked') && user_id.startsWith('PH')) {
		ph_count = ph_count -1;
		if (ph_count == 0) {
			toll.addClass('disabled');
			local.addClass('disabled');
		}
	}
}

// function load_3() {
// 	var selected = [];

// 	cf_change_table.rows().every(function(index, element) {
// 			var row = $(this.node());
// 			var col0 = row.find('td:first-child input[type="checkbox"]'); // checkbox
// 			var col1 = row.find('td:nth-child(2)').val(); // User ID

// 			if (col0.is(':checked')) {
// 				selected.append(col1);
// 			}
// 		})

// 	$.ajax({
// 		url: '/chartchange/{{ dept_info.dept_id }}/',
// 		type: "POST",
// 		data: {
// 			'selected':selected
// 		},
// 		dataType:'json',
// 		success: function(data) {
// 			alert('Congratulations, Rachel! You were successful.');
// 		}
// 	})
// }
