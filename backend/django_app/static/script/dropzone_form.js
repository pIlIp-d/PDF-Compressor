let SELECT;
let PROCESSING_BUTTON;
let SELECTS = {};

// TODO!!! Class diagram and new logic implementing all sub-forms functionality

Dropzone.queueFinished = false;
Dropzone.options.maxFiles = 100;
let dropzone_files;

document.addEventListener("DOMContentLoaded", function () {
    SELECT = new AllFilesRow(current_plugin);
    console.log(SELECT);
    PROCESSING_BUTTON = new ProcessingButton("process_button", Dropzone);
    SELECT.initHtml();
});

Dropzone.options.myDropzone = {
    autoProcessQueue: true,
    files: [],
    init: function () {
        console.log("basj");
        dropzone_files = this.files;
        let _this = this;
        Dropzone.options.myDropzone.files = _this.files
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
                            SELECT.options.update_options();
                            SELECTS[file.file_id].remove();//.clear();
                        }
                    }
                );
            }
        });
        this.on("queuecomplete", function () {
            if (_this.files.length !== 0) {
                Dropzone.queueFinished = true;
                SELECT.options.update_options();
            }
        });
        this.on("success", function (file, responseText) {
            if ("file_id" in responseText) {
                file.file_id = responseText.file_id;
                SELECTS[file.file_id] = new Row(file);
                SELECTS[file.file_id].initHtml();
            }
        });
    }
};

function correct_file_type(file) {
    if (allowed_file_endings.length === 0)
        return true;
    for (const ending of allowed_file_endings) {
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