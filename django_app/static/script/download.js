//TODO completely redesign

let ACTIVE_CHECKBOXES = []; //holds requestId -> fileIDs
let request_list = [];


function download(link, filename) {
    // Create a new link for download
    const anchor = document.createElement('a');
    anchor.href = ROOT_DIR + link;
    anchor.setAttribute("download", filename);
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

// TODO add progress of request (loading circle etc.)
MAIN_INTERVAL_TICK = 2000
let main_interval_obj;
let queue_csrf_token = document.getElementsByName("csrfmiddlewaretoken")[0].value;
let file_list = [];
let current_sorting = "request";
document.addEventListener("DOMContentLoaded", init);

function init() {
    document.getElementById("delete-all-button").addEventListener("click", (_)=>{
        for (let i in request_list){
            for (let file of request_list[i].files){
                deleteFile(file.file_id, file.file_origin);
            }
        }
    });
    document.getElementById("download-selected-button").addEventListener("click", (_)=>{
        for (let i in request_list) {
            let request = request_list[i];
            if (parseInt(request.request_id) in ACTIVE_CHECKBOXES) {
                for (let file_id of ACTIVE_CHECKBOXES[request.request_id]) {
                    for (let file of request_list[i].files){
                        if (file.file_id === file_id){
                            download(file.filename_path, file.filename);
                        }
                    }
                }
            }
        }
    });
    document.getElementById("delete-selected-button").addEventListener("click", (_)=>{
        for (let i in request_list) {
            let request = request_list[i];
            if (parseInt(request.request_id) in ACTIVE_CHECKBOXES) {
                for (let file_id of ACTIVE_CHECKBOXES[request.request_id]) {
                    for (let file of request_list[i].files){
                        if (file.file_id === file_id){
                            deleteFile(file.file_id, file.file_origin);
                        }
                    }
                }
            }
        }
    });

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

                let newRequest_list = [];
                for (let file of new_file_list) {
                    if (typeof newRequest_list[file.request_id] === "undefined") {
                        newRequest_list[file.request_id] = {request_id: file.request_id, files: [], datetime: ""};
                        newRequest_list[file.request_id].datetime = file.date_of_upload;
                    }
                    newRequest_list[file.request_id].files.push(file);
                }
                newRequest_list = newRequest_list.sort((a,b)=>a.request_id < b.request_id ? 1 : -1);
                if (JSON.stringify(request_list) !== JSON.stringify(newRequest_list)) {
                    request_list = newRequest_list;
                    update_html();
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

function changeSelectOnFile(request_id, fileId, newValue){
    if (typeof ACTIVE_CHECKBOXES[request_id] === "undefined"){
        ACTIVE_CHECKBOXES[request_id] = [];
    }
    if (newValue)
        ACTIVE_CHECKBOXES[request_id].push(fileId);
    else if (fileId in ACTIVE_CHECKBOXES[request_id].values)
        ACTIVE_CHECKBOXES[request_id].remove(fileId);

}

function getRow(file){
    let fileRow = document.createElement("div");
    fileRow.classList.add("file-row");
    fileRow.appendChild(getSpan(file.filename));
    fileRow.appendChild(getSpan(file.size));

    let button = document.createElement("button");
    button.classList.add("material-element", "material-button", "small-material-button");
    if (!file.finished) {
        button.disabled = true;
    } else {
        button.onclick = () => download(file.filename_path, file.filename);
    }
    button.appendChild(document.createTextNode("Download"));
    fileRow.appendChild(button);

    let checkbox = document.createElement("input");
    checkbox.setAttribute("type", "checkbox");
    checkbox.onchange = (_) => changeSelectOnFile(file.request_id, file.file_id, checkbox.checked);
    checkbox.classList.add("checkbox");
    checkbox.id = file.file_id;
    checkbox.checked = (typeof ACTIVE_CHECKBOXES[file.request_id] !== "undefined" && file.file_id in ACTIVE_CHECKBOXES[file.request_id]);
    fileRow.appendChild(checkbox);
    return fileRow;
}

function selectAll(newValue, request_id){
    for (let i in request_list){
        if (typeof request_list[i] !== "undefined" && request_list[i].request_id === request_id) {
            for (let file of request_list[i].files) {
                document.getElementById(file.file_id).checked = newValue;
                changeSelectOnFile(request_id, file.file_id, newValue);
            }
        }
    }
}

function getSpan(textValue){
    let span = document.createElement("span");
    span.appendChild(document.createTextNode(textValue));
    return span;
}

function getContainerHeader(request){
    let header = document.createElement("div");
    header.classList.add("request_header");
    let title = getSpan("Files from "+request.datetime);
    let select_all = document.createElement("span");
    select_all.appendChild(document.createTextNode("All"));
    select_all.classList.add("select-all-container");
    let checkbox = document.createElement("input");
    checkbox.type = "checkbox";
    checkbox.onchange = () => selectAll(checkbox.checked, request.request_id);

    //TODO checkbox.checked = file.file_id in ACTIVE_CHECKBOXES[file.request_id];

    select_all.appendChild(checkbox);
    header.appendChild(title);
    header.appendChild(select_all);
    return header;
}

function getContainer(request){
    let container = document.createElement("div");
    container.classList.add("material-element");
    container.classList.add("request-container");
    container.appendChild(getContainerHeader(request));
    for (let file of request.files){
        container.appendChild(getRow(file));
    }
    return container;
}

function update_html() {
    let container = document.getElementById("content_container");
    let last_request_id = null;

    // remove all old children
    while (container.lastChild) {
        container.removeChild(container.lastChild);
    }
    if (file_list.length === 0){
        document.getElementById("content_container").innerHTML = "<div style='margin: auto; text-align: center;'>Nothing here, yet.</div>";
    }

    container.innerHTML = "";
    for (let request in request_list){
        container.appendChild(getContainer(request_list[request]));
    }
    //
    // for (const file of file_list) {
    //     if (file.request_id !== last_request_id) {
    //         let table = document.createElement("table")
    //         table.classList.add("request_files_container");
    //         table.id = file.request_id;
    //         table.appendChild(get_table_head());
    //         container.appendChild(table);
    //     }
    //     container.lastElementChild.appendChild(get_file_row(file));
    //     last_request_id = file.request_id;
    // }
}
