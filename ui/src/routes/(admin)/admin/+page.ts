import { PUBLIC_BASE_URL } from "$env/static/public";
import { Configuration, PostsApi, type PostDetails } from "$lib/api";
import { getAccessToken } from "../../../stores/auth"
import type { PageLoad } from "./$types"

export const load: PageLoad = async () => {
    const token = await getAccessToken();
    const config = new Configuration({
        basePath: PUBLIC_BASE_URL,
        headers: {
            "Authorization": "Bearer " + token
        }
    });
    const api = new PostsApi(config);

    let publishedPosts: PostDetails[] = [];
    let draftPosts: PostDetails[] = [];

    try {
        publishedPosts = (await api.blogApiListPosts({all: false, limit: 100, offset: 0})).items;

        console.log("Fetched posts: " + publishedPosts.length);
    } catch (error)
    {
        console.log("Error fetching published posts: " + error);
    }

    try {
        draftPosts = (await api.blogApiListPosts({all: false, drafts: true, limit: 100, offset: 0})).items;

        console.log("Fetched posts: " + draftPosts.length);
    } catch (error)
    {
        console.log("Error fetching draft posts: " + error);
    }

    return {
        publishedPosts: publishedPosts,
        draftPosts: draftPosts
    }
}