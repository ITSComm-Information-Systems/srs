$(document).ready(function() {

	// Select first options by default
	$("#doc_depts").prop("selectedIndex", 0);
	$("#doc_bill_date").prop("selectedIndex", 0);

	
	// Change chartfields with department
	$('#doc_depts').on('change', function() {
		var sel = document.getElementById("doc_depts");
		var selected = sel.options[sel.selectedIndex].value;

		$.ajax({
			url: '/reports/doc/select-cf/',
			data: {
				'select_dept':selected
			},
			dataType:'json',
			// Reset chartfield options when department changes
			success: function(data) {
				test = data;
				$('#doc_chartcom').empty();
				for (i = 0; i < data.length - 1; ++i) {
					var drp = document.getElementById('doc_chartcom');
					var option = document.createElement("OPTION");
					option.value = data[i].account_number;
					option.text = data[i].account_number;
					drp.add(option);
				}
				$('#dept_name').html(data[data.length - 1].name);
			}
		})
	})

	
	// Change date label
	$('#doc_bill_date').on('change', function() {
		var sel = document.getElementById("doc_bill_date");
		var selected = sel.options[sel.selectedIndex].value;

		$('#billing_label').html(selected);
	})

	
	// List selected chartfields
	$('#doc_chartcom').on('change', function() {
		var selected = $('#doc_chartcom').val();
		var text = '';
		for (i = 0; i < selected.length; ++i) {
			text += '<strong>&nbsp;&nbsp;' + selected[i] + '</strong><br>'
		}
		$('#chartfield_list').html(text);
	})

	
	// Send data to report page
	$('.detail_link').on('click', function(e) {
		e.preventDefault();

		var selected = $('#selected_dept').text();
		var bill_date = $('#billing_date').text();
		// var chartcoms = $('#chartcoms').val();

		data = {
				selected_dept: 'test',
				billing_date: 'test',
				chartcoms: 'test'
			};
		$.post('/reports/doc/report/detail/', data);

		// $.ajax({
		// 	url: '/reports/doc/report/detail/',
		// 	data: {
		// 		'selected_dept': selected,
		// 		'billing_date': bill_date,
		// 		'chartcoms': chartcoms
		// 	},
		// 	dataType: 'json',
		// 	success: function(data) {
		// 		alert('success');
		// 	},
		// 	error: function(data) {
		// 		alert('error');
		// 	}
		// })
	})


	// Validate form
	$('#generate').on('click', function(e) {
		var chartfields = $('#doc_chartcom').val();
		if (chartfields == null) {
			e.preventDefault();
			$('#error_message').removeClass('hidden');
		}
	})
})