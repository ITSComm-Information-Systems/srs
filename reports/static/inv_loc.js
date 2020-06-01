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

    // Pre-register filter-able columns
    locCols = [];
    typeCols = [];
    cfCols =[];
    lt12Cols = [];
    gt6Cols = [];

    $('.invLocTable tr.datarow').each(function() {
        locCols.push($(this).find('.location'));
        typeCols.push($(this).find('.type'));
        cfCols.push($(this).find('.chartfield'));
        lt12Cols.push($(this).find('.lt12'));
        gt6Cols.push($(this).find('.gt6'));
    })


    // Apply filters on click
    $('#filterapply').on('click', function(e) {
            e.preventDefault();

            filter();

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
    $('#date-filter').html('');
    $('#date-filter').hide();
    $('#filterremove').hide();

    // Clear out filter option selected
    $("#location").prop("selectedIndex", 0);
    $("#type").prop("selectedIndex", 0);
    $("#cf").prop("selectedIndex", 0);
    $("#date").prop("selectedIndex", 0);
}

function filter() {
    $('#filterremove').show();

    var loc = $('#location').val(),
    type = $('#type').val(),
    cf = $('#cf').val(),
    date = $('#date').val();

    // Remove totals and ability to download
    affected_cfs = []
    $('#download-link').hide();

    //console.log(locCols);

    if (loc) {
        for (i = 0; i < locCols.length; i++) {
            // current_loc = locCols[i][0].innerText;
            current_loc = locCols[i][0].outerHTML;
            if (current_loc) {
                //console.log(current_loc)
                // current_loc = current_loc.split('Location: ')[1];
                // current_loc = current_loc.split('Floor: ')[0];
                // current_loc = current_loc.replace('\n', '');

                current_loc = current_loc.split('<br>')[0];
                current_loc = current_loc.split('Location: ')[1];

            }

            if (current_loc != loc) {
                locCols[i].parent().hide();
                affected_cfs.push(cfCols[i][0].innerText);
                html = '<strong>Location: </strong>'.concat(loc).concat('<br>');
                $('#location-filter').html(html);
                $('#location-filter').show();
            }
        }
    }

    if (type) {
        for (i = 0; i < typeCols.length; i++) {
            if (typeCols[i][0].innerText != type) {
                typeCols[i].parent().hide();
                affected_cfs.push(cfCols[i][0].innerText);
                html = '<strong>User ID Type: </strong>'.concat(type).concat('<br>');
                $('#type-filter').html(html);
                $('#type-filter').show();
            }
        }
    }

    if (cf) {
        for (i = 0; i < cfCols.length; i++) {
            if (cfCols[i][0].innerText != cf) {
                id = '#'.concat(cfCols[i][0].innerText);
                $(id).hide();            
                affected_cfs.push(cfCols[i][0].innerText);
                html = '<strong>Chartfield: </strong>'.concat(cf).concat('<br>');
                $('#cf-filter').html(html);
                $('#cf-filter').show();
            }
        }
    }

    if (date) {
        for (i = 0; i < gt6Cols.length; i++) {
            filter_match = ((date == '6-12' && lt12Cols[i][0].innerText == 1 && gt6Cols[i][0].innerText == 1) ||
                    (date == 'gt12' && lt12Cols[i][0].innerText == 0) || (date == 'lt6' && gt6Cols[i][0].innerText == 0))


            if (filter_match == false || (lt12Cols[i][0].innerText == 0 && gt6Cols[i][0].innerText == 0)) {
                gt6Cols[i].parent().hide();
                affected_cfs.push(cfCols[i][0].innerText);
                html = '<strong>Last Call Date: </strong>'.concat($('#'.concat(date)).html()).concat('<br>');
                $('#date-filter').html(html);
                $('#date-filter').show();
            }
        }
    }

    for (i = 0; i < affected_cfs.length; i++) {
        $('#total-row'.concat(affected_cfs[i])).hide();

        if (table_empty(affected_cfs[i])) {
            $('#'.concat(affected_cfs[i])).hide();
        }
        else {
            $('#'.concat(affected_cfs[i])).show();
        }
    }
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
