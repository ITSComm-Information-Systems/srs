
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
    
            // Handle numeric sorting, including prices with symbols or commas
            var xNum = parseFloat(x.replace(/[^0-9.-]+/g, '')); // Remove non-numeric characters
            var yNum = parseFloat(y.replace(/[^0-9.-]+/g, ''));
    
            if (!isNaN(xNum) && !isNaN(yNum)) {
                return dir === "asc" ? xNum - yNum : yNum - xNum;
            }
    
            // Sort alphabetically as a fallback
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
