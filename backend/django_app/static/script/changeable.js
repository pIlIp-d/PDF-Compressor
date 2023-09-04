// is called by plugin specific javascript
function addChangeableClass(object, callbackFunction) {
    console.log(object)
    object.addEventListener("dblclick", function (e) {
        if (e.target.classList.contains("changeable")) {
            e.target.setAttribute("contenteditable", true);
            e.target.focus();
        }
    });
    object.addEventListener('keydown', function (e) {
        if (e.key === "Enter") {
            // don't type enter
            e.preventDefault();
            // remove focus of field
            e.target.blur();
        }
    });
    object.addEventListener('focusout', function (e) {
        let value = e.target.textContent;
        callbackFunction(value);
    });
}
