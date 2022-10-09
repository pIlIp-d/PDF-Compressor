function update_visibility_of_container(container_id, disabled) {
    let container = document.getElementById(container_id);
    let DISABLED_CLASS = "disabled_option";
    if (disabled) {
        container.classList.add(DISABLED_CLASS);
    } else {
        container.classList.remove(DISABLED_CLASS);
    }
}