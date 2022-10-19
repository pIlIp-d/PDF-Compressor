class DestinationTypeSelect {
    constructor() {
        this.select_object = document.getElementById("destination_type_select");

    }

    init() {
        let _this = this;

        this.update_options(false);
        this.select_object.addEventListener("change", function () {

            let selected_option = this.value;
            save_plugin_in_url(selected_option);
            updateProcessedButton()

            make_request(
                "GET",
                ROOT_DIR + "api/get_allowed_input_file_types/?plugin_info=" + selected_option, true,
                function () {
                    if (this.readyState === 4 && this.status === 200) {
                        let json_response = JSON.parse(this.response);
                        if ("allowed_file_endings" in json_response)
                            allowed_file_endings = json_response.allowed_file_endings
                    }
                }
            )

            // TODO 555 add separate request for get allowed_file_endings, that is call every update of select
            if (selected_option === "null") {
                set_form_content("Choose something.");
                deactivate_compression_button();
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
                            _this.update_options();
                        }
                    }
                );
            }
        });
        // run change event once for initialization
        this.select_object.dispatchEvent(new Event('change'));
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
        return this.select_object.options.length <= 1;
    }

    update_options(async = true) {
        // always deactivate button until its clear, that it can be pressed again
        deactivate_compression_button();
        let _this = this;
        make_request(
            "GET",
            ROOT_DIR + "api/get_possible_destination_file_types?request_id=" + REQUEST_ID,
            async,
            function () {
                if (this.readyState === 4 && this.status === 200) {
                    let json_response = JSON.parse(this.response);
                    if ("possible_file_types" in json_response)
                        _this.add_options(json_response.possible_file_types);
                    updateProcessedButton();
                    if (_this.is_empty()) {
                        set_form_content("No Processing option for the current combination of files found.");
                    }
                }
            }
        )
    }
}

let compress_button = document.getElementById("compress_button");
let csrfmiddlewaretoken = document.getElementsByName("csrfmiddlewaretoken")[0].value;
let SELECT = new DestinationTypeSelect();
document.addEventListener("DOMContentLoaded", function () {
    SELECT.init();
});

let dz = null;
Dropzone.queueFinished = false;
Dropzone.options.maxFiles = 100;
Dropzone.options.myDropzone = {
    autoProcessQueue: true,
    init: function () {
        dz = this;
        let _this = this;
        this.on("addedfile", function (file) {
            if (!correct_file_type(file)) {
                this.removeFile(file);
                showUnsupportedFileAnimation();
                if (Dropzone.options.FileList <= 0) // TODO redundant?
                    deactivate_compression_button();
                return;
            }
            // TODO add default thumbnail for pdfs etc (use line below)
            //dz.emit("thumbnail", file, "http://path/to/image");
            Dropzone.queueFinished = false;
            file.file_id = null;
            let removeButton = Dropzone.createElement("<button class='remove-button'>Remove file</button>");
            removeButton.addEventListener("click", function (e) {
                // Make sure the button click doesn't submit the form
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
                make_request(
                    "GET",
                    `${ROOT_DIR}api/remove_file/?file_id=${file.file_id}&user_id=${USER_ID}&queue_csrf_token=${queue_csrf_token}&file_origin=uploaded`
                );
            }
            SELECT.update_options();
            if (_this.files.length === 0)
                Dropzone.queueFinished = false;
        });
        this.on("queuecomplete", function () {
            Dropzone.queueFinished = true;
            if (_this.files.length !== 0)
                SELECT.update_options();
        });
        this.on("success", function (file, responseText) {
            if ("file_id" in responseText)
                file.file_id = responseText.file_id;
        });
    }
};

function set_form_content(form_html) {
    document.getElementById("form_content").innerHTML = form_html;
}

function set_form_script(script_string) {
    let script = document.createElement("script");
    script.innerHTML = script_string;
    document.getElementById("form_content").appendChild(script);
    initialize_form_hierarchy();
}

function save_plugin_in_url(plugin_name) {
    current_plugin = plugin_name;
    let new_url = location.href.split("?")[0]
    let parameters;
    if (location.href.split("?").length > 1)
        parameters = location.href.split("?")[1].split("&")
    else
        parameters = ["plugin="]
    for (let p in parameters) {
        if (Number(p) === 0) {
            new_url += "?";
        } else if (Number(p) < parameters.length - 1) {
            new_url += "&";
        }
        if (parameters[p].startsWith("plugin"))
            new_url += "plugin=" + plugin_name
        else
            new_url += parameters[p];
    }
    window.history.pushState(null, "", new_url);
}


function updateProcessedButton() {
    if (!SELECT.is_empty() && Dropzone.queueFinished && SELECT.select_object.value !== "null")
        activate_compression_button();
    else {
        deactivate_compression_button();
    }
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

function correct_file_type(file) {
    if (allowed_file_endings.length === 0)
        return true
    for (const ending in allowed_file_endings) {
        if (file.type === ending) {
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