    function make_request(method, url, async = true, response_handler = null, post_data = null) {
        let xhttp = new XMLHttpRequest();
        xhttp.onreadystatechange = response_handler;
        xhttp.open(method, url, async);
        if (post_data != null) xhttp.send(post_data);
        else xhttp.send();
    }