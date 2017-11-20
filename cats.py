import platform
import os
from catw import create_app, db
from catw.db_model import User
from waitress import serve


# Run Application
if __name__ == "__main__":
    if platform.node() == "zeegeus":
        app = create_app('production')
    else:
        app = create_app('development')

    with app.app_context():
        db.create_all()
        if User.query.filter_by(username='dirk').first() is None:
            User.register('dirk', 'olse')
        if platform.node() == "zeegeus":
            serve(app, listen='127.0.0.1:8001')
        else:
            # app.run(host="0.0.0.0", port=5012, debug=True)
            app.run()
