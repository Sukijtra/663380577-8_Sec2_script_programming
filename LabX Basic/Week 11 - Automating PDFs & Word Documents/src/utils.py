# document-automator/src/utils.py
import logging
import os
# Configure basic logging for the utility module
logging.basicConfig(level=logging.INFO, format=&#39;%(asctime)s - %(levelname)s - %(message)s&#39;)
def setup_logging(name, level=logging.INFO):

&quot;&quot;&quot;Sets up a logger for specific modules.&quot;&quot;&quot;
logger = logging.getLogger(name)
logger.setLevel(level)
if not logger.handlers: # Prevent adding multiple handlers if called multiple times
ch = logging.StreamHandler()
formatter = logging.Formatter(&#39;%(asctime)s - %(name)s - %(levelname)s - %(message)s&#39;)
ch.setFormatter(formatter)
logger.addHandler(ch)
return logger
def ensure_directory_exists(path):
&quot;&quot;&quot;Ensures that a directory exists, creating it if necessary.&quot;&quot;&quot;
try:
os.makedirs(path, exist_ok=True)
logging.info(f&quot;Directory ensured: {path}&quot;)
except OSError as e:
logging.error(f&quot;Error creating directory {path}: {e}&quot;)
raise