===========================
mig - SQLAlchemy migrations
===========================

mig ([M]ediaGoblin [i]s [G]reat!) was first written by 
`Christopher Allan Webber <http://dustycloud.org>`_ for
`GNU MediaGoblin <http://mediagoblin.org>`_.

Since then, `Joar Wandborg <http://wandborg.se>`_ has extracted the essentials
of the functionality from MediaGoblin and into a separate package which's README
you are currently reading.


---------------
Init migrations
---------------

Either run ``mig.run(engine, name, models, migrations)`` or add the ``mig.models.MigrationData`` table manually.

.. note::

    If your database is already populated and there are no migration version rows in the MigrationData table, ``mig.run()`` will fail.

If you already have a populated database you'll need to create a ``MigrationData(name='migrations_handle', version=0)`` row for your migrations in the MigrationData table, otherwise mig will try to initiate the database.


===============
Example setup
===============


----------------
Create migration
----------------

.. code-block:: python

    from mig import RegisterMigration

    from sqlalchemy import MetaData, Table, Column, Integer, Unicode, DateTime, \
            ForeignKey

    MIGRATIONS = {}


    @RegisterMigration(1, MIGRATIONS)
    def create_site_table(db_conn):
        metadata = MetaData(bind=db_conn.bind)

        user_table = Table('user', metadata, autoload=True,
                autoload_with=db_conn.bind)

        site_table = Table('site', metadata,
                Column('id', Integer, primary_key=True),
                Column('domain', Unicode),
                Column('owner_id', Integer, ForeignKey(user_table.columns['id'])))

        site_table.create()

        db_conn.commit()


    @RegisterMigration(2, MIGRATIONS)
    def item_add_site_id(db_conn):
        metadata = MetaData(bind=db_conn.bind)

        item_table = Table('item', metadata, autoload=True)
        site_table = Table('site', metadata, autoload=True)

        site_id_col = Column('site_id', Integer, ForeignKey(
            site_table.columns['id']))

        site_id_col.create(item_table)

        db_conn.commit()


---------------
Register models
---------------

.. code-block:: python

    import bcrypt

    from datetime import datetime

    from migrate import changeset

    from talkatv import db


    class User(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        username = db.Column(db.String(60), unique=True)
        email = db.Column(db.String(255), unique=True)
        password = db.Column(db.String(60))

        def __init__(self, username, email, password=None, openid=None):
            self.username = username
            self.email = email

            if password:
                self.set_password(password)

            if openid:
                self.openid = openid

        def __repr__(self):
            return '<User {0}>'.format(self.username)

        def set_password(self, password):
            self.password = bcrypt.hashpw(password, bcrypt.gensalt())

        def check_password(self, password):
            return bcrypt.hashpw(password, self.password) == self.password


    class OpenID(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        url = db.Column(db.String())
        created = db.Column(db.DateTime)

        user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
        user = db.relationship('User',
                backref=db.backref('openids', lazy='dynamic'))

        def __init__(self, user, url):
            self.created = datetime.utcnow()
            self.user = user
            self.url = url


    class Item(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        title = db.Column(db.String())
        url = db.Column(db.String(), unique=True)
        created = db.Column(db.DateTime)

        site_id = db.Column(db.Integer, db.ForeignKey('site.id'))
        site = db.relationship('Site',
                backref=db.backref('items', lazy='dynamic'))

        def __init__(self, url, title, site=None):
            if site:
                self.site = site

            self.title = title
            self.url = url

            self.created = datetime.utcnow()

        def __repr__(self):
            return '<Item {0} ({1})>'.format(
                    self.url,
                    self.site.owner.username if self.site else None)

        def as_dict(self):
            me = {
                    'id': self.id,
                    'title': self.title,
                    'url': self.url,
                    'created': self.created.isoformat()}
            if self.site:
                me.update({'owner': self.site.owner.id})

            return me


    class Site(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        created = db.Column(db.DateTime)
        domain = db.Column(db.String)

        owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
        owner = db.relationship('User',
                backref=db.backref('sites', lazy='dynamic'))

        def __init__(self, owner, domain):
            self.owner = owner
            self.domain = domain

            self.created = datetime.utcnow()

        def __repr__(self):
            return '<Site {0} ({1})>'.format(
                    self.domain,
                    self.owner.username)


    class Comment(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        created = db.Column(db.DateTime)
        text = db.Column(db.String())

        item_id = db.Column(db.Integer, db.ForeignKey('item.id'))
        item = db.relationship('Item',
                backref=db.backref('comments', lazy='dynamic'))

        user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
        user = db.relationship('User',
                backref=db.backref('comments', lazy='dynamic'))

        def __init__(self, item, user, text):
            self.item = item
            self.user = user
            self.text = text

            self.created = datetime.utcnow()

        def __repr__(self):
            return '<Comment {0} ({1})>'.format(
                    self.text[:25] + ('...' if len(self.text) > 25 else ''),
                    self.user.username)

        def as_dict(self):
            me = {
                    'id': self.id,
                    'item': self.item.id,
                    'user_id': self.user.id,
                    'username': self.user.username,
                    'text': self.text,
                    'created': self.created.isoformat()}
            return me

    MODELS = [
            User,
            Comment,
            Item,
            OpenID,
            Site]


--------------
Run migrations
--------------

.. code-block:: python

    from mig import run
    from mig.models import MigrationData

    from yourapp import db
    from yourapp.models import MODELS
    from yourapp.migrations import MIGRATIONS



    def check_or_create_mig_data():
        if not db.engine.dialect.has_table(db.session, 'mig__data'):
            # Create migration table
            MigrationData.__table__.create(db.engine)

            # Create the first migration, so that mig doesn't init.
            migration = MigrationData(name=u'__main__', version=0)
            db.session.add(migration)
            db.session.commit()


    if __name__ == '__main__':
        if db.engine.dialect.has_table(db.session, 'user'):
            # The DB is already populated, check if migrations are active,
            # otherwise create the migration data table
            check_or_create_mig_data()

        run(db.engine, u'__main__', MODELS, MIGRATIONS)
