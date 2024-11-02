import { goto } from "$app/navigation";
import { PUBLIC_BASE_URL } from "$env/static/public";
import { CommentsApi, Configuration, type AdminCommentList } from "$lib/api";
import { retrieveAccessToken } from "../../../../../stores/auth"
import type { PageLoad } from "./$types"

export const load: PageLoad = async () => {
    let token = undefined;
    try {
        token = await retrieveAccessToken();
    } catch {
        goto('/login');
    }

    const config = new Configuration({
        basePath: PUBLIC_BASE_URL,
        headers: {
            "Authorization": "Bearer " + token
        }
    });

    const commentsAPI = new CommentsApi(config);

    let comments: AdminCommentList[] = [];

    try {
        comments = (await commentsAPI.blogApiModQueueList({reviewed: false})).items;

        console.log("Fetched comments: " + comments.length);
    } catch (error) {
        console.log("Error fetching comments: " + error);
    }

    return {
        comments
    }
}