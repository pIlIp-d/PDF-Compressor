document.addEventListener("DOMContentLoaded", init);

function init() {
    // add onchange functions for special form elements which deactivate other options when checked
    let simple_and_lossless = document.getElementsByName("simple_and_lossless")[0];
    simple_and_lossless.onchange = function () {
        let list_of_items = ["compression_mode", "default_pdf_dpi", "ocr_mode", "tesseract_language"]
        for (let i in list_of_items)
            update_visibility_of_container("id_" + list_of_items[i], this.checked);
    }
    let ocr_mode = document.getElementsByName("ocr_mode")[0];
    ocr_mode.onchange = function () {
        update_visibility_of_container("id_tesseract_language", this.value === "off");
    };
    // call them once to initiate css classes from default values
    simple_and_lossless.onchange();
    ocr_mode.onchange();
}