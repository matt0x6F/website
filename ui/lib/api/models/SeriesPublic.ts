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
/**
 * 
 * @export
 * @interface SeriesPublic
 */
export interface SeriesPublic {
    /**
     * 
     * @type {string}
     * @memberof SeriesPublic
     */
    title: string;
    /**
     * URL-friendly identifier. Will be auto-generated from title if not provided.
     * @type {string}
     * @memberof SeriesPublic
     */
    slug: string;
    /**
     * 
     * @type {string}
     * @memberof SeriesPublic
     */
    description?: string | null;
    /**
     * 
     * @type {number}
     * @memberof SeriesPublic
     */
    id: number;
    /**
     * 
     * @type {Date}
     * @memberof SeriesPublic
     */
    createdAt: Date;
    /**
     * 
     * @type {Date}
     * @memberof SeriesPublic
     */
    updatedAt: Date;
    /**
     * 
     * @type {number}
     * @memberof SeriesPublic
     */
    postCount?: number;
}

/**
 * Check if a given object implements the SeriesPublic interface.
 */
export function instanceOfSeriesPublic(value: object): value is SeriesPublic {
    if (!('title' in value) || value['title'] === undefined) return false;
    if (!('slug' in value) || value['slug'] === undefined) return false;
    if (!('id' in value) || value['id'] === undefined) return false;
    if (!('createdAt' in value) || value['createdAt'] === undefined) return false;
    if (!('updatedAt' in value) || value['updatedAt'] === undefined) return false;
    return true;
}

export function SeriesPublicFromJSON(json: any): SeriesPublic {
    return SeriesPublicFromJSONTyped(json, false);
}

export function SeriesPublicFromJSONTyped(json: any, ignoreDiscriminator: boolean): SeriesPublic {
    if (json == null) {
        return json;
    }
    return {
        
        'title': json['title'],
        'slug': json['slug'],
        'description': json['description'] == null ? undefined : json['description'],
        'id': json['id'],
        'createdAt': (new Date(json['created_at'])),
        'updatedAt': (new Date(json['updated_at'])),
        'postCount': json['post_count'] == null ? undefined : json['post_count'],
    };
}

export function SeriesPublicToJSON(value?: SeriesPublic | null): any {
    if (value == null) {
        return value;
    }
    return {
        
        'title': value['title'],
        'slug': value['slug'],
        'description': value['description'],
        'id': value['id'],
        'created_at': ((value['createdAt']).toISOString()),
        'updated_at': ((value['updatedAt']).toISOString()),
        'post_count': value['postCount'],
    };
}

