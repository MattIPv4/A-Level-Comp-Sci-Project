(() => {

    // Globals for table sorting
    let counter = 0;
    let table_data = [];

    const apply_icons = (id, active) => {
        // Get relevant elms
        const table = document.getElementById(id);
        const headers = document.querySelectorAll("table#" + id + " > thead > tr > th");

        // Iterate over headers
        let header_counter = 0;
        headers.forEach((header) => {
            // Skip unsortable
            if (!table_data[id][header_counter][0]) return;

            // Remove any old icons (save text) (use toString to remove warnings about self-assignment)
            header.textContent = header.textContent.toString();

            // Create base icon
            let icon = document.createElement("i");
            icon.classList.add("fas");
            icon.classList.add("ml-2");

            // Apply correct type
            if (header_counter.toString() === active.toString()) {
                // Check reversed state
                const reverse = table.getAttribute("data-sort-reverse");
                if (reverse.toString() === "0") {
                    icon.classList.add("fa-sort-up");
                } else {
                    icon.classList.add("fa-sort-down");
                }
            } else {
                icon.classList.add("fa-sort");
            }

            // Save icon to header
            header.appendChild(icon);

            // Increment counter
            header_counter++;
        });
    };

    const process_table = (elm) => {
        // Get and give table unique id
        const id = "table-" + counter.toString();
        elm.setAttribute("id", id);
        counter++;

        // Set other attrs
        elm.setAttribute("data-sort-last", "");
        elm.setAttribute("data-sort-reverse", "0");

        // Get sortable headers
        let sortable = [];
        let header_counter = 0;
        const headers = document.querySelectorAll("table#" + id + " > thead > tr > th");
        headers.forEach((header) => {
            // Set header id
            const header_id = id + "-h-" + header_counter.toString();
            header.setAttribute("id", header_id);
            header_counter++;
            // Save blank data (false immediately if no header text)
            sortable.push([!!header.textContent.trim().length, header_id, []]); // sortable, id, elements sort data
        });

        // Iterate over each row
        let row_counter = 0;
        const rows = document.querySelectorAll("table#" + id + " > tbody > tr");
        rows.forEach((row) => {
            // Set row id
            const row_id = id + "-" + row_counter.toString();
            row.setAttribute("id", row_id);
            row_counter++;

            // Iterate over each child
            let column_counter = 0;
            Array.from(row.children).forEach((child) => {
                // Set row/column id
                const column_id = row_id + "-" + column_counter.toString();
                child.setAttribute("id", column_id);

                // Add sort data or null
                sortable[column_counter][2].push([child.getAttribute("data-sort"), row_id]); // data, id
                // Disable sort for column if doesn't have sort data
                if (!child.hasAttribute("data-sort")) sortable[column_counter][0] = false;

                // Increment column counter
                column_counter++;
            });
        });

        // Iterate over sortable
        sortable.forEach((column) => {
            // Skip unsortable
            if (!column[0]) return;

            // Get the header elm
            const header = document.getElementById(column[1]);
            if (!header) return;

            // Get index
            const header_id = header.getAttribute("id").split("-");
            const index = parseInt(header_id[header_id.length - 1]);

            // Set click event
            header.onclick = (event) => {
                event.preventDefault();
                sort_table(id, index);
            };

            // Set style
            header.style.cursor = "pointer";
            header.style.userSelect = "none";
        });

        // Save data
        table_data[id] = sortable;

        // Do icons
        apply_icons(id, "");

        // Return id
        return id;
    };

    const sort = (a, b) => {
        if (a[0] === b[0]) return 0;
        return (a[0] < b[0]) ? -1 : 1;
    };

    const sort_table = (id, column) => {
        // Check given column and id
        if (id === undefined || column === undefined || id === null || column === null) return; // null/undefined check
        if (typeof id !== "string" || (typeof column != "string" && typeof column != "number")) return; // type check
        if (!id.trim().length || !column.toString().trim().length) return; // empty check

        // Check table exists in data
        if (!id in table_data) return;

        // Check table exists in DOM
        const table = document.getElementById(id);
        if (!table) return;

        // Get data
        let data = table_data[id];

        // Check can sort by column
        if (column >= data.length) return;
        if (!data[column][0]) return;

        // Get column data and sort
        data = data[column][2];
        data.sort(sort);

        // Set relevant table attrs and reverse if needed
        if (table.getAttribute("data-sort-last") === column.toString()) {
            // Currently sorted by this column already, check direction
            if (table.getAttribute("data-sort-reverse") === "0") {
                // Previous sort was normal, so reverse
                data.reverse();
                table.setAttribute("data-sort-reverse", "1");
            } else {
                // Previous sort was reverse, so normal
                table.setAttribute("data-sort-reverse", "0");
            }
        } else {
            // New column to sort by
            table.setAttribute("data-sort-last", column.toString());
            table.setAttribute("data-sort-reverse", "0");
        }

        // Do icons
        apply_icons(id, column);

        // Fetch rows in correct order
        let new_rows = [];
        data.forEach((item) => {
            // Get existing row by id and save
            new_rows.push(document.getElementById(item[1]));
        });

        // Get the table body and wipe all elements inside
        const tbody = document.querySelector("table#" + id + " > tbody");
        while (tbody.firstChild) tbody.removeChild(tbody.firstChild);

        // Append new sorted rows back to table
        new_rows.forEach((row) => {
            tbody.appendChild(row);
        });
    };

    // Initialise sorting
    const tables = document.querySelectorAll("table");
    tables.forEach((table) => {
        const id = process_table(table);
        // Attempt initial sort
        sort_table(id, document.getElementById(id).getAttribute("data-sort-initial"));
    });

})();