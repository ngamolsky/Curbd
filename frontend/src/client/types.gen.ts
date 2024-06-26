// This file is auto-generated by @hey-api/openapi-ts

export type Body_GeneratePost = {
    images: Array<((Blob | File))>;
    user_input?: string | null;
};

export type GeneratedPost = {
    title: string;
    description: string;
    hashtags: Array<(string)>;
};

export type HTTPValidationError = {
    detail?: Array<ValidationError>;
};

export type PostGenerationResponse = {
    post: GeneratedPost;
    image_count: number;
    total_cost: number;
    image_processing_cost: number;
    post_generation_cost: number;
    timing_info: {
        [key: string]: (number);
    };
};

export type ValidationError = {
    loc: Array<(string | number)>;
    msg: string;
    type: string;
};

export type GeneratePostData = {
    formData: Body_GeneratePost;
};

export type GeneratePostResponse = PostGenerationResponse;

export type $OpenApiTs = {
    '/api/v1/generate-post/': {
        post: {
            req: GeneratePostData;
            res: {
                /**
                 * Successful Response
                 */
                200: PostGenerationResponse;
                /**
                 * Validation Error
                 */
                422: HTTPValidationError;
            };
        };
    };
};