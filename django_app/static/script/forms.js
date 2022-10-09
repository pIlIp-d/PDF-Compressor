function update_visibility_of_container(container_id, disabled) {
    let containers = document.getElementsByClassName(container_id);
    let DISABLED_CLASS = "disabled_container";
    for (let i = 0; i < containers.length; i++) {
        let container = containers[i];
        if (disabled) {
            container.classList.add(DISABLED_CLASS);
        } else {
            container.classList.remove(DISABLED_CLASS);
        }
    }
}