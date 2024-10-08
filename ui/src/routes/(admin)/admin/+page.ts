import { PUBLIC_BASE_URL } from "$env/static/public";
import { AccountsApi, Configuration, FilesApi, PostsApi, type FileDetails, type PostDetails, type UserDetails } from "$lib/api";
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

    const postsAPI = new PostsApi(config);
    const usersAPI = new AccountsApi(config);
    const filesAPI = new FilesApi(config);

    let publishedPosts: PostDetails[] = [];
    let draftPosts: PostDetails[] = [];
    let users: UserDetails[] = [];
    let files: FileDetails[] = [];

    try {
        publishedPosts = (await postsAPI.blogApiListPosts({all: false, drafts: false, limit: 100, offset: 0})).items;

        console.log("Fetched posts: " + publishedPosts.length);
    } catch (error)
    {
        console.log("Error fetching published posts: " + error);
    }

    try {
        draftPosts = (await postsAPI.blogApiListPosts({all: false, drafts: true, limit: 100, offset: 0})).items;

        console.log("Fetched posts: " + draftPosts.length);
    } catch (error)
    {
        console.log("Error fetching draft posts: " + error);
    }

    try {
        users = (await usersAPI.accountsApiListUsers({limit: 100, offset: 0})).items;
        console.log("Fetched users: " + users.length);
    } catch (error) {
        console.log("Error fetching users: " + error);
    }

    try {
        files = (await filesAPI.blogApiListFiles({limit: 100, offset: 0})).items;
        console.log("Fetched files: " + files.length);
    } catch (error) {
        console.log("Error fetching files: " + error);
    }

    return {
        publishedPosts: publishedPosts,
        draftPosts: draftPosts,
        users: users,
        files: files
    }
}