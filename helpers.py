def calculate_price(size, length):
    """
    Price calculation logic as defined in the requirements.
    """
    price = 5 if size < 500 else 12.5
    price += 12.5 if length < 6 * 60 + 18 else 25
    return price


def allowed_filetype(filename):
    allowed = ["mkv", "mp4"]
    return filename.rsplit(".", 1)[1] in allowed


class UploadingFileEntry(object):
    """
    Context manager for recording files that are being uploaded.
    """

    def __init__(self, filesize, db, id):
        """
        filesize: size of file being uploaded
        db: database connection
        id: unique id for this file
        """
        self.filesize = filesize
        self.db = db
        self.id = id

    def __enter__(self):
        self.db.execute(
            f"INSERT INTO ACTIVE_UPLOADS (FILESIZE, UUID) VALUES ('{self.filesize}', '{self.id}')"
        )
        self.db.commit()

    def __exit__(self, type, value, traceback):
        self.db.execute(f"DELETE FROM ACTIVE_UPLOADS WHERE UUID = '{self.id}'")
        self.db.commit()


def get_uploading_files(db):
    """
    Return a list of files that are being uploaded.
    """
    return [
        {"filesize": x[1], "uuid": x[2]}
        for x in db.execute("SELECT * FROM ACTIVE_UPLOADS").fetchall()
    ]
