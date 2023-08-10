class ProcessingButton {
    constructor(button_id, dropzone) {
        this.process_button = document.getElementById(button_id);
        this.dropzone = dropzone;
    }

    update() {
        let active = true;
        // active means not empty and not null for either (all || all without 0 || only 0) with 0 being the select for all
        for (const selectID in SELECTS) {
            // all without selects except the one for all files at once
            const select = SELECTS[selectID];
            if (select.options.is_empty() || select.options.get_select_container().value === "null")
                active = false;
        }
        if (!active){
            // apply to all select
            active = !SELECT.options.is_empty() && !(SELECT.options.get_select_container().value === "null");
        }
        if (active && this.dropzone.queueFinished  && Dropzone.options.myDropzone.files.length > 0)
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
        // TODO account for all selects
        document.getElementById("compression_options_form").submit();
    }
}
