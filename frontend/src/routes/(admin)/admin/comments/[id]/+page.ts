import { goto } from '$app/navigation';
import { PUBLIC_BASE_URL } from '$env/static/public';
import { CommentsApi, Configuration, type CommentList } from '$lib/api';
import { retrieveAccessToken } from '../../../../../stores/auth';
import type { PageLoad } from './$types';

export const load: PageLoad = async ({params}) => {
    const commentID = params.id;
    let comment: CommentList | null = null;

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

    try {
        const commentsAPI = new CommentsApi(config);

        comment = await commentsAPI.blogApiGetComment({id: +commentID});
        
        console.log("Fetched comment: " + comment.id);
    } catch (error) {
        console.log("Error fetching comment: " + error);
    }

    return {
        comment,
    }
}