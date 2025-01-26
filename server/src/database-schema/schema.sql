CREATE TABLE trails (
    "trail_id" SERIAL PRIMARY KEY,
    "world_name" TEXT,
    "trail_name" TEXT,
    UNIQUE("world_name", "trail_name")
);

CREATE TABLE bike_types (
    "bike_id" INTEGER PRIMARY KEY,
    "bike_name" TEXT
);
INSERT INTO bike_types ("bike_id", "bike_name") VALUES (0, 'enduro');
INSERT INTO bike_types ("bike_id", "bike_name") VALUES (1, 'downhill');
INSERT INTO bike_types ("bike_id", "bike_name") VALUES (2, 'hardtail');

CREATE TABLE player_times (
    "player_time_id" BIGINT, -- Unique ID for each time
    "steam_id" TEXT, -- Steam ID of the player
    "submission_timestamp" FLOAT, -- Time the time was submitted
    "trail_id" INTEGER,
    "bike_id" INTEGER,
    "starting_speed" FLOAT, -- Speed the player started at
    "version" TEXT, -- modkit version used
    "game_version" TEXT, -- game version used
    "deleted" BOOLEAN, -- If the time has been deleted
    PRIMARY KEY ("player_time_id") -- Primary key is the time ID
);

CREATE TABLE verifications (
    "player_time_id" BIGINT, -- ID of the time being verified
    "verifier_id" BIGINT, -- Discord ID of the verifier
    "verification_timestamp" FLOAT, -- Time the verification was submitted
    "verified" BOOLEAN -- If the time has been verified
);

CREATE TABLE website_users (
    "discord_id" BIGINT UNIQUE,
    "steam_id" TEXT,
    "discord_name" TEXT,
    "authorised" BOOLEAN,
    PRIMARY KEY ("discord_id")
);

CREATE TABLE players (
    "steam_id" TEXT PRIMARY KEY,
    "steam_name" TEXT
);

CREATE TABLE checkpoint_times (
    "player_time_id" BIGINT NOT NULL,
    "checkpoint_num" INTEGER,
    "checkpoint_time" FLOAT,
    FOREIGN KEY ("player_time_id")
    REFERENCES player_times ("player_time_id")
    ON DELETE CASCADE
);

CREATE TABLE pending_items (
    "steam_id" TEXT,
    "item_id" TEXT,
    "time_redeemed" FLOAT,
    CONSTRAINT "fk_steam_id"
    FOREIGN KEY ("steam_id")
    REFERENCES players ("steam_id")
);




CREATE VIEW final_times AS

-- First CTE: Rank rows by checkpoint_num for each player_time_id
WITH RankedCheckpoints AS (
    SELECT 
        player_times.steam_id,                          -- Select the Steam ID of the player
		player_times.trail_id,
        checkpoint_times.player_time_id,               -- Select the player's time ID
        checkpoint_times.checkpoint_num,               -- Select the checkpoint number
        checkpoint_times.checkpoint_time,              -- Select the time taken for the checkpoint
        ROW_NUMBER() OVER (                            -- Generate a row number for each player_time_id
            PARTITION BY checkpoint_times.player_time_id -- Group rows by player_time_id
            ORDER BY checkpoint_times.checkpoint_num DESC -- Rank rows by checkpoint_num in descending order
        ) AS rn                                        -- Alias the row number as `rn`
    FROM 
        checkpoint_times
    JOIN
        player_times
        ON player_times.player_time_id = checkpoint_times.player_time_id -- Join to get Steam ID
),

-- Second CTE: Filter for the highest checkpoint_num (rn = 1) and rank rows by checkpoint_time for each steam_id
RankedByTime AS (
    SELECT 
        steam_id,                                       -- The Steam ID of the player
        player_time_id,                                 -- The player's time ID
        checkpoint_num,                                 -- The largest checkpoint number
        checkpoint_time,                                -- The time at the largest checkpoint
		trail_id,
        ROW_NUMBER() OVER (                            -- Generate a row number for each steam_id
            PARTITION BY steam_id                      -- Group rows by steam_id
            ORDER BY checkpoint_time ASC               -- Rank rows by the lowest checkpoint_time
        ) AS rn_by_time                                -- Alias the row number as `rn_by_time`
    FROM 
        RankedCheckpoints
    WHERE 
        rn = 1                                         -- Keep only rows with the largest checkpoint_num per player_time_id
)

-- Final Query: Select only the rows with the lowest checkpoint_time for each steam_id
SELECT 
    player_time_id,                                    -- The player's time ID
    checkpoint_time AS final_time                                  -- The lowest checkpoint time for the steam_id
FROM 
    RankedByTime
JOIN trails ON trails.trail_id = RankedByTime.trail_id
WHERE 
    rn_by_time = 1                                     -- Keep only rows with the lowest checkpoint_time for each steam_id
ORDER BY 
    checkpoint_time;                                          -- Order the results by Steam ID


CREATE VIEW final_times_detailed AS
 SELECT player_times.player_time_id,
    player_times.steam_id,
    player_times.submission_timestamp,
    player_times.trail_id,
    player_times.bike_id,
    player_times.starting_speed,
    player_times.version,
    player_times.game_version,
    player_times.deleted,
    final_times.final_time,
    COALESCE(verifications.verified, FALSE) AS verified,
    verifications.verifier_id
   FROM final_times
     JOIN player_times ON player_times.player_time_id = final_times.player_time_id
     LEFT JOIN verifications ON verifications.player_time_id = player_times.player_time_id;