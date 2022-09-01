import os
import click
from chat import create_app, sio
from chat.utils import load_categories
from chat.models import db, Room

app = create_app()


@app.cli.group()
def translate():
    """Flask-Babel cli commands."""
    pass
    
    
@translate.command()
@click.argument("lang")
def init(lang):
    """Flask-Babel command to initialize new language.
    
    :param lang: new app language.
    """
    if os.system("pybabel extract -F babel.cfg -k _l -o messages.pot ."):
        raise RuntimeError("Extract command failed.")
    if os.system("pybabel init -i messages.pot -d chat/translations -l " + lang):
        raise RuntimeError(f"Init {lang} language command failed.")
    os.remove("messages.pot")
    
    
@translate.command()
def update():
    """Flask-Babel command to update all languages."""
    if os.system("pybabel extract -F babel.cfg -k _l -o messages.pot ."):
        raise RuntimeError("Extract command failed.")
    if os.system("pybabel update -i messages.pot -d chat/translations"):
        raise RuntimeError("Update command failed.")
    os.remove("messages.pot")
    
    
@translate.command()
def compile():
    """Flask-Babel command to Compile all languages."""
    if os.system("pybabel compile -d chat/translations"):
        raise RuntimeError("Compile command failed.")
 
 
@app.cli.command()
@click.argument("test_names", nargs=-1)
def test(test_names):
    import unittest
    if test_names:
        tests = unittest.TestLoader().loadTestsFromNames(test_names)
    else:
        tests = unittest.TestLoader().discover("tests")
    unittest.TextTestRunner(verbosity=2).run(tests)
  
  
@app.cli.command()
@click.argument("categories", nargs=-1)
def insert_categories(categories):
    load_categories(categories)
    
    
@app.cli.command()
@click.argument("room_id", nargs=1)
def drop_room(room_id):
    room = Room.query.get(room_id)
    if room is not None:
        db.session.delete(room)
        db.session.commit()
    
    
if __name__ == "__main__":
    app.run()
    