class Options {
    constructor(file_id, url_persistent = false) {
        this._file_id = file_id;
        this._url_persistent = url_persistent;
        this._select_container = null;
        this._form_container = null;
        this.update_options_request_parameter = "request_id=" + REQUEST_ID; // TODO -> file_id
        this.current_plugin = "null";
    }

    get_form_container() {
        if (this._form_container === null) {
            this._form_container = document.getElementById("form_" + this._file_id);
        }
        return this._form_container;
    }

    get_select_container() {
        if (this._select_container === null) {
            this._select_container = document.getElementById("select_" + this._file_id);
        }
        return this._select_container;
    }

    initHtml() {
        let _this = this;
        this.get_select_container().addEventListener("change", function () {
            let selected_option = this.value;
            if (_this._url_persistent) {
                save_plugin_in_url(selected_option);
            }
            PROCESSING_BUTTON.update();
            _this.update_allowed_input_file_types(selected_option);
            if (selected_option === "null"){
                _this.set_form_content("Choose something.");
                }
            else {
                // get form html for the newly selected plugin
                make_request(
                    "GET",
                    ROOT_DIR + "api/get_form_html_for_web_view/?plugin=" + selected_option.split(":")[0] + "&destination_file_type=" + selected_option.split(": ")[1],
                    true,
                    function () {
                        if (this.readyState === 4 && this.status === 200) {
                            _this.current_plugin = selected_option;
                            let json_response = JSON.parse(this.response);
                            if ("form_html" in json_response)
                                _this.set_form_content(json_response.form_html)
                            if ("form_script" in json_response)
                                _this.set_form_script(json_response.form_script)
                            _this.update_options();
                        }
                    }
                );
            }
        });
        // trigger onchange event after update_options finished (only needed the first time to load the form html)
        this.update_options(() => this.get_select_container().dispatchEvent(new Event('change')));
    }

    update_options(extra_response_handler = null) {
        console.log(this);
        // always deactivate button until its clear, that it can be pressed again
        PROCESSING_BUTTON.deactivate();
        let _this = this;
        make_request(
            "GET",
            ROOT_DIR + "api/get_possible_destination_file_types?" + this.update_options_request_parameter,
            true,
            function () {
                if (this.readyState === 4 && this.status === 200) {
                    let json_response = JSON.parse(this.response);
                    if ("possible_file_types" in json_response)
                        _this.add_options(json_response.possible_file_types);
                    if (_this.is_empty()) {
                        _this.set_form_content("No Processing option for the current combination of files found.");
                    }
                    PROCESSING_BUTTON.update();
                    if (extra_response_handler != null)
                        extra_response_handler();
                }
            }
        )
    }

    show_form() {
        this.get_form_container().style.display = "block";
    }

    hide_form() {
        this.get_form_container().style.display = "none";
    }

    clear() {
        this.get_select_container().innerHTML = "";
    }

    remove() {
        this.get_select_container().remove();
        this.get_form_container().remove();
    }

    is_empty() {
        // =empty if there are no options but the 'null' option
        return this.get_select_container().options.length <= 1;
    }

    add_options(possible_file_types) {
        this.clear();
        this.get_select_container().options.add(new Option("Choose a Result File Type", null));
        for (let i in possible_file_types)
            for (let file_ending_index in possible_file_types[i])
                this.get_select_container().options.add(new Option(i + ": " + possible_file_types[i][file_ending_index]));
        // set value if current plugin is a possible value
        for (let option of this.get_select_container().options)
            if (this.current_plugin === option.value)
                this.get_select_container().value = this.current_plugin;
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

    set_form_content(form_html_string) {
        this.get_form_container().innerHTML = form_html_string;
    }

    set_form_script(script_string) {
        let script = document.createElement("script");
        script.innerHTML = script_string;
        this.get_form_container().appendChild(script);
        // call predefined function that comes with form_script
        initialize_form();
    }
}