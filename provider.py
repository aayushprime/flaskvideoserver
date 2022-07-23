import abc, os, time
from distutils.command.upload import upload


class StorageProvider(metaclass=abc.ABCMeta):
    """
    ABC for storage providers.
    A storage provider is like a KV store. It will store a identifier and a related file.
    """

    @abc.abstractmethod
    def __init__(self):
        """
        Do setup for storage provider.
        """
        pass

    @abc.abstractmethod
    def get_item(self, item_id):
        """
        Get a stored item
        """
        pass

    @abc.abstractmethod
    def set_item(self, item_id, item):
        """
        Store a new item
        """
        pass

    @abc.abstractmethod
    def search(self, query):
        """
        Search for items
        """
        pass

    @abc.abstractmethod
    def remove(self, id):
        """
        Search for items
        """
        pass


class LocalStorageProvider(StorageProvider):
    """
    Id is path in this case
    """

    def __init__(self, db):
        self.db = db

    def get_item(self, item_id):
        fp = "./video/" + item_id
        if os.path.exists(fp):
            return fp
        else:
            return None

    def set_item(self, item_id, item):
        basepath = os.path.dirname(__file__)
        save_path = os.path.join(basepath, "video", item_id)
        item.save(save_path)
        self.db.execute(
            f'INSERT INTO VIDEO_INDEX (IDENTIFIER, PATH, TIMESTAMP) VALUES ("{str(item_id)}", "{save_path}", {time.time()});'
        )
        self.db.commit()
        return save_path

    def search(self, query=None, timestamp=None):
        """
        Return all items containing query in their identifier and uploaded after timestamp
        """
        if query is None and timestamp is None:
            cursor = self.db.execute("SELECT IDENTIFIER FROM VIDEO_INDEX")
        elif timestamp is None:
            cursor = self.db.execute(
                f"SELECT IDENTIFIER FROM VIDEO_INDEX WHERE IDENTIFIER LIKE '%{query}%'"
            )
        elif query is None:
            cursor = self.db.execute(
                f"SELECT IDENTIFIER FROM VIDEO_INDEX WHERE TIMESTAMP > '{timestamp}'"
            )
        else:
            cursor = self.db.execute(
                f"SELECT IDENTIFIER FROM VIDEO_INDEX WHERE IDENTIFIER LIKE '%{query}%' AND TIMESTAMP > '{timestamp}'"
            )
        return cursor.fetchall()

    def remove(self, id):
        os.remove(id)
        self.db.execute(f"DELETE FROM VIDEO_INDEX WHERE IDENTIFIER = '{id}'")
        self.db.commit()


class S3BucketStorageProvider(StorageProvider):
    pass
