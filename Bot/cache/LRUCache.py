class LRUCache:
	cache = dict()

	def __init__(self, max_size):
		self.max_size = max_size

	def __contains__(self, key):
		return key in self.cache

	def contains_by_field(self, field, value):
		for key, item in self.cache.items():
			if getattr(item, field) == value:
				return True
		return False

	def get_by_field(self, field, value):
		for key, item in self.cache.items():
			if getattr(item, field) == value:
				return item

	def __getitem__(self, key):
		return self.cache[key]

	def __setitem__(self, key, value):
		if len(self.cache) >= self.max_size:
			self.cache.popitem()
		self.cache[key] = value

	def __delitem__(self, key):
		del self.cache[key]
