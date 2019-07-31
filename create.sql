create extension postgis;
create extension timescaledb;

CREATE TABLE IF NOT EXISTS 'observations' (
    time     TIMESTAMPTZ not null,
    tag      TEXT not null,
    value    NUMERIC,
    metadata JSONB,
    location GEOGRAPHY(POINT)
) WITH OWNER pi;

select create_hypertable('observations', 'time', chunk_time_interval=>'7 days');
