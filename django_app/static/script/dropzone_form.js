let SELECT;
let PROCESSING_BUTTON;
document.addEventListener("DOMContentLoaded", function () {
    SELECT = new DestinationTypeSelect("destination_type_select");
    PROCESSING_BUTTON = new ProcessingButton("process_button", SELECT, Dropzone);
    SELECT.init();
});

class DestinationTypeSelect {
    constructor(select_id) {
        this.select_object = document.getElementById(select_id);
    }

    init() {
        let _this = this;
        // trigger onchange event after update_options finished (only needed the first time to load the form html)
        this.update_options(()=>this.select_object.dispatchEvent(new Event('change')));
        this.select_object.addEventListener("change", function () {
            let selected_option = this.value;
            save_plugin_in_url(selected_option);
            PROCESSING_BUTTON.update();
            _this.update_allowed_input_file_types(selected_option);
            if (selected_option === "null")
                set_form_content("Choose something.");
            else {
                // get form html for the newly selected plugin
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
                            _this.update_options();
                        }
                    }
                );
            }
        });
    }

    update_options(extra_response_handler = null) {
        // always deactivate button until its clear, that it can be pressed again
        PROCESSING_BUTTON.deactivate();
        let _this = this;
        make_request(
            "GET",
            ROOT_DIR + "api/get_possible_destination_file_types?request_id=" + REQUEST_ID,
            true,
            function () {
                if (this.readyState === 4 && this.status === 200) {
                    let json_response = JSON.parse(this.response);
                    if ("possible_file_types" in json_response)
                        _this.add_options(json_response.possible_file_types);
                    if (_this.is_empty()) {
                        set_form_content("No Processing option for the current combination of files found.");
                    }
                    PROCESSING_BUTTON.update();
                    if (extra_response_handler != null)
                        extra_response_handler();
                }
            }
        )
    }

    clear() {
        for (let o in this.select_object.options)
            this.select_object.options.remove(this.select_object.options[o]);
    }

    add_options(possible_file_types) {
        this.clear();
        this.select_object.options.add(new Option("Choose a Result File Type", null));
        for (let i in possible_file_types)
            for (let file_ending_index in possible_file_types[i])
                this.select_object.options.add(new Option(i + ": " + possible_file_types[i][file_ending_index]));
        // set value if current plugin is a possible value
        for (let i in this.select_object.options)
            if (current_plugin === this.select_object.options[i].value)
                this.select_object.value = current_plugin;
    }

    is_empty() {
        // =empty if there are no options but the 'null' option
        return this.select_object.options.length <= 1;
    }

    update_allowed_input_file_types(selected_option) {
        make_request(
            "GET",
            ROOT_DIR + "api/get_allowed_input_file_types/?plugin_info=" + selected_option, true,
            function () {
                if (this.readyState === 4 && this.status === 200) {
                    let json_response = JSON.parse(this.response);
                    if ("allowed_file_types" in json_response)
                        allowed_file_endings = json_response.allowed_file_types
                }
            }
        )
    }
}

class ProcessingButton {
    constructor(button_id, select, dropzone) {
        this.process_button = document.getElementById(button_id);
        this.select = select;
        this.dropzone = dropzone;
    }

    update() {
        if (!this.select.is_empty() && this.select.select_object.value !== "null" && this.dropzone.queueFinished && dropzone_files.length > 0)
            this.activate();
        else
            this.deactivate();
    }

    activate() {
        this.process_button.classList.remove("disabled");
        this.process_button.classList.add("enabled");
        this.process_button.disabled = false;
        this.process_button.addEventListener("click", this.submit);
    }

    deactivate() {
        this.process_button.classList.remove("enabled");
        this.process_button.classList.add("disabled");
        this.process_button.disabled = true;
        this.process_button.removeEventListener("click", this.submit);
    }

    submit() {
        document.getElementById("compression_options_form").submit();
    }
}

Dropzone.queueFinished = false;
Dropzone.options.maxFiles = 100;
let dropzone_files;
Dropzone.options.myDropzone = {
    autoProcessQueue: true,
    init: function () {
        dropzone_files = this.files;
        let _this = this;
        this.on("addedfile", function (file) {
            if (!correct_file_type(file)) {
                this.removeFile(file);
                showUnsupportedFileAnimation();
            } else {
                function get_remove_button(file) {
                    let removeButton = Dropzone.createElement("<button class='remove-button'>Remove file</button>");
                    removeButton.addEventListener("click", function (e) {
                        // Make sure the button click doesn't submit the form
                        e.preventDefault();
                        e.stopPropagation();
                        // Remove the file preview
                        _this.removeFile(file);
                    });
                    return removeButton;
                }
                // TODO add default thumbnail for pdfs etc (use line below)
                //dz.emit("thumbnail", file, "http://path/to/image");
                Dropzone.queueFinished = false;
                file.file_id = null;
                file.previewElement.appendChild(get_remove_button(file));
            }
        });
        this.on("removedfile", function (file) {
            if (_this.files.length === 0)
                Dropzone.queueFinished = false;
            if (file.file_id != null) {
                let queue_csrf_token = document.getElementsByName("csrfmiddlewaretoken")[0].value;
                // TODO if request is already finished, get a new request_id
                make_request(
                    "GET",
                    `${ROOT_DIR}api/remove_file/?file_id=${file.file_id}&user_id=${USER_ID}&queue_csrf_token=${queue_csrf_token}&file_origin=uploaded`,
                    true,
                    function () {
                        if (this.readyState === 4 && this.status === 200) {
                            SELECT.update_options();
                        }
                    }
                );
            }
        });
        this.on("queuecomplete", function () {
            if (_this.files.length !== 0) {
                Dropzone.queueFinished = true;
                SELECT.update_options();
            }
        });
        this.on("success", function (file, responseText) {
            if ("file_id" in responseText)
                file.file_id = responseText.file_id;
        });
    }
};

function set_form_content(form_html_string) {
    document.getElementById("form_content").innerHTML = form_html_string;
}

function set_form_script(script_string) {
    let script = document.createElement("script");
    script.innerHTML = script_string;
    document.getElementById("form_content").appendChild(script);
    // call predefined function that comes with form_script
    initialize_form();
}

function correct_file_type(file) {
    if (allowed_file_endings.length === 0)
        return true;
    for (const ending of allowed_file_endings) {
        console.log(ending);
        if (ending === "*")
            return true;
        else if (file.type === ending)
            return true;
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