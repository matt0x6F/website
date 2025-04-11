import { goto } from "$app/navigation";
import { PUBLIC_BASE_URL } from "$env/static/public";
import { AccountsApi, Configuration, FilesApi, PostsApi, type FileDetails, type PostDetails, type AdminUserDetails, CommentsApi, type AdminChildCommentList } from "$lib/api";
import { retrieveAccessToken } from "../../../stores/auth"
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

    const postsAPI = new PostsApi(config);
    const usersAPI = new AccountsApi(config);
    const filesAPI = new FilesApi(config);
    const commentsAPI = new CommentsApi(config);

    let publishedPosts: PostDetails[] = [];
    let draftPosts: PostDetails[] = [];
    let users: AdminUserDetails[] = [];
    let files: FileDetails[] = [];
    let comments: AdminChildCommentList[] = [];

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

    try {
        comments = (await commentsAPI.blogApiModQueueList({limit: 100, offset: 0})).items;
        console.log("Fetched comments: " + comments.length);
    } catch (error) {
        console.log("Error fetching comments: " + error);
    }

    return {
        publishedPosts: publishedPosts,
        draftPosts: draftPosts,
        users: users,
        files: files,
        comments: comments
    }
}