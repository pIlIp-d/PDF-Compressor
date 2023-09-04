import axios from "axios";

export function download(fileUrl: string) {
    axios({
        url: fileUrl,
        method: 'GET',
        responseType: 'blob'
    }).then((response) => {
        const url = window.URL
            .createObjectURL(new Blob([response.data]));
        const link = document.createElement('a');
        link.href = url;
        link.setAttribute('download', fileUrl.split("/").pop() as string);
        document.body.appendChild(link);
        link.click();
    })
}
