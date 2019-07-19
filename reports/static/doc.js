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
				$('#chartfield_list').html('');
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

	// Validate form
	$('#generate').on('click', function(e) {
		var chartfields = $('#doc_chartcom').val();
		if (chartfields == null) {
			e.preventDefault();
			$('#error_message').removeClass('hidden');
		}
	})

	$('#return_link').on('click', function(e) {
		e.preventDefault();
		$('#return').submit();
	})

	// Select all chartfields
	$('#select-all').on('click', function() {
		if ($('#select-all').is(':checked')) {
			$('#doc_chartcom option').prop('selected', 'selected');
		}
		else {
			$('#doc_chartcom option').prop('selected', '');
		}
	})
})

// When the user scrolls down 20px from the top of the document, show the button
window.onscroll = function() {scrollFunction()};

function scrollFunction() {
  if (document.body.scrollTop > 20 || document.documentElement.scrollTop > 20) {
    document.getElementById("scrollTop").style.display = "block";
  } else {
    document.getElementById("scrollTop").style.display = "none";
  }
}

// When the user clicks on the button, scroll to the top of the document
function topFunction() {
  document.body.scrollTop = 0;
  document.documentElement.scrollTop = 0;
}