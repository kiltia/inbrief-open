CREATE DATABASE inbrief;

\c inbrief

CREATE TYPE embedder AS ENUM ('jina');

CREATE TYPE inbox_status AS ENUM ('pending', 'in_progress', 'done');

CREATE TABLE scrape_inbox (
    request_id uuid NOT NULL PRIMARY KEY,
    chat_folder_link varchar(64) NOT NULL,
    right_bound timestamp WITH TIME ZONE NOT NULL,
    left_bound timestamp WITH TIME ZONE NOT NULL,
    social boolean NOT NULL,
    exporters varchar(64)[] NOT NULL,
    created_at timestamp WITH TIME ZONE NOT NULL,
    status inbox_status DEFAULT 'pending',
    worker_id varchar(64),
);

CREATE TABLE channel (
    channel_id bigint NOT NULL PRIMARY KEY,
    title varchar(64) NOT NULL,
    subscribers bigint NOT NULL,
    about varchar(512),
    created_at timestamp WITH TIME ZONE NOT NULL
);

CREATE TABLE folder (
    chat_folder_link varchar(64) NOT NULL PRIMARY KEY,
    channels bigint[] NOT NULL,
    created_at timestamp WITH TIME ZONE NOT NULL
);

CREATE TABLE source (
    source_id uuid NOT NULL PRIMARY KEY,
    text text NOT NULL,
    ts timestamp WITH TIME ZONE NOT NULL,
    channel_id bigint NOT NULL,
    reference varchar(64) NOT NULL,
    views bigint,
    comments text[],
    reactions jsonb,
    request_id uuid NOT NULL,
    created_at timestamp WITH TIME ZONE NOT NULL
);


CREATE TABLE embeddings (
    source_id uuid NOT NULL,
    embedder embedder NOT NULL,
    embedding float[],
    created_at timestamp WITH TIME ZONE NOT NULL,

    PRIMARY KEY (source_id, embedder)
);

CREATE TABLE processed_intervals (
    l_bound timestamp WITH TIME ZONE NOT NULL,
    r_bound timestamp WITH TIME ZONE NOT NULL,
    request_id uuid NOT NULL,
    channel_id bigint NOT NULL,
    created_at timestamp WITH TIME ZONE NOT NULL
);

CREATE VIEW sources_extended AS (
	SELECT
        source_id,
        text,
        ts,
        reference,
        views,
        comments,
        reactions,
        source.created_at,
        embedder,
        embedding
	FROM source
	INNER JOIN embeddings USING (source_id)
);
