from app import db


class KeyLookupTable(db.Model):
    __tablename__ = "key_lookup_table"

    key = db.Column(db.String(64), primary_key=True)
    meta_data = db.Column(db.Text, nullable=False)
    hidden = db.Column(db.Boolean, nullable=False)

    def __init__(self, **kwargs):
        super(KeyLookupTable, self).__init__(**kwargs)

    def __repr__(self):
        return '<KeyLookupTable {0}>'.format(self.key)

    @classmethod
    def new_entry(cls, key, meta_data):
        entry = cls(key=key, meta_data=meta_data, hidden=False)
        db.session.add(entry)
        db.sessionl.commit()
