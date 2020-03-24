window.onscroll = function () { scrollFunction() };

$(document).ready(function() {
    // Select first options by default
    $("#dept_id").prop("selectedIndex", 0);
    $("#bill_period").prop("selectedIndex", 0);

    // Initially hide "current filters" div and remove filters button
    $("#filters-info").hide();
    $('#location-filter').hide();
    $('#type-filter').hide();
    $('#cf-filter').hide();
    $('#date-filter').hide();
    $('#filterremove').hide();

    // Apply filters on click
    $('#filterapply').on('click', function(e) {
        e.preventDefault();
        loc = $('#location').val();
        type = $('#type').val();
        cf = $('#cf').val();
        date = $('#date').val();

        var filters = [loc, type, cf, date];

        filter(filters, 'filter');

        $('#filters-info').show();
    });


    // Remove filters on click
    $('#filterremove').on('click', function(e) {
        e.preventDefault();
        remove_filters();

        // Hide "current filters" div
        $('#filters-info').hide();
    });
})

// Scroll to top funcctionality
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


// Allow user to download full report to CSV
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
                    row.push('\n');
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


// Create clickable download button
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


// Removes all filters
function remove_filters() {
    // Re-allow CSV downloads and show totals again
    $('.invLocTable tr.datarow').each(function() {
        current_cf = $(this).attr('id').split(':')[1];
        $('#total-row'.concat(current_cf)).show();
        $('#'.concat(current_cf)).show();
        $('#download-link').show();
        $(this).show();
    })

    // Clear and hide current filters and remove filters button
    $('#location-filter').html('');
    $('#location-filter').hide();
    $('#type-filter').html('');
    $('#type-filter').hide();
    $('#cf-filter').html('');
    $('#cf-filter').hide();
    $('#filterremove').hide();

    // Clear out filter option selected
    $("#location").prop("selectedIndex", 0);
    $("#type").prop("selectedIndex", 0);
    $("#cf").prop("selectedIndex", 0);
    $("#date").prop("selectedIndex", 0);
}


// Filter data in tables
function filter(filters, action) {
    let location = filters[0], type = filters[1], cf = filters[2], date = filters[3];
    $('#filterremove').show();

    
    // Filter by chartfield, if specified
    if (cf) {
        $('.chartfield-title').each(function() {
            current_cf = $(this).html().split('Chartfield: ')[1].trim();
            if (current_cf != cf) {
                id = '#'.concat(current_cf);
                $(id).hide();
                html = '<strong>Chartfield: </strong>'.concat(cf).concat('<br>');
                $('#cf-filter').html(html);
                $('#cf-filter').show();
            }
        })
    }

    // Additional filters
    $('.invLocTable tr.datarow').each(function() {
        current_cf = $(this).attr('id').split(':')[1];

        // Remove totals and ability to download
        $('#total-row'.concat(current_cf)).hide();
        $('#download-link').hide();

        // Get current location from table
        current_loc = $(this).find('.location').html();
        current_loc = current_loc.split('<br>')[0];
        current_loc = current_loc.split('Location: ')[1];

        // Filter by location, if specified
        if (location && current_loc != location) {
            $(this).hide();
            html = '<strong>Location: </strong>'.concat(location).concat('<br>');
            $('#location-filter').html(html);
            $('#location-filter').show();
        }

        // Filter by type, if specified
        if (type && $(this).find('.type').html() != type) {
            $(this).hide();
            html = '<strong>User ID Type: </strong>'.concat(type).concat('<br>');
            $('#type-filter').html(html);
            $('#type-filter').show();
        }

        // Filter by last call date, if specified
        if (date) {
            filter_match = ((date = '6-12' && $(this).find('.lt12').html() && $(this).find('.gt6').html()) ||
                (date = '12+' && !$(this).find('.lt12').html()) || $(this).find('.date').html() == 'None')

            if (filter_match == false) {
                $(this).hide();
                html = '<strong>Last Call Date: </strong>'.concat(date).concat('<br>');
                $('#date-filter').html(html);
                $('#date-filter').show();
            }
        }


        if (table_empty(current_cf)) {
            $('#'.concat(current_cf)).hide();
        }
        else {
            $('#'.concat(current_cf)).show();
        }
    })
}

function table_empty(cf) {
    var response = true;
    $('#invLocTable'.concat(cf).concat(' tr.datarow')).each(function() {
        if ($(this).is(':visible')) {
            response = false;
        }
    })
    return response;
}
