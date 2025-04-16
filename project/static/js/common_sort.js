
    var sortDirections = {}; // Object to keep track of sorting directions for each column

    function sortTable(tableId, n) {
        var table = document.getElementById(tableId);
        var rowsArray = Array.from(table.rows).slice(1); // Convert rows to array and exclude the header row

        // Determine the sorting direction for the column
        if (!sortDirections[tableId]) {
            sortDirections[tableId] = {};
        }
        if (!sortDirections[tableId][n]) {
            sortDirections[tableId][n] = "asc";
        } else {
            sortDirections[tableId][n] = sortDirections[tableId][n] === "asc" ? "desc" : "asc";
        }

        var dir = sortDirections[tableId][n];

        rowsArray.sort(function (a, b) {
            var x = a.getElementsByTagName("TD")[n].innerHTML.trim();
            var y = b.getElementsByTagName("TD")[n].innerHTML.trim();
        
            // Remove commas from the values
            var xClean = x.replace(/,/g, "");
            var yClean = y.replace(/,/g, "");
        
            // Check if the column contains dates
            if (isValidDate(xClean) && isValidDate(yClean)) {
                var xDate = new Date(xClean);
                var yDate = new Date(yClean);
                return dir === "asc" ? xDate - yDate : yDate - xDate;
            }
        
            // Check if x and y are numeric
            var xNum = parseFloat(xClean);
            var yNum = parseFloat(yClean);
        
            if (!isNaN(xNum) && !isNaN(yNum)) {
                return dir === "asc" ? xNum - yNum : yNum - xNum;
            }
        
            // Sort alphabetically
            if (dir === "asc") {
                return x.localeCompare(y);
            } else {
                return y.localeCompare(x);
            }
        });

        // Append sorted rows back to the table
        for (var i = 0; i < rowsArray.length; i++) {
            table.tBodies[0].appendChild(rowsArray[i]);
        }

        // Update the sorting icons
        updateSortingIcons(table, n, dir);
    }

    function updateSortingIcons(table, columnIndex, direction) {
        var headers = table.getElementsByTagName("th");
        for (var i = 0; i < headers.length; i++) {
            var sortIcon = headers[i].querySelector(".fa-sort");
            var upIcon = headers[i].querySelector(".fa-sort-up");
            var downIcon = headers[i].querySelector(".fa-sort-down");
            if (i === columnIndex) {
                sortIcon.style.display = "none";
                if (direction === "asc") {
                    upIcon.style.display = "inline";
                    downIcon.style.display = "none";
                } else {
                    upIcon.style.display = "none";
                    downIcon.style.display = "inline";
                }
            } else {
                sortIcon.style.display = "inline";
                upIcon.style.display = "none";
                downIcon.style.display = "none";
            }
        }
    }

    // Helper function to check if a string is a valid date
    function isValidDate(dateString) {
        var date = Date.parse(dateString);
        return !isNaN(date);
    }
