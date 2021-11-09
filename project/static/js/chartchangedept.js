document.addEventListener('DOMContentLoaded', function (event) {
	$("[data-toggle=popover]").popover(
		{
			trigger: "hover",
			template: '<div class="popover" role="tooltip"><div class="arrow"></div><div class="popover-body"></div></div>',
			html: true
		}
	);
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
	$('#chart_deptids :first-child').prop('selected', true);

	// Hide chartfield selection if department doesn't have any
	if (cf_info) {
		$('#no_cfs_alert').hide();
	}
	else {
		$('.cf-dropdown-div').hide();
		$("#cfNextBtn").attr('disabled', 'true');
	}


	// Next/prev buttons
	$("#cfNextBtn").click(function (event) {
		nextPrev(1, table, cf_change_table, review_table);
	});
	$("#cfPrevBtn").click(function (event) {
		nextPrev(-1, table, cf_change_table, review_table);
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
		"autoWidth": false,
		"ordering": false,
		'ajax': {
			url: '/chartchange/update-table/',
			method: 'GET',
			data: function (d) {
				d.selected = $('#cf_chartfield option:selected').text();
			},
			dataSrc: ""
		},
		'columns': [
			{ data: 'selected' },
			{ data: 'user_defined_id' },
			{ data: 'building' },
			{ data: 'mrc_charged' },
			{ data: 'toll_charged' },
			{ data: 'local_charged' }
		],
		'aoColumnDefs': [
			{
				"targets": 0,
				"mRender": function (data, type, full, meta) {
					return '<input type="checkbox" class="minimal"' + (data ? ' checked' : '') + '/>'; // this returns opposite???
				}
			},
			{
				"targets": [3],
				"mRender": function (data, type, full, meta) {
					if (data == 'Y') {
						return '<i class="fa fa-check-circle" aria-hidden="true"></i>';
					}
					else {
						return '<i class="far fa-times-circle"></i>';
					}
				}

			},
			{
				"targets": [4, 5],
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
		"ordering": false,
	});

	var review_table = $('#review_table').DataTable({
		"destroy": true,
		"lengthChange": false,
		"bFilter": false,
		"dom": 'rtp',
		"ordering": false
	});


	// Create search feature for Choose User IDs table
	$('#search_test').on('keyup', function () {
		table.search($('#search_test').val()).draw();
	});

	// Prevent search from submitting
	$('.noEnterSubmit').keypress(function (e) {
		if (e.which == 13) return false;
	});


	// Select all button - choose users
	$("#select_all").on("change", function () {
		record_count = 0;
		isChecked = false;
		if (document.getElementById('select_all').checked) {
			isChecked = true;
		}

		table.rows().every(function (index, element) {
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
	$('#select_all_page').on('change', function () {
		isChecked = false;
		if (document.getElementById('select_all_page').checked) {
			isChecked = true;
		}

		// Select 10 records
		table.rows({ page: 'current' }).every(function (index, element) {
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
	$("#select_all_an").on("change", function () {
		isChecked = false;
		if (document.getElementById('select_all_an').checked) {
			isChecked = true;
		}

		cf_change_table.rows().every(function (index, element) {
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
	$("#select_cf_3").attr("disabled", "disabled")
	$("#cf_shortcode_3").attr("disabled", "disabled")

	// Update department for page 3 - AJAX
	$('#select_dept_3').on('change', function (e) {
		$("#select_cf_3").attr("disabled", "disabled")
		$("#cf_shortcode_3").attr("disabled", "disabled")

		e.preventDefault();
		$.ajax({
			url: '/chartchangedept/ajax/',
			data: {
				'deptids': $('#select_dept_3 option:selected').val().split("?")[0]
			},
			dataType: 'json',
			// Reset chartfield options when department changes
			success: function (data) {
				$('#cf_shortcode_3').empty();
				var drp = document.getElementById('cf_shortcode_3');
				for (i = 0; i < data.length; ++i) {
					if (data[i].short_code != "" && data[i].short_code != undefined) {
						var drp = document.getElementById('cf_shortcode_3');
						var option = document.createElement("OPTION");
						option.value = JSON.stringify(data[i]);
						option.text = data[i].short_code;

						drp.add(option);
					}
				}

				$('#select_cf_3').empty();
				var drp = document.getElementById('select_cf_3');
				for (i = 0; i < data.length; ++i) {
					var drp = document.getElementById('select_cf_3');
					var option = document.createElement("OPTION");
					option.value = JSON.stringify(data[i]);
					option.text = data[i].account_number;

					drp.add(option);
				}
				$("#new_dept_full_name").html($('#select_dept_3 option:selected').text())
				$("#new_dept_mgr").html($('#select_dept_3 option:selected').val().split("?")[1])
				$("#new_dept_mgr_uniqname").html($('#select_dept_3 option:selected').val().split("?")[2])
				$("#new_dept_mgr_email").html($('#select_dept_3 option:selected').val().split("?")[2] + "@umich.edu")
				$("#select_cf_3").attr("disabled", null)
				$("#cf_shortcode_3").attr("disabled", null)
				$('#select_cf_3').trigger('change')
			}
		})
	})


	// Record count
	$('#cf_users_table').on('change', 'tr', function () {
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
	$('#cf_users_table').on('page.dt', function () {
		if ($('#select_all_page').is(':checked')) {
			$('#select_all_page').click();
		}
	})

	// MRC/Toll/Local checkbox functionality
	$('#cf_change_table').on('change', 'tr', function () {
		var box = $(this).find('td:first-child input[type="checkbox"]');
		var checked = box.is(':checked');
		var starts_with = $(this).find('td:nth-child(2)').text().startsWith('PH') |
			$(this).find('td:nth-child(2)').text().startsWith('RA');
		maintain_checks(checked, starts_with);
	})


	// Applies changes to table
	$('#apply').on("click", function () {
		selected = $("#select_cf_3 option:selected").text();

		cf_change_table.rows().every(function (index, element) {
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
	$('#chart_deptids').on('change', function () {
		var selected = $('#chart_deptids').val();
		$("#old_dept_mgr").html(selected.split("?")[1])
		$("#old_dept_mgr_uniqname").html(selected.split("?")[2])
		$("#old_dept_mgr_email").html(selected.split("?")[2] + "@umich.edu")
		$.ajax({
			url: '/chartchange/ajax/',
			data: {
				'deptids': selected
			},
			dataType: 'json',
			// Reset chartfield options when department changes
			success: function (data) {
				$('#cf_shortcode_dr').empty();
				$('#cf_chartfield').empty();
				if (data.length < 1) {
					$("#cfNextBtn").attr('disabled', 'true');
					$('#cf_details').hide();
					$("#cf_dropdown_row").hide()
					$('#no_cfs_alert').show();
				}
				else {
					$("#cfNextBtn").removeAttr('disabled');
					$('.cf-dropdown-div').show();
					$('#no_cfs_alert').hide();
					$("#cf_dropdown_row").show()
					$('#cf_details').show();

					var sc_drp = document.getElementById('cf_shortcode_dr');
					for (i = 0; i < data.length; ++i) {
						if (data[i].short_code != "") {
							var option = document.createElement("OPTION");
							option.value = JSON.stringify(data[i]);
							option.text = data[i].short_code
							sc_drp.add(option);
						}
					}

					var drp = document.getElementById('cf_chartfield');
					for (i = 0; i < data.length; ++i) {
						var option = document.createElement("OPTION");
						option.value = JSON.stringify(data[i]);
						option.text = data[i].account_number;
						drp.add(option);
					}

					change_current_page(data[0]);
				}
				name_display = selected.split('?');
				$('#dept_title').html('Department: ' + name_display[0]);

				$('#dept_mgr').html(name_display[1].replace(",", ", "));
				$('#old_dept_full_name').html(name_display[0]);
				$('#cfc-2').addClass('disabled');
				$('#cfc-3').addClass('disabled');
				$('#cfc-4').addClass('disabled');
			}
		})
	})
	$('#chart_deptids').trigger('change');

	// Reload data when new chartfield is selected
	$('#cf_chartfield').on('change', function () {
		change_current_page(document.getElementById("cf_chartfield").value);

		$('#cfc-2').addClass('disabled');
		$('#cfc-3').addClass('disabled');
		$('#cfc-4').addClass('disabled');
	})

	$('#cf_shortcode_dr').on('change', function () {
		if (($('#cf_shortcode_dr').val() != '') & ($('#cf_shortcode_dr').val() != $('#cf_chartfield').value)) {
			var selected = document.getElementById("cf_shortcode_dr").value

			$('#cf_chartfield').val(selected)
			$('#cf_chartfield').trigger('change')

			$('#cfc-2').addClass('disabled');
			$('#cfc-3').addClass('disabled');
			$('#cfc-4').addClass('disabled');
		}
	})

	$('#cf_shortcode_3').on('change', function () {
		if (($('#cf_shortcode_3').val() != '') & ($('#cf_shortcode_3').val() != $('#select_cf_3').value)) {
			var selected = document.getElementById("cf_shortcode_3").value
			$('#select_cf_3').val(selected)
			$('#select_cf_3').trigger('change')
		}
	})

	$("#select_cf_3").on('change', function () {
		var selected = JSON.parse(document.getElementById("select_cf_3").value);
		$("#new_chartfield").html(selected.account_number)
		$("#new_shortcode").html(selected.short_code)

	})

	$('#show_chartfield_check').on('change', function () {
		var chartfield = document.getElementById("cf_chartfield_form");
		var shortcode = document.getElementById("cf_shortcode_form");
		if (chartfield.style.display == "none") {
			chartfield.style.display = "block";
			shortcode.style.display = "none";
		}
		else {
			chartfield.style.display = "none"
			shortcode.style.display = "block"
			document.getElementById('cf_shortcode_dr').value = '';
			$('#cf_shortcode_dr').trigger('change')
		}
	})

	$('#show_chartfield_check_3').on('change', function () {
		var shortcode_form = document.getElementById("cf_shortcode_form_3");
		var cf_dropdown = document.getElementById("cf_dropdown_3");
		if (shortcode_form.style.display == "none") {
			shortcode_form.style.display = "block"
			cf_dropdown.style.display = "none"
		}
		else {
			shortcode_form.style.display = "none";
			cf_dropdown.style.display = "block";
			document.getElementById('cf_shortcode_3').value = '';
			$('#cf_shortcode_3').trigger('change')
		}
	})



});

// Next->submit
$('a[data-toggle="tab"]').on('shown.bs.tab', function (e) {
	if (currStep == lastStep) {
		$('#cfNextBtn').html('Submit');
	} else {
		$('#cfNextBtn').html('Next');
	}
	$('#cfNextBtn').prop('disabled', false);
})

// Next/prev functionality
function nextPrev(n, table, cf_change_table, review_table) {

	// Validate before submit
	if (n == 1 && currStep == 3) {
		if (!validate(cf_change_table)) {
			$('#validate').removeClass('hidden');
			return false;
		}
		else {
			$('#validate').addClass('hidden');
		}
	}

	if (n == 1 && (currStep == lastStep)) {
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
	if (n == -1) {
		$('#cfc-' + currStep).removeClass('active')
		$('#cfc-' + currStep).addClass('disabled')
		$('#cfc-line-' + currStep).addClass('disabled')
	}
	currStep = currStep + n;

	$('#cfc-' + currStep).removeClass('disabled');
	$('#cfc-' + currStep).addClass('active');
	$('#cfc-line-' + currStep).removeClass('disabled');

	$('#cf-' + currStep).addClass('active')
	$('#cf-' + currStep).addClass('show')

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

	if (n == 1 && currStep == 4) {
		$("#cfNextBtn").html("Submit")
	}
	else {
		$("#cfNextBtn").html("Next")
	}
}

function tab_handler(tab) {
	for (var i = 1; i <= 4; i++) {
		$('#cf-' + i).removeClass('active')
		$('#cf-' + i).removeClass('show')
	}
	$('#cf-' + tab).addClass('active')
	$('#cf-' + tab).addClass('show')
	if (tab < 4) {
		$("#cfNextBtn").html("Next")
	}
	else {
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
	if (typeof (selected) == "string") {
		selected = JSON.parse(selected);
	}

	var dept_title = $('#dept_title').text();
	dept_title = dept_title.split(':');
	dept_title = dept_title[1];


	$("#fund").html(selected.fund);
	$("#deptid").html(selected.deptid);
	$("#program").html(selected.program);
	$("#class_code").html(selected.class_code);
	$("#project_grant").html(selected.project_grant);
	if (selected.short_code != '') {
		$('#cf_shortcode').html(selected.short_code);
	}
	else {
		$('#cf_shortcode_dr').html('')
		$('#cf_shortcode_dr').trigger('change')
	}
	$('#cf_nickname').html(selected.nickname);
	$('.cf_num').html(selected.account_number);
	$('#old_shortcode').html(selected.short_code);
	$('#old_chartfield').html(selected.account_number);
	$('#cf_users_table').DataTable().ajax.reload();
}


// Add selected rows to page 3
function load_3(table, cf_change_table) {
	cf_change_table.clear();

	table.rows().every(function (index, element) {
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
	cf_change_table.rows().every(function (index, element) {
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

	var current_cf = document.getElementsByClassName('current')[0].textContent
	cf_change_table.rows().every(function (index, element) {
		var row = $(this.node());
		var user_id = row.find('td:nth-child(2)').text()
		var building = row.find('td:nth-child(3)').text()
		var mrc = row.find('td:nth-child(4)').text()
		var toll = row.find('td:nth-child(5)').text()
		var local = row.find('td:nth-child(6)').text()
		var new_chartfield = $("#new_chartfield").html()

		review_table.row.add([
			user_id,
			building,
			mrc,
			toll,
			local
		]).draw();

		if (mrc == '') {
			mrc = current_cf;
		}
		else {
			mrc = new_chartfield
		}
		if (toll == '') {
			toll = current_cf;
		}
		else {
			toll = new_chartfield
		}
		if (local == '') {
			local = current_cf;
		}
		else {
			local = new_chartfield
		}

		// Information that should be the same for all phone numbers
		$('#num_rows').val(index)
		$('#old_dept_full_name_form').val($("#old_dept_full_name").html())
		$('#old_dept_mgr_form').val($("#old_dept_mgr").html())
		$('#old_chartfield_form').val($("#old_chartfield").html())
		$('#old_shortcode_form').val($("#old_shortcode").html())
		$('#user_full_name_form').val($("#user_full_name").html())
		$('#new_dept_full_name_form').val($("#new_dept_full_name").html())
		$('#new_dept_mgr_form').val($("#new_dept_mgr").html())
		$('#new_chartfield_form').val($("#new_chartfield").html())
		$('#new_shortcode_form').val($("#new_shortcode").html())
		// optional message input
		$('#new_dept_mgr_uniqname_form').val($("#new_dept_mgr_uniqname").text())
		$('#new_dept_mgr_email_form').val($("#new_dept_mgr_email").text())
		$('#old_dept_mgr_uniqname_form').val($("#old_dept_mgr_uniqname").text())

		// Rows for individual phone number (user_id)
		var user_id_form = document.createElement("input");
		user_id_form.type = "hidden";
		user_id_form.name = "user_id_form";
		user_id_form.value = user_id;
		document.getElementById('submit-form').appendChild(user_id_form);

		var building_form = document.createElement("input");
		building_form.type = "hidden";
		building_form.name = "building_form";
		building_form.value = building;
		document.getElementById('submit-form').appendChild(building_form);

		var mrc_form = document.createElement("input");
		mrc_form.type = "hidden";
		mrc_form.name = "mrc_form";
		mrc_form.value = mrc;
		document.getElementById('submit-form').appendChild(mrc_form);

		var toll_form = document.createElement("input");
		toll_form.type = "hidden";
		toll_form.name = "toll_form";
		toll_form.value = toll;
		document.getElementById('submit-form').appendChild(toll_form);

		var local_form = document.createElement("input");
		local_form.type = "hidden";
		local_form.name = "local_form";
		local_form.value = local;
		document.getElementById('submit-form').appendChild(local_form);

	})
	$("#review_table")[0].style.width = "100%";

}

function table_empty(table) {
	return !table.data().any();
}