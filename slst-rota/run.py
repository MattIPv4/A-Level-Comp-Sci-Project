from app import app
from app.utils import Utils

Utils.install_reqs()
app.run(host='127.0.0.1', port=8080, debug=True)
