$(document).ready(function() {
	ph_count = 0;
	record_count = 0;

	// Enable first pill
	$("#cfc-1").removeClass('disabled');
	$("#cfc-line-1").removeClass('disabled');

	// Select first tab
	currStep = 1;
	lastStep = document.getElementsByClassName("tab-pane").length;
	$('#chartchange_nav li:first-child a').tab('show');

	// Select first option in dropdowns
	// $('#chart_deptids :first-child').prop('selected', true);
	// $('#cf_dropdown :first-child').prop('selected', true);

	// Hide chartfield selection if department doesn't have any
	if (cf_info) {
		$('#no_cfs_alert').hide();
	}
	else {
		$('.cf-dropdown-div').hide();
		$("#cfNextBtn").attr('disabled', 'true');
	}


	// Next/prev buttons
	$("#cfNextBtn").click(function(event) {
		nextPrev(1, table, cf_change_table, review_table);
	});
	$("#cfPrevBtn").click(function(event) {
		nextPrev(-1, table, cf_change_table, review_table);
	});

	$('#chart_deptids').find('[data-default]').each(function(){
		$(this).prop('selected', true);
	});

	// Create paginated tables
	var table = $('#cf_users_table').DataTable({
		"processing": true,
		"language": {
			"processing": "Loading..."
		 },
		"destroy": true,
		"lengthChange": false,
		"dom": 'rtp',
		"autoWidth":false,
		"ordering":false,
		'ajax': {
			url: '/chartchange/update-table/',
			method: 'GET',
			data: function(d) {
				d.selected = $('#cf_dropdown option:selected').text();
			},
			dataSrc: ""
		},
		'columns': [
			{ data: 'selected'},
			{ data: 'user_defined_id' },
			{ data: 'building' },
			{ data: 'mrc_charged' },
			{ data: 'toll_charged' },
			{ data: 'local_charged' }
		],
		'aoColumnDefs': [
			{ "targets": 0,
              "mRender": function (data, type, full, meta) {
                  return '<input type="checkbox" class="minimal"' + (data ? ' checked' : '') + '/>'; // this returns opposite???
              }
            },
            { "targets": [3],
              "mRender": function (data, type, full, meta) {
              	 if (data == 'Y') {
          			return '<i class="fa fa-check-circle" aria-hidden="true"></i>';
          		 }
          		 else {
          		 	return '<i class="far fa-times-circle"></i>';
          		 }
              }

            },
            { "targets": [4, 5],
              "mRender": function (data, type, row, full, meta) {
              	var type = row['user_defined_id'];
              	type = type.split('-');
              	type = type[0];
              	if (type == 'PH' | type == 'RA') {
              		if (data == 'Y') {
              			return '<i class="fa fa-check-circle" aria-hidden="true"></i>';
              		}
              		else {
              			return '<i class="far fa-times-circle"></i>';
              		}
              	}
              	else {
	                return 'N/A';
              	}
              }
            }
          ]
	});

	var cf_change_table = $('#cf_change_table').DataTable({
		"destroy": true,
		"lengthChange": false,
		"bFilter": false,
		"dom": 'rtp',
		"ordering":false,
	});

	var review_table =  $('#review_table').DataTable({
		"destroy": true,
		"lengthChange": false,
		"bFilter": false,
		"dom": 'rtp',
		"ordering":false
	});


	// Create search feature for Choose User IDs table
	$('#search_test').on( 'keyup', function () {
    	table.search($('#search_test').val()).draw();
  	});

  	// Prevent search from submitting
  	$('.noEnterSubmit').keypress(function(e){
    if ( e.which == 13 ) return false;
});

  	
	// Select all button - choose users
  	$("#select_all").on( "change", function() {
  		record_count = 0;
  		isChecked = false;
	 	if (document.getElementById('select_all').checked) {
	 		isChecked = true;
	 	}

	 	table.rows().every(function(index, element) {
	 		record_count = record_count + 1;
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

		// Maintain record count
		if (isChecked) {
			$('#record-count').html(record_count + ' Records Selected');
		}
		else {
			$('#record-count').html('0 Records Selected');
			record_count = 0;
		}
	});

	// Select all from current page
	$('#select_all_page').on('change', function() {
		isChecked = false;
		if (document.getElementById('select_all_page').checked) {
			isChecked = true;
		}

		// Select 10 records
		table.rows({page:'current'}).every(function(index, element) {
			var row = $(this.node());
			var col0 = row.find('td:first-child input[type="checkbox"]');
			 
			insideChecked = false;
			if (col0.is(':checked')) {
			    insideChecked = true;
			}

			if (isChecked != insideChecked) {
				col0.click();
			}
		})
	})


	// Select all button - assign new
  	$("#select_all_an").on( "change", function() {
  		isChecked = false;
	 	if (document.getElementById('select_all_an').checked) {
	 		isChecked = true;
	 	}

	 	cf_change_table.rows().every(function(index, element) {
			var row = $(this.node());
			var col0 = row.find('td:first-child input[type="checkbox"]');
			var starts_with = row.find('td:nth-child(2)').text().startsWith('PH') |
							  row.find('td:nth-child(2)').text().startsWith('RA');
			 
			insideChecked = false;
			if (col0.is(':checked')) {
			    insideChecked = true;
			}

			if (isChecked != insideChecked) {
				col0.click();
				maintain_checks(isChecked, starts_with);
			}
		});
	});


	// Change chartfields on page 3 with selected department
	$('#dept_dropdown_3').on('submit', function(e) {
		e.preventDefault();
		$.ajax({
			url: '/chartchange/ajax/',
			data: {
				'when': 'assign_new',
				'deptids':$('#dept_text_search').val()
			},
			dataType:'json',
			// Reset chartfield options when department changes
			success: function(data) {
				$('#select_cf_3').empty();
				var drp = document.getElementById('select_cf_3');
				var option = document.createElement("OPTION");
				drp.add(option);
				for (i = 0; i < data.length; ++i) {
					if (data[i].short_code != ""){
						var drp = document.getElementById('select_cf_3');
						var option = document.createElement("OPTION");
						// option.value = data[i].account_number;
						// option.text = data[i].account_number + " (Shortcode: " + data[i].short_code + ")";
						option.value = JSON.stringify(data[i]);
						option.text = data[i].short_code
						
						drp.add(option);
					}
				}

				$('#cf_chartfield_3').empty();
				var drp = document.getElementById('cf_chartfield_3');
				var option = document.createElement("OPTION");
				drp.add(option);
				for (i = 0; i < data.length; ++i) {
					var drp = document.getElementById('cf_chartfield_3');
					var option = document.createElement("OPTION");
					// option.value = data[i].account_number;
					// option.text = data[i].account_number + " (Shortcode: " + data[i].short_code + ")";
					option.value = JSON.stringify(data[i]);
					option.text = data[i].account_number
					
					drp.add(option);
				}
			}
		})	
	})

	$('#select_dept_3').on('change', function(e) {
		$("#select_cf_3").attr("disabled", "disabled")
		$("#cf_chartfield_3").attr("disabled", "disabled")
		
		e.preventDefault();
		$.ajax({
			url: '/chartchange/ajax/',
			data: {
				'when': 'assign_new',
				'deptids':$('#select_dept_3 option:selected').val().split("?")[0]
			},
			dataType:'json',
			// Reset chartfield options when department changes
			success: function(data) {
				$('#select_cf_3').empty();
				var drp = document.getElementById('select_cf_3');
				var option = document.createElement("OPTION");
				drp.add(option);
				for (i = 0; i < data.length; ++i) {
					if (data[i].short_code != "" && data[i].short_code != undefined){
						var drp = document.getElementById('select_cf_3');
						var option = document.createElement("OPTION");
						// option.value = data[i].account_number;
						// option.text = data[i].account_number + " (Shortcode: " + data[i].short_code + ")";
						option.value = JSON.stringify(data[i]);
						option.text = data[i].short_code
						
						drp.add(option);
					}
				}

				$('#cf_chartfield_3').empty();
				var drp = document.getElementById('cf_chartfield_3');
				var option = document.createElement("OPTION");
				drp.add(option);
				for (i = 0; i < data.length; ++i) {
					var drp = document.getElementById('cf_chartfield_3');
					var option = document.createElement("OPTION");
					// option.value = data[i].account_number;
					// option.text = data[i].account_number + " (Shortcode: " + data[i].short_code + ")";
					option.value = JSON.stringify(data[i]);
					option.text = data[i].account_number
					
					drp.add(option);
				}
				$("#new_dept_full_name").html($('#select_dept_3 option:selected').text())
				$("#new_dept_mgr").html($('#select_dept_3 option:selected').val().split("?")[1])

				$("#select_cf_3").attr("disabled", null)
				$("#cf_chartfield_3").attr("disabled", null)
			}
		})
	})

	
	// Record count
	$('#cf_users_table').on('change', 'tr', function() {
		var box = $(this).find('td:first-child input[type="checkbox"]');
		var checked = box.is(':checked');
		var select_all_checked = $('#select_all').is(':checked');
		if (checked && !select_all_checked) {
			record_count += 1;
		}
		else if (!checked) {
			record_count -= 1;
		}
		$('#record-count').html(record_count + ' Records Selected');
	})

	// Uncheck select from page when you switch page
	$('#cf_users_table').on('page.dt', function() {
		if ($('#select_all_page').is(':checked')) {
			$('#select_all_page').click();
		}
	})

	// MRC/Toll/Local checkbox functionality
	$('#cf_change_table').on('change', 'tr', function() {
		var box = $(this).find('td:first-child input[type="checkbox"]');
		var checked = box.is(':checked');
		var starts_with = $(this).find('td:nth-child(2)').text().startsWith('PH') |
						  $(this).find('td:nth-child(2)').text().startsWith('RA');
		maintain_checks(checked, starts_with);
	})


  	// Applies changes to table
	$('#apply').on("click", function() {
		selected = $("#select_cf_3 option:selected").text();

		cf_change_table.rows().every(function(index, element) {
			var row = $(this.node());
			var col0 = row.find('td:first-child input[type="checkbox"]'); // checkbox
			var col1 = row.find('td:nth-child(2)').text(); // User ID
			var col3 = row.find('td:nth-child(4)'); // MRC
			var col4 = row.find('td:nth-child(5)'); // toll
			var col5 = row.find('td:nth-child(6)'); // local
			 
			if (col0.is(':checked')) {
			    // If PH
			    if (col1.startsWith("PH") | col1.startsWith("RA")) {
			    	// Set MRC
			    	if ($('#mrc').is(':checked')) {
			    		col3.html(selected);
			    		col3.val(selected);
			    	}

			    	// Set toll
			    	if ($('#toll').is(':checked')) {
			    		col4.html(selected);
			    		col4.val(selected);
			    	}

			    	// Set local
			    	if ($('#local').is(':checked')) {
			    		col5.html(selected);
			    		col5.val(selected);
			    	}
			    }
			    // Non-PH
			    else {
			    	// Set MRC charges
			    	col3.html(selected);
			    	col3.val(selected);
			    }
			    col0.click();
			}
		})

		// Uncheck when necessary
		if (document.getElementById('mrc').checked) {
			document.getElementById('mrc').click();
		}
		if (document.getElementById('toll').checked) {
			document.getElementById('toll').click();
		}
		if (document.getElementById('local').checked) {
			document.getElementById('local').click();
		}
		if (document.getElementById('select_all_an').checked) {
	    	document.getElementById('select_all_an').click();
	    }
	    $('#toll').attr('disabled', 'disabled');
	    $('#local').attr('disabled', 'disabled');
	})

	
	// Update department for page 1 - AJAX
	$('#chart_deptids').on('change', function() {
		var selected = $('#chart_deptids').val();

		$.ajax({
			url: '/chartchange/ajax/',
			data: {
				'when': 'choose cf',
				'deptids':selected
			},
			dataType:'json',
			// Reset chartfield options when department changes
			success: function(data) {
				$('#cf_dropdown').empty();
				if (data.length < 1) {
					$("#cfNextBtn").attr('disabled', 'true');
					$('#cf_dropdown_group').hide();
					$('#cf_details').hide();
					$("#checkbox-1").hide()
					$('#no_cfs_alert').show();
				}
				else {
					$("#cfNextBtn").removeAttr('disabled');
					$('.cf-dropdown-div').show();
					$('#no_cfs_alert').hide();
					$('#cf_dropdown_group').show();
					$('#cf_details').show();
					$("#checkbox-1").show()
					var drp = document.getElementById('cf_dropdown');
					var option = document.createElement("OPTION");
					drp.add(option);
					for (i = 0; i < data.length; ++i) {
						if (data[i].short_code != ""){
							var option = document.createElement("OPTION");
							option.value = JSON.stringify(data[i]);
							// option.text = data[i].account_number + " (Shortcode: " + data[i].short_code + ")";
							option.text = data[i].short_code
							drp.add(option);
						}
					}
					


					var drp = document.getElementById('cf_chartfield');
					var option = document.createElement("OPTION");
					drp.add(option);
					for (i = 0; i < data.length; ++i) {
						var option = document.createElement("OPTION");
						option.value = JSON.stringify(data[i]);
						// option.text = data[i].account_number + " (Shortcode: " + data[i].short_code + ")";
						option.text = data[i].account_number
						drp.add(option);
					}
					// change_current_page(data[0]);


				}
				name_display = selected.split('?');
				$('#dept_title').html('Department: ' + name_display[0]);
				$('#dept_mgr').html(name_display[1].replace(",", ", "));
				$('.dept_full_name').html(name_display[0]);
				$('#cfc-2').addClass('disabled');
				$('#cfc-3').addClass('disabled');
				$('#cfc-4').addClass('disabled');
			}
		})
	})

	// Reload data when new chartfield is selected
	$('#cf_dropdown').on('change', function() {
		var sel = document.getElementById("cf_dropdown");
		var selected = sel.options[sel.selectedIndex].value;

		change_current_page(selected);

		$('#cfc-2').addClass('disabled');
		$('#cfc-3').addClass('disabled');
		$('#cfc-4').addClass('disabled');
	})

	$('#cf_chartfield').on('change', function() {
		var sel = document.getElementById("cf_chartfield");
		var selected = sel.options[sel.selectedIndex].value;

		$('#cf_dropdown').val(selected)
		$('#cf_dropdown').trigger('change')

		change_current_page(selected);

		$('#cfc-2').addClass('disabled');
		$('#cfc-3').addClass('disabled');
		$('#cfc-4').addClass('disabled');
	})

	$('#cf_chartfield_3').on('change', function() {
		var sel = document.getElementById("cf_chartfield_3");
		var selected = sel.options[sel.selectedIndex].value;
		$('#select_cf_3').val(selected)
		$('#select_cf_3').trigger('change')
	})

	$("#select_cf_3").on('change', function() {
		var sel = document.getElementById("select_cf_3");
		var selected = JSON.parse(sel.options[sel.selectedIndex].value);
		$("#new_chartfield").html(selected.account_number)
		$("#new_shortcode").html(selected.short_code)
		
	})

	$('#show_chartfield_check').on('change', function() {
		var cf_select = document.getElementById("cf_chartfield_form")
		var cf_dropdown = document.getElementById("cf_dropdown_group")
		if (cf_select.style.display == "none"){
			cf_select.style.display = "block"
			cf_dropdown.style.display = "none"
		}
		else{
			cf_select.style.display = "none"
			cf_dropdown.style.display = "flex"
		}
	})

	$('#show_chartfield_check_3').on('change', function() {
		var cf_select = document.getElementById("cf_chartfield_form_3")
		var cf_dropdown = document.getElementById("cf_dropdown_3")
		if (cf_select.style.display == "none"){
			cf_select.style.display = "block"
			cf_dropdown.style.display = "none"
		}
		else{
			cf_select.style.display = "none"
			cf_dropdown.style.display = "flex"
		}
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

function accept(){
	$(".page_4_style").addClass("bg-success")
	$(".page_4_style").addClass("text-white")
	$("#page_4_top_text").addClass("font-weight-bold")
	$("#page_4_top_text").addClass("text-success")
	$("#page_4_top_text").html("Accepted! The Requestor will be notified and access will be automatically granted shortly. You may leave this page.")
	$("#manager_submit").attr("disabled", "disabled")
	$("#manager_reject").attr("disabled", "disabled")
}


function reject(){
	$(".page_4_style").addClass("bg-danger")
	$(".page_4_style").addClass("text-white")
	$("#page_4_top_text").addClass("font-weight-bold")
	$("#page_4_top_text").addClass("text-danger")
	$("#page_4_top_text").html("Rejected! The Requestor will be notified shortly. You may leave this page.")
	$("#manager_submit").attr("disabled", "disabled")
	$("#manager_reject").attr("disabled", "disabled")
}


// Next/prev functionality
function nextPrev(n, table, cf_change_table, review_table) {
	
  // Validate before submit
  if (n ==1 && currStep == 3) {
  	if (!validate(cf_change_table)) {
  		$('#validate').removeClass('hidden');
  		return false;
  	}
  	else {
  		$('#validate').addClass('hidden');
  	}
  }

  if (currStep == lastStep) {
	$(".page_4_style").addClass("bg-success")
	$(".page_4_style").addClass("text-white")
	$("#page_4_top_text").addClass("font-weight-bold")
	$("#page_4_top_text").addClass("text-success")
	
	$("#page_4_top_text").html("Submitted! Nothing left to do. You will be informed when the authorizing department accepts or rejects the request.")
	document.body.scrollTop = 0;
  	document.documentElement.scrollTop = 0;
	$('#submit-form').submit();
	return
      
  }
  

  // Load third page correctly
  if (n == 1 && currStep == 2) {
  	load_3(table, cf_change_table);
  	if (table_empty(cf_change_table)) {
  		$('#empty-validate').removeClass('hidden');
  		return false;
  	}
  	else {
  		$('#empty-validate').addClass('hidden');
  	}
  }

  $('#cf-' + currStep).removeClass('active')
  $('#cf-' + currStep).removeClass('show')
  if (n == -1){
	$('#cfc-' + currStep).removeClass('active')
	$('#cfc-' + currStep).addClass('disabled')
	$('#cfc-line-' + currStep).addClass('disabled')
	
  }
  currStep = currStep + n;

  $('#cfc-'+currStep).removeClass('disabled');
  $('#cfc-'+currStep).addClass('active');
  $('#cfc-line-'+currStep).removeClass('disabled');

  $('#cf-' + currStep).addClass('active')
  $('#cf-' + currStep).addClass('show')
//   $('#chartchange_nav li:nth-child(' + currStep + ') a').tab('show');
  

  // Details up top
  if (n == 1 && currStep == 2) {
  	$('#dept_search').hide();
  	$('#select_dept').hide();
  	$("#cfPrevBtn").removeAttr('disabled');
  }
  if (n == -1 && currStep == 1) {
  	$('#dept_search').show();
  	$('#select_dept').show();
  	$("#cfPrevBtn").attr('disabled', 'disabled');
  }

  if (n == 1 && currStep == 4) {
  	load_4(cf_change_table, review_table);
  }

  
  	if (n == 1 && currStep == 4){
		$("#cfNextBtn").html("Submit")
	}
	else{
		$("#cfNextBtn").html("Next")
	}
}

function tab_handler(tab){
	for (var i = 1; i <= 4; i++){
		$('#cf-' + i).removeClass('active')
		$('#cf-' + i).removeClass('show')
	}
	$('#cf-' + tab).addClass('active')
	$('#cf-' + tab).addClass('show')
	if (tab < 4){
		$("#cfNextBtn").html("Next")
	}
	else{
		$("#cfNextBtn").html("Submit")
	}
}

// Navigation bar functionality
function tab_func1() {
	currStep = 1;
	record_count = 0;
	$('#record-count').html(record_count + ' Records Selected');
 	$('#dept_search').show();
  	$('#select_dept').show();
  	$("#cfPrevBtn").attr('disabled', 'disabled');
	$("#cfc-line-2").addClass('disabled');
	$("#cfc-line-3").addClass('disabled');
	$("#cfc-2").removeClass('active')
	$("#cfc-3").removeClass('active')
	$("#cfc-4").removeClass('active')
	$("#cfc-2").addClass('disabled')
	$("#cfc-3").addClass('disabled')
	$("#cfc-4").addClass('disabled')
	
	tab_handler(1)
}

function tab_func2() {
	if (!$('#cfc-2').hasClass('disabled')) {
		currStep = 2;
		$('#dept_search').hide();
		$('#select_dept').hide();
		$("#cfPrevBtn").removeAttr('disabled');
		$("#cfc-line-3").addClass('disabled');
		$("#cfc-3").removeClass('active')
		$("#cfc-4").removeClass('active')
		$("#cfc-3").addClass('disabled')
		$("#cfc-4").addClass('disabled')
		tab_handler(2)
	}
}

function tab_func3() {
	if (!$('#cfc-3').hasClass('disabled')) {
		currStep = 3;
		$('#dept_search').hide();
	  	$('#select_dept').hide();
	  	$("#cfPrevBtn").removeAttr('disabled');
		$("#cfc-line-3").removeClass('disabled');
		$("#cfc-4").removeClass('active')
		$("#cfc-4").addClass('disabled')
		tab_handler(3)
	  }
}

function tab_func4() {
	if (!$('#cfc-4').hasClass('disabled')) {
		currStep = 4;
		$('#dept_search').hide();
		$('#select_dept').hide();
		$("#cfPrevBtn").removeAttr('disabled');
		tab_handler(4)
	  }
}



// MRC/Toll/Local checkbox functionality
function maintain_checks(checked, starts_with) {
	var toll = $('#toll');
	var local = $('#local');

	// Enable toll and local if necessary
	if (checked && starts_with) {
		ph_count = ph_count + 1;
		if (toll.is(':disabled')) {
			toll.removeAttr('disabled');
			local.removeAttr('disabled');
		}

	}
	// Disable toll and local if necessary
	else if (!checked && starts_with) {
		ph_count = ph_count - 1;
		if (ph_count == 0) {
			if (toll.is(':checked')) {
				toll.click();
			}
			if (local.is(':checked')) {
				local.click();
			}
			toll.attr('disabled', 'disabled');
			local.attr('disabled', 'disabled');
		}
	}
	return ph_count;
}

// Updates chartfield information when changed
function change_current_page(selected) {
	// $('#cf_dropdown').val(selected)
	// $('#cf_chartfield').val(selected)
	// $('#cf_dropdown').trigger('change')
	// $('#cf_chartfield').trigger('change')
	// infinite loop :(

	if (typeof(selected) == "string") {
		selected = JSON.parse(selected);
	}

	

	var dept_title = $('#dept_title').text();
	dept_title = dept_title.split(':');
	dept_title = dept_title[1];
	var dept_mgr = $('#dept_mgr').text();


	$("#fund").html(selected.fund);
	$("#deptid").html(selected.deptid);
	$("#program").html(selected.program);
	$("#class_code").html(selected.class_code);
	$("#project_grant").html(selected.project_grant);
	$('#cf_shortcode').html(selected.short_code);
	$('#cf_nickname').html(selected.nickname);
	$('.cf_num').html(selected.account_number);
	if (selected.nickname) {
		$('.cf_nickname').html('(' + selected.nickname + ')');
	}
	$('#cf_users_table').DataTable().ajax.reload();
}


// Add selected rows to page 3
function load_3(table, cf_change_table) {
	cf_change_table.clear();

	table.rows().every(function(index, element) {
		var row = $(this.node());
		var col0 = row.find('td:first-child input[type="checkbox"]'); // checkbox
		var col1 = row.find('td:nth-child(2)').text();
		var charges = '';
		if (!(col1.startsWith('PH') | col1.startsWith('RA'))) {
			charges = 'N/A';
		}

		if (col0.is(':checked')) {
			cf_change_table.row.add([
				'<input type="checkbox">',
				row.find('td:nth-child(2)').text(),
				row.find('td:nth-child(3)').text(),
				'',
				charges,
				charges
			]).draw();
		}
	})
}

// Make sure table is filled out before submitting - this would be nice with a break statement
function validate(cf_change_table) {
	var get_out = false;
	cf_change_table.rows().every(function(index, element) {
		var row = $(this.node());
		var col1 = row.find('td:nth-child(2)').text(); // user defined ID
		var col3 = row.find('td:nth-child(4)').text(); // MRC
		var col4 = row.find('td:nth-child(5)').text(); // Toll
		var col5 = row.find('td:nth-child(6)').text(); // Local

		if (col1.startsWith('PH') | col1.startsWith('RA')) {
			if (col3 == '' && col4 == '' && col5 == '') {
				get_out = true;
			}
		}
		else {
			if (col3 == '') {
				get_out = true;
			}
		}
	})
	return !get_out;
}


// Load review and submit page
function load_4(cf_change_table, review_table) {
	review_table.clear();

	var current_cf = $('.current').text();
	cf_change_table.rows().every(function(index, element) {
		var row = $(this.node());
		var user_id = row.find('td:nth-child(2)').text()
		var building = row.find('td:nth-child(3)').text()
		var mrc = row.find('td:nth-child(4)').text()
		var toll = row.find('td:nth-child(5)').text()
		var local = row.find('td:nth-child(6)').text()

		review_table.row.add([
			user_id,
			building,
			mrc,
			toll,
			local
		]).draw();

		var dept_full_name = $("#dept_full_name").html()
		var dept_mgr = $("#dept_mgr").html()
		var user_full_name = $("#user_full_name").html()
		var new_dept_full_name = $("#new_dept_full_name").html()
		var new_dept_mgr = $("#new_dept_mgr").html()
		var new_chartfield = $("#new_chartfield").html()
		var new_shortcode = $("#new_shortcode").html()
		var optional_message = $("#optional_message").val()

		if (mrc == '') {
			mrc = current_cf;
		}
		else{
			mrc = new_chartfield
		}
		if (toll == '') {
			toll = current_cf;
		}
		else{
			toll = new_chartfield
		}
		if (local == '') {
			local = current_cf;
		}
		else{
			local = new_chartfield
		}


		

		var input = document.createElement("input");
        input.type = "hidden";
        input.name = user_id;
        input.value = user_id + '//' 
		+ building + "//" 
		+ mrc + '//' 
		+ toll + '//' 
		+ local + '//' 
		+ dept_full_name + "//"
		+ dept_mgr + "//"
		+ user_full_name + "//"
		+ new_dept_full_name + "//"
		+ new_dept_mgr + "//"
		+ new_chartfield + "//"
		+ new_shortcode + "//"
		+ optional_message
		;
		document.getElementById('submit-form').appendChild(input);
	})
	$("#review_table")[0].style.width = "100%";
	
}

function table_empty(table) {
	return !table.data().any();	
}