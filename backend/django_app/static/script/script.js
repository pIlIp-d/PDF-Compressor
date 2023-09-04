function make_request(method, url, async = true, response_handler = null, post_data = null) {
    let xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = response_handler;
    xhttp.open(method, url, async);
    if (post_data != null) xhttp.send(post_data);
    else xhttp.send();
}


function save_plugin_in_url(plugin_name) {
    console.log(plugin_name);
    let new_url = location.href.split("?")[0]
    let parameters = ["plugin="];
    // reserve other parameters if they exist
    if (location.href.split("?").length > 1)
        parameters = location.href.split("?")[1].split("&")

    // set plugin value without changing any other parameters
    for (let p in parameters) {
        if (Number(p) === 0)
            new_url += "?";
        else if (Number(p) < parameters.length - 1)
            new_url += "&";

        if (parameters[p].startsWith("plugin="))
            new_url += "plugin=" + plugin_name
        else
            new_url += parameters[p];
    }
    console.log(new_url);
    window.history.pushState(null, "", new_url);
}