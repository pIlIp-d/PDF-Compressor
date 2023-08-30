import {useDropzone} from 'react-dropzone'
import axios from "axios";
import {v4 as uuidv4} from 'uuid';
import {FileType} from "./FileType.ts";
import {Requester} from "./Requester.ts";

type FileUploaderType = {
    updateFile: (id: string, newProps: Partial<FileType>) => void;
    addFile: (file: FileType) => void;
    currentProcessor: string;
    inputFileTypes: {[processor: string]: string[]};
}

const FileUploader = ({updateFile, addFile, currentProcessor, inputFileTypes}: FileUploaderType) => {

    const uploadFile = async (file: File, id: string) => {
        try {
            const formData = new FormData();
            formData.append('file', file);
            // @ts-ignore
            formData.append("csrfmiddlewaretoken", axios.defaults.headers.common['X-CSRFTOKEN']);

            const response = await Requester("/upload_file/",
                {
                    method: "POST",
                    data: formData,
                    onUploadProgress: (progressEvent) => {
                        if (progressEvent.total && progressEvent.total > 0) {
                            updateFile(id, {progress: Math.round((progressEvent.loaded * 100) / progressEvent.total)});
                        }
                    }
                });
            if (response.status == 200) {
                updateFile(id, {id: ""+response.data.file_id});
                id = ""+response.data.file_id;
                updateFile(id, {status: "success"});
            } else {
                updateFile(id, {status: "failed"});
            }
        } catch (error) {
            updateFile(id, {status: "failed"});
        }
    }

    const handleDrop = async (acceptedFiles: File[]) => {
        const tasks = [];
        for (const file of acceptedFiles) {
            const id = uuidv4();

            const processorName = currentProcessor.split("-");
            processorName.pop();  //remove last element / result mime-type

            if (currentProcessor != "null" && !inputFileTypes[processorName.join("-")].includes(file.type) )
                console.log("INCORRECT TYPE", file.type, currentProcessor);
            else {
                addFile({progress: 0, id: id, status: "uploading", name: file.name, size: file.size});
                tasks.push(uploadFile(file, id));
            }
        }
        await Promise.all(tasks);
    };

    const {getRootProps, getInputProps, isDragActive} = useDropzone({onDrop: handleDrop});
    return (
        <>
            <div className={"text-center"} {...getRootProps()}>
                <input {...getInputProps()} />
                {
                    isDragActive
                        ? <p>Drop the files here ...</p>
                        : <span className={"bi bi-plus-lg fs-1"}/>
                }
            </div>
        </>

    );
};

export default FileUploader;