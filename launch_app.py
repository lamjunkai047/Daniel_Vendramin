"""
Simple launcher for the Sales Forecasting application.
Double-click this file to run the application.
"""

import sys
import os
import subprocess
import webbrowser
import time

def check_and_install_packages():
    """Check if required packages are installed, install if missing."""
    required_packages = ['streamlit', 'pandas', 'numpy', 'prophet', 'plotly', 'openpyxl']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("Installing required packages...")
        print("This may take a few minutes on first run...")
        try:
            subprocess.check_call([
                sys.executable, '-m', 'pip', 'install', '--quiet', '--upgrade', 'pip'
            ])
            subprocess.check_call([
                sys.executable, '-m', 'pip', 'install', '--quiet', '-r', 'requirements.txt'
            ])
            print("Packages installed successfully!")
        except subprocess.CalledProcessError:
            print("ERROR: Failed to install required packages")
            input("Press Enter to exit...")
            sys.exit(1)

def setup_streamlit_config():
    """Set up Streamlit config to skip email prompt."""
    # Create user's .streamlit directory if it doesn't exist
    streamlit_dir = os.path.join(os.path.expanduser('~'), '.streamlit')
    os.makedirs(streamlit_dir, exist_ok=True)
    
    # Create credentials file to skip email prompt (always overwrite to ensure it's set)
    credentials_file = os.path.join(streamlit_dir, 'credentials.toml')
    with open(credentials_file, 'w', encoding='utf-8') as f:
        f.write('# Streamlit credentials\n')
        f.write('email = ""\n')
    
    # Also create/update config.toml in user directory
    config_file = os.path.join(streamlit_dir, 'config.toml')
    with open(config_file, 'w', encoding='utf-8') as f:
        f.write('[browser]\n')
        f.write('gatherUsageStats = false\n')
        f.write('\n')
        f.write('[server]\n')
        f.write('headless = false\n')
        f.write('runOnSave = true\n')
        f.write('port = 8501\n')

def main():
    """Main launcher function."""
    print("=" * 50)
    print("  Sales Forecasting with Prophet")
    print("=" * 50)
    print()
    print("Starting application...")
    print("Please wait, this may take a moment...")
    print()
    
    # Change to script directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # Set up Streamlit config to skip email prompt
    setup_streamlit_config()
    
    # Check and install packages
    check_and_install_packages()
    
    # Set environment variables to skip email prompt
    os.environ['STREAMLIT_BROWSER_GATHER_USAGE_STATS'] = 'false'
    os.environ['STREAMLIT_THEME_BASE'] = 'light'
    
    # Run Streamlit with flags to skip email and open browser
    print("The application will open in your browser automatically.")
    print("To close the application, close this window or press Ctrl+C")
    print()
    
    try:
        # Use the wrapper script to ensure email prompt is skipped
        wrapper_script = os.path.join(os.path.dirname(__file__), 'run_streamlit.py')
        if os.path.exists(wrapper_script):
            process = subprocess.Popen([
                sys.executable, wrapper_script
            ], env=os.environ.copy())
        else:
            # Fallback to direct streamlit call
            process = subprocess.Popen([
                sys.executable, '-m', 'streamlit', 'run', 'app.py',
                '--server.headless', 'false',
                '--browser.gatherUsageStats', 'false',
                '--server.port', '8501'
            ], env=os.environ.copy())
        
        # Wait for the process
        process.wait()
    except KeyboardInterrupt:
        print("\nApplication closed.")
    except Exception as e:
        print(f"ERROR: {str(e)}")
        input("Press Enter to exit...")

if __name__ == "__main__":
    main()

