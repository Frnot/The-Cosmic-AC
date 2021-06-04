# Abstract class that caches DB data in memory
# Cache is automatically maintained
# Use this class instead of accessing database manually

import db
import logging
log = logging.getLogger(__name__)

class DBCache:
    def __init__(self, table_name, key_name, value_name):
        self.cache_dict = {}
        self.table_name = table_name
        self.key_name = key_name
        self.value_name = value_name



    async def add_or_update(self, key, value):
        if self.cache_dict.get(key) != value:
            if self.cache_dict.get(key) is None:
                log.debug(f"Adding value for {key} in {self.table_name}")
            else:
                log.debug(f"Changing {key} in {self.table_name}")
            self.cache_dict[key] = value
        
        await self.flush_cache_item_to_db(key)


    async def remove(self, key):
        if await self.get(key) is None:
            log.debug(f"Cannot remove item with key '{key}' as it doesnt not exist in db table '{self.table_name}'")
            return
        else:
            log.debug(f"Removing row with key '{self.key_name}'='{key}' in table '{self.table_name}'")
            self.cache_dict.pop(key)
            await db.delete(self.table_name, [self.key_name, key])


    async def get(self, key):
        if self.cache_dict.get(key) is None:
            cache_item = await db.select(self.value_name, self.table_name, self.key_name, key)

            if cache_item is None:
                log.debug(f"Could not find {self.value_name} in table {self.table_name} for {self.key_name} = {key}")
                return None
            else:
                log.debug(f"Found {self.value_name} in table {self.table_name} for {self.key_name} = {key}. Loading into cache")
                self.cache_dict[key] = cache_item
        
        return self.cache_dict.get(key)


    async def flush_cache_item_to_db(self, key):
        cache_item = self.cache_dict.get(key)
        db_item = await db.select(self.value_name, self.table_name, self.key_name, key)

        if cache_item == db_item:
            log.debug(f"Cache and DB are already in sync for key '{key}' in table '{self.table_name}'")
        else:
            log.debug(f"Syncing cache to DB for key '{key}' in table '{self.table_name}'")
            sql_data = [[self.key_name, key], [self.value_name, cache_item]]
            if db_item is None:
                await db.insert(self.table_name, sql_data)
            else:
                await db.update(self.table_name, sql_data)