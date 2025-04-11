import { PUBLIC_BASE_URL } from "$env/static/public";
import { CommentsApi, Configuration, PostsApi, type CommentList, type PostDetails } from "$lib/api";
import { retrieveAccessToken } from "../../../../../../stores/auth"
import type { PageLoad } from "./$types"

export const load: PageLoad = async ({ params }) => {
    let token = undefined;
    try {
        token = await retrieveAccessToken();
    } catch {
        console.log("No access token found, fetching without one")
    }

    const config = new Configuration({
        basePath: PUBLIC_BASE_URL,
        headers: {
            "Authorization": "Bearer " + token
        }
    });

    const postsAPI = new PostsApi(config);
    const commentsAPI = new CommentsApi(config);

    let comments: CommentList[] = [];

    let post: PostDetails = {
        id: 0,
        title: "",
        content: "",
        slug: params.slug,
        createdAt: new Date(),
        updatedAt: new Date(),
        authorId: 0,
    }

    try {
        post = await postsAPI.blogApiGetPostBySlug({slug: params.slug, year: +params.year});

        console.log("Fetched post: " + post.id);
    } catch (error)
    {
        console.log("Error fetching posts: " + error);
    }

    try {
        comments = (await commentsAPI.blogApiListComments({postId: post.id, topLevel: true})).items;

        let count = 0

        comments.forEach((comment) => {
            count++;
            console.log("Comment " + count + ": " + comment.id);

            comment.children.forEach((child) => {
                count++;
                console.log("Comment " + count + ": " + child.id);
            });
        });

        console.log("Fetched comments: " + comments.length);
    } catch (error) {
        console.log("Error fetching comments: " + error);
    }

    return {
        post,
        comments
    }
}