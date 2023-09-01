import {useEffect} from 'react';
import axios from "axios";
import {Requester} from "./processing-container/utils/Requester.ts";
import ProcessingContainer from "./processing-container/ProcessingContainer.tsx";

import {ToastContainer} from 'react-toastify';
import "./custom-toasty-color.css"
import "react-toastify/dist/ReactToastify.css";

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
        <div className={"p-3"} style={{background: "rgba(43,51,210,0.15)"}}>
            <h2>[x] DragonFile</h2>
            <ProcessingContainer/>
            <ToastContainer
                position="bottom-center"
                autoClose={false}
                newestOnTop
                closeOnClick
                rtl={false}
                pauseOnFocusLoss
                draggable
                theme="light"
            />
        </div>
    );
};

export default App;