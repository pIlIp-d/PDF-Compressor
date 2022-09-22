let compress_button = document.getElementById("compress_button");
let csrfmiddlewaretoken = document.getElementsByName("csrfmiddlewaretoken")[0].value;

let dz = null;
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
                let user_id = "{{ user_id }}";
                let removeFileRequest = new XMLHttpRequest();
                removeFileRequest.onreadystatechange = function () {
                };
                removeFileRequest.open(
                    "GET",
                    "{{ dir }}api/remove_file/?file_id=" + file.file_id + "&user_id=" + user_id + "&queue_csrf_token=" + queue_csrf_token,
                    true
                );
                removeFileRequest.send();
            }
            if (_this.files.length === 0)
                deactivate_compression_button() // case: no element
        });
        this.on("queuecomplete", function () {
            activate_compression_button();
        });
        this.on("success", function (file, responseText) {
            file.file_id = responseText.file_id;
        });

    }
};

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
    for (let ending in allowed_file_ending) {
        if (ending != null && filename.endsWith(allowed_file_ending[ending])) {
            return true;
        }
    }
    return false;
}

// Animations
function showUnsupportedFileAnimation() {
    let dropzone = document.getElementById("my-dropzone");
    dropzone.classList.add("wiggle");
    setTimeout(function () {
        dropzone.classList.remove("wiggle");
    }, 1000); //At least the time the animation lasts
}