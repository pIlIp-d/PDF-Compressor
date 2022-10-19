function update_visibility_of_container(container_id, disabled) {
    let containers = document.getElementsByClassName(container_id);
    let DISABLED_CLASS = "disabled_container";
    for (let i = 0; i < containers.length; i++) {
        let container = containers[i];
        if (disabled)
            container.classList.add(DISABLED_CLASS);
         else
            container.classList.remove(DISABLED_CLASS);
    }
}

function show_advanced_settings(default_settings_id, disabled) {
    let settings = document.getElementsByClassName(default_settings_id);
    let ADVANCED_SETTINGS = "hidden_settings";
    for (const setting of settings)
        if (setting == disabled)
            setting.classList.add(ADVANCED_SETTINGS);
         else
            setting.classList.remove(ADVANCED_SETTINGS);
    }