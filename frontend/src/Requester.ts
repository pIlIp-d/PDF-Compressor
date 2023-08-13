import axios, {AxiosRequestConfig} from "axios";
import {API_HOST} from "./config.ts";

/**
 * Wrapper for axios requests, injects all necessary parameters to work with the django backend
 * @param url starts with /, contains the path to the correct request without having to include the server url, port, etc. (f.e '/file/upload')
 *            the correct url to the server gets injected from the config
 * @param additionalOptions any other features of axios can still be used by passing the config to this variable
 * @returns Promise == axios response
 **/
export function Requester(url: string, additionalOptions: Partial<Omit<AxiosRequestConfig, "url" | "withCredentials">> = {}) {
    return axios({
        url: API_HOST + url,
        withCredentials: true,
        ...additionalOptions
    });
}