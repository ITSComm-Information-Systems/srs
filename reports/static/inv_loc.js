window.onscroll = function () { scrollFunction() };

$(document).ready(function() {
	// Select first options by default
    $("#dept_id").prop("selectedIndex", 0);
    $("#bill_period").prop("selectedIndex", 0);

    $('#filterapply').on('click', function(e) {
    	e.preventDefault();
    	test1 = $('#location').val();
    	test2 = $('#type').val();
    	test3 = $('#cf').val();

    	var filters = [test1, test2, test3];

    	filter(filters, 'filter');
    });


    $('#filterremove').on('click', function(e) {
    	e.preventDefault();
    	test1 = $('#location').val();
    	test2 = $('#type').val();
    	test3 = $('#cf').val();

    	var filters = [test1, test2, test3];

    	filter(filters, 'remvove');
    });
})

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

function exportTableToCSV(filename) {
    var csv = [];
    var rows = document.querySelectorAll("table tr");

    for (var i = 0; i < rows.length; i++) {
        var row = [], cols = rows[i].querySelectorAll("td, th");
        var name = rows[i].getAttribute('data-name');

        for (var j = 0; j < cols.length; ++j) {
            var text = cols[j].innerText;

            // New chartfield
            if (text == 'User ID') {
                if (i != 0) {
                    row.push('\n'); // does this work on mac?
                    csv.push(row);
                    row = [];
                }
                row.push(name);
                csv.push(row);
                row = [];
            }
            text = '"' + text + '"';
            row.push(text);
        }

        csv.push(row.join(","));
    }

    // Download CSV file
    downloadCSV(csv.join("\n"), filename);
}

function downloadCSV(csv, filename) {
    var csvFile;
    var downloadLink;

    // CSV file
    csvFile = new Blob([csv], { type: "text/csv" });

    // Download link
    downloadLink = document.createElement("a");

    // File name
    downloadLink.download = filename;

    // Create a link to the file
    downloadLink.href = window.URL.createObjectURL(csvFile);

    // Hide download link
    downloadLink.style.display = "none";

    // Add the link to DOM
    document.body.appendChild(downloadLink);

    // Click download link
    downloadLink.click();
}

function filter(filters, action) {
	let location = filters[0], type = filters[1], cf = filters[2];

	$('.invLocTable tr.datarow').each(function() {
		current_loc = $(this).find('.location').html();
		current_loc = current_loc.split('<br>')[0];
		current_loc = current_loc.split('Location: ')[1];
		if (location && current_loc != location) {
			if (action == 'filter') {
				$(this).hide();
			}
			else {
				$(this).show();
			}
		}

		if (type && $(this).find('.type').html() != type) {
			if (action == 'filter') {
				$(this).hide();
			}
			else {
				$(this).show();
			}
		}
    })

    if (cf) {
    	$('.chartfield-title').each(function() {
    		current_cf = $(this).html().split('Chartfield: ')[1].trim();
    		if (current_cf != cf) {
    			id = '#'.concat(current_cf);
    			if (action == 'filter') {
    				$(id).hide();
    			}
    			else {
    				$(id).show();
    			}
    		}
	    })
    }
}