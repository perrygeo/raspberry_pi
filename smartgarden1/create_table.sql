create table obs
(
    time timestamptz not null,
    airquality float,
    humidity float,
    ir float,
    lumens float,
    rangefinder float,
    soilmoisture float,
    temperature float,
    uv float,
    notes jsonb
);

SELECT create_hypertable('obs', 'time');
