let compress_button = document.getElementById("compress_button");
let csrfmiddlewaretoken = document.getElementsByName("csrfmiddlewaretoken")[0].value;

let dz = null;
Dropzone.queueFinished = false;
Dropzone.options.maxFiles = 100;
Dropzone.options.myDropzone = {
    // Prevents Dropzone from uploading dropped files immediately
    autoProcessQueue: true,
    init: function () {
        dz = this;
        let _this = this;
        this.on("addedfile", function (file) {
            if (!correct_file_ending(file.name)) {
                this.removeFile(file);
                showUnsupportedFileAnimation();
                return;
            }
            Dropzone.queueFinished = false;
            file.file_id = null;
            let removeButton = Dropzone.createElement("<button class='remove-button'>Remove file</button>");
            removeButton.addEventListener("click", function (e) {
                // Make sure the button click doesn't submit the form:
                e.preventDefault();
                e.stopPropagation();
                // Remove the file preview.
                _this.removeFile(file);

            });
            file.previewElement.appendChild(removeButton);
        });
        this.on("removedfile", function (file) {
            if (file.file_id != null) {
                let queue_csrf_token = document.getElementsByName("csrfmiddlewaretoken")[0].value;
                let user_id = USER_ID;
                let removeFileRequest = new XMLHttpRequest();
                removeFileRequest.onreadystatechange = function () {
                };
                removeFileRequest.open(
                    "GET",
                    ROOT_DIR + "api/remove_file/?file_id=" + file.file_id + "&user_id=" + user_id + "&queue_csrf_token=" + queue_csrf_token + "&file_origin=uploaded",
                    true
                );
                removeFileRequest.send();
            }
            deactivate_compression_button();
        });
        this.on("queuecomplete", function () {
            Dropzone.queueFinished = true;
            if (_this.files.length !== 0) {
                update_file_type_select(
                    activate_compression_button
                );
            }
        });
        this.on("success", function (file, responseText) {
            file.file_id = responseText.file_id;
        });

    }
};
// TODO clean up
document.addEventListener("DOMContentLoaded", select_init);

let select = document.getElementById("destination_type_select");
let current_form = "null";

function set_form_content(form_html) {
    document.getElementById("form_content").innerHTML = form_html;
}

function set_form_script(script_string){
    let script = document.createElement("script");
    script.innerHTML = script_string;
    document.getElementById("form_content").appendChild(script);
    initialize_form_hierarchy();
}

function select_init() {
    update_file_type_select();
    select.addEventListener("change", function () {
        let selected_option = this.value;
        current_form = selected_option;
        if (selected_option === "null") {
            set_form_content("Choose something.");
            deactivate_compression_button();
            allowed_file_endings = [];
        } else {
            // changed to another processor
            make_request(
                "GET",
                ROOT_DIR + "api/get_form_html_for_web_view/?plugin=" + selected_option.split(":")[0] + "&destination_file_type=" + selected_option.split(": ")[1],
                true,
                function () {
                    if (this.readyState === 4 && this.status === 200) {
                        let json_response = JSON.parse(this.response);
                        if ("form_html" in json_response)
                            set_form_content(json_response.form_html)
                        if ("form_script" in json_response)
                            set_form_script(json_response.form_script)
                        if ("allowed_file_endings" in json_response)
                            allowed_file_endings = json_response.allowed_file_endings
                    }
                }
            );
        }
    });
    // run change event once for initialization
    select.dispatchEvent(new Event('change'));
}

function update_file_type_select(extra_execution = null) {
    // TODO keep selection if possible
    make_request(
        "GET",
        ROOT_DIR + "api/get_possible_destination_file_types?request_id=" + REQUEST_ID,
        true,
        function () {
            if (this.readyState === 4 && this.status === 200) {
                let json_response = JSON.parse(this.response);

                function add_options(options) {
                    for (let o in select.options)
                        select.options.remove(select.options[o]);
                    select.options.add(new Option("Choose a Result File Type", null));
                    // TODO allow 'display_name: processing', and have a separate value with the real plugin name
                    for (let i in options) {
                        for (let file_ending_index in options[i]) {
                            select.options.add(new Option(
                                i + ": " + options[i][file_ending_index]
                            ));
                        }
                    }
                    for (let i in select.options)
                        if (current_form === select.options[i].value)
                            select.value = current_form;
                }
                if ("possible_file_types" in json_response)
                    add_options(json_response.possible_file_types);
                if (Dropzone.queueFinished && select.value !== "null")
                    activate_compression_button();

                if (select.options.length <= 1) {
                    console.log("SHOW MESSAGE");
                    deactivate_compression_button();
                    set_form_content("No Processing option for the current combination of files found.");
                } else if (extra_execution instanceof Function)
                    extra_execution();

            }
        }
    )
}

function activate_compression_button() {
    compress_button.classList.remove("disabled");
    compress_button.classList.add("enabled");
    compress_button.disabled = false;
    compress_button.addEventListener("click", submit_compression_options_form);
}

function deactivate_compression_button() {
    compress_button.classList.remove("enabled");
    compress_button.classList.add("disabled");
    compress_button.disabled = true;
    compress_button.removeEventListener("click", submit_compression_options_form);
}

function submit_compression_options_form() {
    document.getElementById("compression_options_form").submit();
}

function correct_file_ending(filename) {
    if (allowed_file_endings.length === 0)
        return true
    for (let ending in allowed_file_endings) {
        if (ending != null && filename.endsWith(allowed_file_endings[ending])) {
            return true;
        }
    }
    return false;
}

// Animations
function showUnsupportedFileAnimation() {
    let dropzone = document.getElementById("my-dropzone");
    let wiggle_class = "wiggle";
    if (dropzone.classList.contains(wiggle_class))
        dropzone.classList.remove(wiggle_class);
    dropzone.classList.add(wiggle_class);
    setTimeout(function () {
        dropzone.classList.remove(wiggle_class);
    }, 1000); //At least the time the animation lasts
}