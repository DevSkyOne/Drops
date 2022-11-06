import datetime

from aiomysql import Pool, DictCursor

from Bot.cache.Caches import guild_cache
from Database import get_pool


class GuildData:

	def __init__(self, guild_id: int):
		self.guild_id = guild_id
		self.language = "en"
		self.presets = list()
		self.cronjob = None
		self.cronjob_presets = []

	async def load(self):
		if guild_cache.__contains__(self.guild_id):
			entry = guild_cache[self.guild_id]
			self.language = entry.language
			self.presets = entry.presets
			self.cronjob = entry.cronjob
			self.cronjob_presets = entry.cronjob_presets
			return self
		pool: Pool = await get_pool()
		async with pool.acquire() as conn:
			async with conn.cursor() as cur:
				await cur.execute("SELECT * FROM guilds WHERE guild_id = %s", (self.guild_id,))
				data = await cur.fetchone()
				if data is None:
					await cur.execute("INSERT INTO guilds (guild_id, language) VALUES (%s, %s)", (self.guild_id, self.language))
					await conn.commit()
					print("Created new guild entry for guild with id", self.guild_id)
					return
				self.language = data[1]
				print("Loaded guild entry for guild with id", self.guild_id)
		pool.close()
		await pool.wait_closed()
		await self.load_presets()
		guild_cache[self.guild_id] = self
		return self

	async def load_presets(self):
		pool: Pool = await get_pool()
		async with pool.acquire() as conn:
			async with conn.cursor(DictCursor) as cur:
				await cur.execute("SELECT id, guild_id, name, description, value, fetch_credentials, reward_credentials "
				                  "FROM presets WHERE guild_id = %s", (self.guild_id,))
				data = [PresetData(**preset) for preset in await cur.fetchall()]
				if data is None:
					print("No presets found for guild with id", self.guild_id)
					return
				self.presets = data
				print("Loaded presets for guild with id", self.guild_id)
		pool.close()
		await pool.wait_closed()

	async def save_presets(self):
		for preset in self.presets:
			await preset.save()

	async def save(self):
		pool: Pool = await get_pool()
		async with pool.acquire() as conn:
			async with conn.cursor() as cur:
				await cur.execute("UPDATE guilds SET language = %s WHERE guild_id = %s", (self.language, self.guild_id))
				await conn.commit()
				print("Saved guild entry for guild with id", self.guild_id)
		pool.close()
		await pool.wait_closed()
		await self.save_presets()
		guild_cache[self.guild_id] = self

	async def delete(self):
		pool: Pool = await get_pool()
		async with pool.acquire() as conn:
			async with conn.cursor() as cur:
				await cur.execute("DELETE FROM guilds WHERE guild_id = %s", (self.guild_id,))
				await conn.commit()
				print("Deleted guild entry for guild with id", self.guild_id)
		pool.close()
		await pool.wait_closed()


class PresetData:

	def __init__(self, id: int = -1, guild_id: int = -1, name: str = "", description: str = "", value: str = None,
	             fetch_credentials: int = None, reward_credentials: int = None):
		self.id = id
		self.guild_id = guild_id
		self.name = name
		self.description = description
		self.value = value
		self.fetch_credentials = fetch_credentials
		self.reward_credentials = reward_credentials

	async def load(self):
		pool: Pool = await get_pool()
		async with pool.acquire() as conn:
			async with conn.cursor() as cur:
				await cur.execute("SELECT * FROM presets WHERE id = %s", (self.id,))
				data = await cur.fetchone()
				if data is None:
					await cur.execute("INSERT INTO presets (guild_id, name, description) VALUES (%s, %s, %s)",
					                  (self.guild_id, self.name, self.description))
					await conn.commit()
					self.id = cur.lastrowid
					print("Created new preset entry with id", self.id)
					return self
				self.guild_id = data[1]
				self.name = data[2]
				self.description = data[3]
				self.value = data[4]
				print("Loaded preset entry with id", self.id)
		pool.close()
		await pool.wait_closed()
		return self

	async def save(self):
		pool: Pool = await get_pool()
		async with pool.acquire() as conn:
			async with conn.cursor() as cur:
				if self.value is None:
					await cur.execute("UPDATE presets SET name = %s, description = %s WHERE id = %s", (self.name,
					                                                                                   self.description,
					                                                                                   self.id))
				else:
					await cur.execute("UPDATE presets SET name = %s, description = %s, value = %s WHERE id = %s", (self.name,
					                                                                                               self.description,
					                                                                                               self.value,
					                                                                                               self.id))
				await conn.commit()
				print("Saved preset entry with id", self.id)
		pool.close()
		await pool.wait_closed()

	async def delete(self):
		pool: Pool = await get_pool()
		async with pool.acquire() as conn:
			async with conn.cursor() as cur:
				await cur.execute("DELETE FROM presets WHERE id = %s", (self.id,))
				await conn.commit()
				print("Deleted preset entry with id", self.id)
		pool.close()
		await pool.wait_closed()

	async def add_to_cronjob(self, cronjob_id: int):
		pool: Pool = await get_pool()
		async with pool.acquire() as conn:
			async with conn.cursor() as cur:
				await cur.execute("INSERT INTO cronjobs_presets (cronjob_id, preset_id) VALUES (%s, %s)", (cronjob_id, self.id))
				await conn.commit()
				print("Added preset with id", self.id, "to cronjob with id", cronjob_id)
		pool.close()
		await pool.wait_closed()

	async def remove_from_cronjob(self, cronjob_id: int):
		pool: Pool = await get_pool()
		async with pool.acquire() as conn:
			async with conn.cursor() as cur:
				await cur.execute("DELETE FROM cronjobs_presets WHERE cronjob_id = %s AND preset_id = %s", (cronjob_id, self.id))
				await conn.commit()
				print("Removed preset with id", self.id, "from cronjob with id", cronjob_id)
		pool.close()
		await pool.wait_closed()


