export type FileType = {
    id: string;
    progress: number;
    status: "uploading" | "failed" | "success";
    name: string;
    size: number;
}