

function download(link, filename) {
    // Create a new link for download
    const anchor = document.createElement('a');
    anchor.href = ROOT_DIR + link;
    anchor.download = filename;
    document.body.appendChild(anchor);
    // click link to download the file
    anchor.click();
    // remove link again
    document.body.removeChild(anchor);
}

function deleteFile(file_id, file_origin) {
    make_request("GET", ROOT_DIR + "api/remove_file?file_id=" + file_id + "&file_origin=" + file_origin, true,
        function () {
            if (this.readyState === 4 && this.status === 200) {
                update_files();
            }
        }
    );
}
console.log("Djapdjad")
// TODO add progress of request (loading circle etc.)
MAIN_INTERVAL_TICK = 2000
let main_interval_obj;
let queue_csrf_token = document.getElementsByName("csrfmiddlewaretoken")[0].value;
let file_list = [];
let current_sorting = "request";
document.addEventListener("DOMContentLoaded", init);

function init() {
    main_interval_obj = setInterval(main_interval, MAIN_INTERVAL_TICK)
}

update_files();

function main_interval() {
    update_files();
}

function update_files() {
    make_request(
        "GET",
        ROOT_DIR + "api/get_all_files/?csrfmiddlewaretoken="+queue_csrf_token,
        true,
        function () {
            if (this.readyState === 4 && this.status === 200) {
                let new_file_list = JSON.parse(this.response).files;
                if (file_list !== new_file_list) {
                    file_list = new_file_list
                    update_html(current_sorting);
                }
            }
        }
    );
}

function get_table_head() {
    let header = document.createElement("tr");
    let th_list = ["Filename", "date of upload", "Size", "Download", "Delete"];
    for (let col in th_list) {
        let column = document.createElement("th");
        column.appendChild(document.createTextNode(th_list[col]));
        header.appendChild(column);
    }
    return header;
}

function get_file_row(file) {
    function get_td(class_list, text_value) {
        let td = document.createElement("td");
        for (let currentClass of class_list)
            td.classList.add(currentClass);

        td.appendChild(document.createTextNode(text_value));
        return td;
    }

    function get_button_td(text, hard_disabled, extra_class, onclick_function) {
        let button = document.createElement("button");
        button.classList.add("button", extra_class);
        if (!file.finished) {
            button.classList.add("disabled");
            if (hard_disabled)
                button.disabled = true;
        } else {
            button.onclick = onclick_function;
        }
        button.appendChild(document.createTextNode(text));
        let td = document.createElement("td");
        td.appendChild(button);
        return td;
    }

    let file_row = document.createElement("tr");
    file_row.id = file.request_id;
    file_row.appendChild(get_td(["filename"], file.filename));
    file_row.appendChild(get_td(["date_of_upload"], file.date_of_upload));
    file_row.appendChild(get_td(["size"], file.size));
    file_row.appendChild(
        get_button_td("Download", true, "download_button", () => download(file.filename_path, file.filename))
    );
    file_row.appendChild(
        get_button_td("Delete", false, "delete_button", () => deleteFile(file.file_id, file.file_origin))
    );
    file_row.lastChild.id = file.file_id;
    return file_row;
}

function update_html(sort_by) {
    let container = document.getElementById("content_container");
    let last_request_id = null;

    // remove all old children
    while (container.lastChild) {
        container.removeChild(container.lastChild);
    }

    for (const file of file_list) {
        if (file.request_id !== last_request_id) {
            let table = document.createElement("table")
            table.classList.add("request_files_container");
            table.id = file.request_id;
            table.appendChild(get_table_head());
            container.appendChild(table);
        }
        container.lastElementChild.appendChild(get_file_row(file));
        last_request_id = file.request_id;
    }
}
