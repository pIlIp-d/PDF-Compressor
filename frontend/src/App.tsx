import {useEffect} from 'react';
import axios from "axios";
import {Requester} from "./processing-container/utils/Requester.ts";
import ProcessingContainer from "./processing-container/ProcessingContainer.tsx";

const App = () => {
    useEffect(() => {
        Requester("/get_csrf/").then((response) => {
            if ("csrfToken" in response.data) {
                // setting csrftoken header for all following requests
                axios.defaults.headers.common['X-CSRFTOKEN'] = response.data.csrfToken;
            }
        });
    }, []);

    return (
        <div className={"p-3"} style={{background: "#eeeeee"}}>
            <h2>[x] DragonFile</h2>
            <ProcessingContainer/>
        </div>
    );
};

export default App;