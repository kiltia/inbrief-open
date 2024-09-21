CREATE DATABASE inbrief;

\c inbrief

CREATE TABLE channel (
    channel_id bigint NOT NULL PRIMARY KEY,
    title varchar(64) NOT NULL,
    subscribers bigint NOT NULL,
    about varchar(512)
);

CREATE TABLE folder (
    chat_folder_link varchar(64) NOT NULL PRIMARY KEY,
    channels bigint[] NOT NULL
);


CREATE TABLE source (
    source_id bigint NOT NULL,
    channel_id bigint NOT NULL,
    text text NOT NULL,
    timestamp timestamp with time zone NOT NULL,
    reference varchar(64) NOT NULL,
    embeddings jsonb NOT NULL,
    views bigint NOT NULL,
    label varchar(16),
    comments text[],
    reactions jsonb,

    PRIMARY KEY (channel_id, source_id)
);

CREATE TABLE request_source (
    request_id uuid NOT NULL,
    source_id uuid NOT NULL,

    PRIMARY KEY (request_id, source_id)
);

CREATE TABLE processed_intervals (
    l_bound timestamp with time zone NOT NULL,
    r_bound timestamp with time zone NOT NULL,
    request_id uuid NOT NULL PRIMARY KEY
);
