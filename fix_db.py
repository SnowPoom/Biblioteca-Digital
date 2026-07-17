import sqlite3
import os

db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'db.sqlite3')
conn = sqlite3.connect(db_path)
c = conn.cursor()
c.execute("DELETE FROM django_migrations WHERE app='materiales' AND name='0013_alter_invitacioncoleccion_unique_together_and_more'")
c.execute("DELETE FROM django_migrations WHERE app='materiales' AND name='0014_alter_invitacioncoleccion_unique_together_and_more'")
conn.commit()
conn.close()
