/* tslint:disable */
/* eslint-disable */
/**
 * ooo-yay.com API
 * Resource-based API for ooo-yay.com.
 *
 * The version of the OpenAPI document: 1.0.0
 * 
 *
 * NOTE: This class is auto generated by OpenAPI Generator (https://openapi-generator.tech).
 * https://openapi-generator.tech
 * Do not edit the class manually.
 */

import { mapValues } from '../runtime';
import type { SeriesSummary } from './SeriesSummary';
import {
    SeriesSummaryFromJSON,
    SeriesSummaryFromJSONTyped,
    SeriesSummaryToJSON,
} from './SeriesSummary';

/**
 * 
 * @export
 * @interface PostDetails
 */
export interface PostDetails {
    /**
     * 
     * @type {number}
     * @memberof PostDetails
     */
    id: number;
    /**
     * 
     * @type {string}
     * @memberof PostDetails
     */
    title: string;
    /**
     * 
     * @type {string}
     * @memberof PostDetails
     */
    content: string;
    /**
     * 
     * @type {Date}
     * @memberof PostDetails
     */
    createdAt: Date;
    /**
     * 
     * @type {Date}
     * @memberof PostDetails
     */
    updatedAt: Date;
    /**
     * 
     * @type {Date}
     * @memberof PostDetails
     */
    published?: Date | null;
    /**
     * 
     * @type {number}
     * @memberof PostDetails
     */
    authorId: number;
    /**
     * 
     * @type {string}
     * @memberof PostDetails
     */
    slug: string;
    /**
     * 
     * @type {SeriesSummary}
     * @memberof PostDetails
     */
    series?: SeriesSummary | null;
}

/**
 * Check if a given object implements the PostDetails interface.
 */
export function instanceOfPostDetails(value: object): value is PostDetails {
    if (!('id' in value) || value['id'] === undefined) return false;
    if (!('title' in value) || value['title'] === undefined) return false;
    if (!('content' in value) || value['content'] === undefined) return false;
    if (!('createdAt' in value) || value['createdAt'] === undefined) return false;
    if (!('updatedAt' in value) || value['updatedAt'] === undefined) return false;
    if (!('authorId' in value) || value['authorId'] === undefined) return false;
    if (!('slug' in value) || value['slug'] === undefined) return false;
    return true;
}

export function PostDetailsFromJSON(json: any): PostDetails {
    return PostDetailsFromJSONTyped(json, false);
}

export function PostDetailsFromJSONTyped(json: any, ignoreDiscriminator: boolean): PostDetails {
    if (json == null) {
        return json;
    }
    return {
        
        'id': json['id'],
        'title': json['title'],
        'content': json['content'],
        'createdAt': (new Date(json['created_at'])),
        'updatedAt': (new Date(json['updated_at'])),
        'published': json['published'] == null ? undefined : (new Date(json['published'])),
        'authorId': json['author_id'],
        'slug': json['slug'],
        'series': json['series'] == null ? undefined : SeriesSummaryFromJSON(json['series']),
    };
}

export function PostDetailsToJSON(value?: PostDetails | null): any {
    if (value == null) {
        return value;
    }
    return {
        
        'id': value['id'],
        'title': value['title'],
        'content': value['content'],
        'created_at': ((value['createdAt']).toISOString()),
        'updated_at': ((value['updatedAt']).toISOString()),
        'published': value['published'] == null ? undefined : ((value['published'] as any).toISOString()),
        'author_id': value['authorId'],
        'slug': value['slug'],
        'series': SeriesSummaryToJSON(value['series']),
    };
}