class CronjobData:

	def __init__(self, _id: int = -1):
		self.id = _id
		self.name = ""
		self.description = ""
		self.cron = ""
		self.load()

	async def load(self):
		pool: Pool = await get_pool()
		async with pool.acquire() as conn:
			async with conn.cursor() as cur:
				await cur.execute("SELECT * FROM cronjobs WHERE id = %s", (self.id,))
				data = await cur.fetchone()
				if data is None:
					await cur.execute("INSERT INTO cronjobs (name, description, cron) VALUES (%s, %s, %s)", (self.name,
					                                                                                         self.description,
					                                                                                         self.cron))
					await conn.commit()
					self.id = cur.lastrowid
					print("Created new cronjob entry with id", self.id)
					return
				self.name = data[1]
				self.description = data[2]
				self.cron = data[3]
				print("Loaded cronjob entry with id", self.id)
		pool.close()
		await pool.wait_closed()

	async def save(self):
		pool: Pool = await get_pool()
		async with pool.acquire() as conn:
			async with conn.cursor() as cur:
				await cur.execute("UPDATE cronjobs SET name = %s, description = %s, cron = %s WHERE id = %s", (self.name,
				                                                                                               self.description,
				                                                                                               self.cron,
				                                                                                               self.id))
				await conn.commit()
				print("Saved cronjob entry with id", self.id)
		pool.close()
		await pool.wait_closed()

	async def delete(self):
		pool: Pool = await get_pool()
		async with pool.acquire() as conn:
			async with conn.cursor() as cur:
				await cur.execute("DELETE FROM cronjobs WHERE id = %s", (self.id,))
				await conn.commit()
				print("Deleted cronjob entry with id", self.id)
		pool.close()
		await pool.wait_closed()


class APICredentials:

	def __init__(self, _id: int = -1):
		self.id = _id
		self.name = ""
		self.type = "GET"
		self.url = ""
		self.headers = ""
		self.body = ""
		self.load()

	async def load(self):
		pool: Pool = await get_pool()
		async with pool.acquire() as conn:
			async with conn.cursor() as cur:
				await cur.execute("SELECT * FROM api_credentials WHERE id = %s", (self.id,))
				data = await cur.fetchone()
				if data is None:
					await cur.execute("INSERT INTO api_credentials (name, type, url, headers, body) VALUES (%s, %s, %s, %s, %s)",
					                  (self.name, self.type, self.url, self.headers, self.body))
					await conn.commit()
					self.id = cur.lastrowid
					print("Created new api credentials entry with id", self.id)
					return
				self.name = data[1]
				self.type = data[2]
				self.url = data[3]
				self.headers = data[4]
				self.body = data[5]
				print("Loaded api credentials entry with id", self.id)
		pool.close()
		await pool.wait_closed()

	async def save(self):
		pool: Pool = await get_pool()
		async with pool.acquire() as conn:
			async with conn.cursor() as cur:
				await cur.execute("UPDATE api_credentials SET name = %s, type = %s, url = %s, headers = %s, body = %s WHERE id = %s",
				                  (self.name, self.type, self.url, self.headers, self.body, self.id))
				await conn.commit()
				print("Saved api credentials entry with id", self.id)
		pool.close()
		await pool.wait_closed()

	async def delete(self):
		pool: Pool = await get_pool()
		async with pool.acquire() as conn:
			async with conn.cursor() as cur:
				await cur.execute("DELETE FROM api_credentials WHERE id = %s", (self.id,))
				await conn.commit()
				print("Deleted api credentials entry with id", self.id)
		pool.close()
		await pool.wait_closed()