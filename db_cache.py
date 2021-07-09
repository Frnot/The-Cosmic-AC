# Abstract class that caches DB data in memory
# Cache is automatically maintained
# Use this class instead of accessing database manually

from sqlite3.dbapi2 import Error
import db
import logging
import pickle
log = logging.getLogger(__name__)

class DBCache:
    def __init__(self, table_name, key_name, value_name, serialize=False):
        self.cache_dict = {}
        self.table_name = table_name
        self.key_name = key_name
        self.value_name = value_name
        self.serialize = serialize



    async def add_or_update(self, key, value):
        if self.cache_dict.get(key) != value:
            if self.cache_dict.get(key) is None:
                log.debug(f"Adding value for {key} in {self.table_name}")
            else:
                log.debug(f"Changing {key} in {self.table_name}")
            self.cache_dict[key] = value

        await self.flush_cache_item(key)


    async def remove(self, key):
        if await self.get(key) is None:
            log.debug(f"Cannot remove item with key '{key}' as it doesnt not exist in db table '{self.table_name}'")
            return
        else:
            log.debug(f"Removing row with key '{self.key_name}'='{key}' in table '{self.table_name}'")
            self.cache_dict.pop(key)
            try:
                await db.delete(self.table_name, [self.key_name, key])
            except Exception as e:
                log.error(f"Cannot delete item from database.")


    async def get(self, key):
        if self.cache_dict.get(key) is None:
            log.debug(f"Key '{key}' not found in cache for '{self.table_name}'. Searching DB")
            
            try:
                cache_item = await db.select(self.value_name, self.table_name, self.key_name, key)
            except Exception as e:
                log.error(f"Cannot retrieve item from database.")
                return None

            if cache_item is None:
                log.debug(f"Could not find {self.value_name} in table {self.table_name} for {self.key_name} = {key}")
                return None
            else:
                log.debug(f"Found {self.value_name} in table {self.table_name} for {self.key_name} = {key}. Loading into cache")
                if self.serialize: cache_item = pickle.loads(cache_item)
                self.cache_dict[key] = cache_item

        return self.cache_dict.get(key)


    async def get_keys(self):
        await self.populate_cache()
        return list(self.cache_dict.keys())



    async def flush_cache_item(self, key):
        try:
            db_item = await db.select(self.value_name, self.table_name, self.key_name, key)
        except:
            log.error(f"Cannot retrieve most recent item from database. Trying to flush cache anyway")
            db_item = Error

        cache_item = self.cache_dict.get(key)
        if self.serialize: cache_item = pickle.dumps(cache_item)

        if cache_item == db_item:
            log.debug(f"Cache and DB are already in sync for key '{key}' in table '{self.table_name}'")
        else:
            log.debug(f"Syncing cache to DB for key '{key}' in table '{self.table_name}'")
            sql_data = [[self.key_name, key], [self.value_name, cache_item]]
            
            try:
                if db_item is None:
                    await db.insert(self.table_name, sql_data)
                else:
                    await db.update(self.table_name, sql_data)
            except:
                log.error(f"Cannot write cache to DB. cache operations will not persist")


    async def populate_cache(self):
        try:
            db_dump = await db.select_all(self.table_name)
        except Exception as e:
            log.critical("Cannot read database")
            log.critical("Cache is not populated")
            return

        for row in db_dump:
            data = row[1]
            if self.serialize: data = pickle.loads(data)
            self.cache_dict[row[0]] = data
