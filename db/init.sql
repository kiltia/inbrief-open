CREATE DATABASE inbrief;

\c inbrief

CREATE TYPE embedder AS ENUM ('jina');

CREATE TABLE channel (
    channel_id bigint NOT NULL PRIMARY KEY,
    title varchar(64) NOT NULL,
    subscribers bigint NOT NULL,
    about varchar(512),
    created_at timestamp with time zone NOT NULL
);

CREATE TABLE folder (
    chat_folder_link varchar(64) NOT NULL PRIMARY KEY,
    channels bigint[] NOT NULL,
    created_at timestamp with time zone NOT NULL
);


CREATE TABLE source (
    source_id bigint NOT NULL,
    channel_id bigint NOT NULL,
    text text NOT NULL,
    ts timestamp with time zone NOT NULL,
    reference varchar(64) NOT NULL,
    views bigint NOT NULL,
    label varchar(16),
    comments text[],
    reactions jsonb,
    request_id uuid NOT NULL,
    created_at timestamp with time zone NOT NULL,

    PRIMARY KEY (channel_id, source_id)
);


CREATE TABLE embeddings (
    source_id bigint NOT NULL,
    channel_id bigint NOT NULL,
    embedder embedder NOT NULL,
    embedding float[],
    created_at timestamp with time zone NOT NULL,

    PRIMARY KEY (source_id, embedder)
);

CREATE TABLE processed_intervals (
    l_bound timestamp with time zone NOT NULL,
    r_bound timestamp with time zone NOT NULL,
    request_id uuid NOT NULL,
    channel_id bigint NOT NULL,
    created_at timestamp with time zone NOT NULL
);
