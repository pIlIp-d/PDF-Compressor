import React, {useEffect, useState} from 'react';
import './custom-dropzone.css'
import FileUploader from "./FileUploader.tsx";
import {FileType} from "./FileType.ts";
import DroppedFile from "./DroppedFile.tsx";
import {useLocation} from 'react-router-dom';
import axios from "axios";
import {Requester} from "./Requester.ts";


type TabType = "Convert" | "Compress" | "Merge";

const App: React.FC = () => {
    const [files, setFiles] = useState<FileType[]>([]);
    const location = useLocation()

    const [currentTab, setCurrentTab] = useState<TabType>();

    async function removeFile(id: string) {
        setFiles(oldFiles => oldFiles.filter(f => f.id != id));
        const response = await Requester(`/file/${id}/`, {
            method: "DELETE",
            params: {file_origin: "uploaded"}
        });
        if (response.status != 200) {
            console.log("Couldn't remove file from server."); // TODO incorporate error message into GUI
        }
    }
    useEffect(() => {
        Requester("/get_csrf/").then((response) => {
            if ("csrfToken" in response.data) {
                // setting csrftoken header for all following requests
                axios.defaults.headers.common['X-CSRFTOKEN'] = response.data.csrfToken;
            }
        });
    }, []);

    useEffect(() => {
        const tab = location.hash.substring(1);
        switch (tab) {
            case "Convert":
            case "Compress":
            case "Merge":
                setCurrentTab(tab);
                break;
            default:
                setCurrentTab("Convert");
        }
        console.log(tab);
    }, [location]);
    return (
        <div className={"container-lg mt-5"}>
            <ul className="nav nav-tabs">
                <li className="nav-item">
                    <a className={`text-dark nav-link ${currentTab === "Convert" && "active fw-bold"}`}
                       href="#Convert">Convert</a>
                </li>
                <li className="nav-item">
                    <a className={`text-dark nav-link ${currentTab === "Compress" && "active fw-bold"}`}
                       href="#Compress">Compress</a>
                </li>
                <li className="nav-item">
                    <a className={`text-dark nav-link ${currentTab === "Merge" && "active fw-bold"}`}
                       href="#Merge">Merge</a>
                </li>
            </ul>

            <div className={"border border-top-0"}>
                {files.map((file, key) =>
                    <DroppedFile
                        key={key}
                        id={file.id}
                        progress={file.progress}
                        status={file.status}
                        name={file.name}
                        size={file.size}
                        onDelete={async () => await removeFile(file.id)}/>
                )}
                <div className={"w-100 py-2"}>
                    <FileUploader setFiles={setFiles}></FileUploader>
                </div>
            </div>
            <div className={"border border-top-0 rounded-bottom p-3"}>
                <button className={"btn btn-secondary"}>Convert All</button>
            </div>
        </div>
    );
};

export default App;