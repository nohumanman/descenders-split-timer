CREATE TABLE Trail (
    "trail_id" SERIAL PRIMARY KEY,
    "world_name" TEXT,
    "trail_name" TEXT
);

CREATE TABLE PlayerTime (
    "player_time_id" SERIAL, -- Unique ID for each time
    "steam_id" TEXT, -- Steam ID of the player
    "submission_timestamp" REAL, -- Time the time was submitted
    "trail_id" INTEGER,
    CONSTRAINT "fk_trail_id"
    FOREIGN KEY ("trail_id")
    REFERENCES Trail ("trail_id"),
    "bike_id" INTEGER,
    "starting_speed" REAL, -- Speed the player started at
    "version" TEXT, -- modkit version used
    "game_version" TEXT, -- game version used
    "deleted" BOOLEAN, -- If the time has been deleted
    PRIMARY KEY ("player_time_id") -- Primary key is the time ID
);

CREATE TABLE Verification (
    "verification_timestamp" TIMESTAMP, -- Time the verification was submitted
    "verified" BOOLEAN, -- If the time has been verified
    "verifier_id" BIGINT, -- Discord ID of the verifier
    "player_time_id" INTEGER, -- ID of the time being verified
    CONSTRAINT "fk_player_time_id"
    FOREIGN KEY ("player_time_id")
    REFERENCES PlayerTime ("player_time_id"),
    PRIMARY KEY ("player_time_id") -- Primary key is the time ID
);

CREATE TABLE BikeType (
    "bike_id" SERIAL PRIMARY KEY,
    "bike_name" TEXT
);
INSERT INTO BikeType ("bike_id", "bike_name") VALUES (0, 'enduro');
INSERT INTO BikeType ("bike_id", "bike_name") VALUES (1, 'downhill');
INSERT INTO BikeType ("bike_id", "bike_name") VALUES (2, 'hardtail');

CREATE TABLE WebsiteUser (
    "discord_id" BIGINT UNIQUE,
    "steam_id" TEXT,
    "discord_name" TEXT,
    "email" TEXT,
    PRIMARY KEY ("discord_id")
);

CREATE TABLE Player (
    "steam_id" TEXT UNIQUE CHECK (LENGTH("steam_id") = 17),
    "steam_name" TEXT,
    PRIMARY KEY ("steam_id")
);

CREATE TABLE CheckpointTime (
    "player_time_id" INTEGER NOT NULL,
    "checkpoint_num" INTEGER,
    "checkpoint_time" REAL,
    CONSTRAINT "fk_player_time_id"
    FOREIGN KEY ("player_time_id")
    REFERENCES PlayerTime ("player_time_id")
    ON DELETE CASCADE
);

CREATE TABLE PendingItem (
    "steam_id" TEXT,
    "item_id" TEXT UNIQUE,
    "time_redeemed" TIMESTAMP,
    CONSTRAINT "fk_steam_id"
    FOREIGN KEY ("steam_id")
    REFERENCES Player ("steam_id")
);
