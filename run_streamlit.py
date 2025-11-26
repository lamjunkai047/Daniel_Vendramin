"""
Wrapper script to run Streamlit without email prompt.
This is called by the launcher to ensure email prompt is skipped.
"""

import sys
import os
import subprocess

# Ensure credentials file exists before running Streamlit
streamlit_dir = os.path.join(os.path.expanduser('~'), '.streamlit')
os.makedirs(streamlit_dir, exist_ok=True)

credentials_file = os.path.join(streamlit_dir, 'credentials.toml')
with open(credentials_file, 'w', encoding='utf-8') as f:
    f.write('# Streamlit credentials\n')
    f.write('email = ""\n')

# Set environment variables
os.environ['STREAMLIT_BROWSER_GATHER_USAGE_STATS'] = 'false'

# Run Streamlit
subprocess.run([
    sys.executable, '-m', 'streamlit', 'run', 'app.py',
    '--server.headless', 'false',
    '--browser.gatherUsageStats', 'false',
    '--server.port', '8501'
])

