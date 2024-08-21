import { writable } from "svelte/store";

export const baseURL = writable("http://localhost:8000");