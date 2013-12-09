from app import app
import os
from app import set_up_mongo

set_up_mongo()
port = int(os.environ.get('PORT', 5000))
app.run(host='0.0.0.0', port=port)
