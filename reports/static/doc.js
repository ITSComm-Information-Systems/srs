$(document).ready(function() {

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

	$('#doc_bill_date').on('change', function() {
		var sel = document.getElementById("doc_bill_date");
		var selected = sel.options[sel.selectedIndex].value;

		$('#billing_label').html(selected);
	})
})