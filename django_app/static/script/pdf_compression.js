document.addEventListener("DOMContentLoaded", init);

function init() {
    // add onchange functions for special form elements which deactivate other options when checked
    let simple_and_lossless = document.getElementsByName("simple_and_lossless")[0];
    simple_and_lossless.onchange = function () {
        update_visibility_of_container("not_lossless_container", this.checked);
    }
    let ocr_mode = document.getElementsByName("ocr_mode")[0];
    ocr_mode.onchange = function () {
        update_visibility_of_container("no_ocr_container", this.value === "off");
    };
    // call them once to initiate css classes from default values
    simple_and_lossless.onchange();
    ocr_mode.onchange();
}