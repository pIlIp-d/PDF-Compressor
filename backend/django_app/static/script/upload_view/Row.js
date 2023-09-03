class Row {
    constructor(file) {
        this._file_id = file === null ? "0" : file.file_id;
        this._file_name = file === null ? "Apply to All Files" : file.name;
        this.options = new Options(this._file_id, file === null);
        this._toggled_open = file === null;
    }

    initHtml() {
        let row = document.createElement("div")
        row.id = this._file_id;
        row.classList.add("file_row");

        let filename = document.createElement("span");
        filename.innerHTML = this._file_name;

        let select = document.createElement("select");
        select.id = "select_" + this._file_id;

        let more = document.createElement("span");
        more.textContent = "\\/";
        more.onclick = () => this.toggle_procession_options_visibility();
        let form = document.createElement("div")
        form.id = "form_" + this._file_id;

        row.appendChild(filename);
        row.appendChild(select);
        row.appendChild(more);
        row.appendChild(form);
        const parent_container = document.getElementById("file_list");
        parent_container.insertBefore(row, parent_container.firstChild);
        console.log(parent_container.children)
        this.options.initHtml();
        this.toggle_procession_options_visibility();
    }

    remove(){
        document.getElementById(this._file_id).remove();
    }

    toggle_procession_options_visibility() {
        this._toggled_open = !this._toggled_open;
        if (this._toggled_open) {
            this.options.hide_form();
        } else {
            this.options.show_form();
        }
    }
}