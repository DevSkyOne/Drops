create table if not exists
  `guilds` (
    `guild_id` BIGINT not null comment 'discord guild id',
    `language` varchar(10) not null default 'en' comment 'language code',
    `created_at` timestamp not null default CURRENT_TIMESTAMP,
    primary key (`guild_id`)
  ) engine=InnoDB default charset=utf8mb4 collate=utf8mb4_unicode_ci comment 'guilds';

create table if not exists
  `presets` (
    `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
    `guild_id` bigint(20) NOT NULL COMMENT 'discord guild id',
    `name` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
    `description` text COLLATE utf8mb4_unicode_ci NOT NULL,
    `value` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
    `fetch_credentials` int(11) DEFAULT NULL,
    `reward_credentials` int(11) DEFAULT NULL,
    `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
    PRIMARY KEY (`id`),
    KEY `presets_guild` (`guild_id`),
    CONSTRAINT `presets_guild` FOREIGN KEY (`guild_id`) REFERENCES `guilds` (`guild_id`) ON DELETE NO ACTION ON UPDATE NO ACTION
  ) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_unicode_ci COMMENT = 'presets';