create table if not exists
  `guilds` (
    `guild_id` BIGINT not null comment 'discord guild id',
    `language` varchar(10) not null default 'en' comment 'language code',
    `created_at` timestamp not null default CURRENT_TIMESTAMP,
    primary key (`guild_id`)
  ) engine=InnoDB default charset=utf8mb4 collate=utf8mb4_unicode_ci comment 'guilds';