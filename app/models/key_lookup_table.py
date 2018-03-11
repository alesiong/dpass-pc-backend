import binascii

from Crypto import Random

from app import db


class KeyLookupTable(db.Model):
    __tablename__ = "key_lookup_table"

    key = db.Column(db.String(16), primary_key=True)
    meta_data = db.Column(db.Text, nullable=False)
    hidden = db.Column(db.Boolean, nullable=False)

    def __init__(self, **kwargs):
        super(KeyLookupTable, self).__init__(**kwargs)

    def __repr__(self):
        return '<KeyLookupTable {0}>'.format(self.key)

    @classmethod
    def new_entry(cls, metadata: str):
        """
        Add new entry with random key
        :param metadata: Encrypted metadata (in base64 string)
        :return:
        """
        while True:
            key = binascii.hexlify(Random.get_random_bytes(8)).decode()
            if cls.query.filter_by(key=key).count():
                break

        entry = cls(key=key, meta_data=metadata, hidden=False)
        db.session.add(entry)
        db.session.commit()
        return entry
