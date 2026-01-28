function sortTable(tableId, n, isNumeric = false) {
    var table, rows, switching, i, x, y, shouldSwitch, dir, switchcount = 0;
    table = document.getElementById(tableId);
    switching = true;
    dir = "asc";
    while (switching) {
        switching = false;
        rows = table.rows;
        for (i = 1; i < (rows.length - 1); i++) {
            shouldSwitch = false;
            x = rows[i].getElementsByTagName("TD")[n];
            y = rows[i + 1].getElementsByTagName("TD")[n];

            let xVal = x.textContent || x.innerText;
            let yVal = y.textContent || y.innerText;

            if (isNumeric) {
                // Clean currency or other symbols if needed, here assuming clean numbers or simple text
                xVal = parseFloat(xVal.replace(/[^0-9.-]+/g, "")) || 0;
                yVal = parseFloat(yVal.replace(/[^0-9.-]+/g, "")) || 0;
            } else {
                xVal = xVal.toLowerCase();
                yVal = yVal.toLowerCase();
            }

            if (dir == "asc") {
                if (xVal > yVal) {
                    shouldSwitch = true;
                    break;
                }
            } else if (dir == "desc") {
                if (xVal < yVal) {
                    shouldSwitch = true;
                    break;
                }
            }
        }
        if (shouldSwitch) {
            rows[i].parentNode.insertBefore(rows[i + 1], rows[i]);
            switching = true;
            switchcount++;
        } else {
            if (switchcount == 0 && dir == "asc") {
                dir = "desc";
                switching = true;
            }
        }
    }
}
