"""
Simplified launcher that handles everything automatically.
Double-click this file to run the application.
"""

import sys
import os
import subprocess
import time

def main():
    """Main launcher function."""
    print("=" * 50)
    print("  Sales Forecasting with Prophet")
    print("=" * 50)
    print()
    print("Setting up application...")
    print()
    
    # Change to script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    # Create Streamlit credentials to skip email prompt
    streamlit_dir = os.path.join(os.path.expanduser('~'), '.streamlit')
    os.makedirs(streamlit_dir, exist_ok=True)
    
    # Create credentials file
    credentials_file = os.path.join(streamlit_dir, 'credentials.toml')
    with open(credentials_file, 'w', encoding='utf-8') as f:
        f.write('email = ""\n')
    
    # Create config file
    config_file = os.path.join(streamlit_dir, 'config.toml')
    with open(config_file, 'w', encoding='utf-8') as f:
        f.write('[browser]\n')
        f.write('gatherUsageStats = false\n')
        f.write('\n')
        f.write('[server]\n')
        f.write('headless = false\n')
        f.write('port = 8501\n')
    
    # Check if packages are installed
    try:
        import streamlit
        import pandas
        import prophet
    except ImportError:
        print("Installing required packages...")
        print("This may take a few minutes on first run...")
        # Upgrade pip and setuptools first
        subprocess.check_call([
            sys.executable, '-m', 'pip', 'install', '-q', '--upgrade', 'pip', 'setuptools', 'wheel'
        ])
        # Try to install pyarrow with pre-built wheels first
        try:
            subprocess.check_call([
                sys.executable, '-m', 'pip', 'install', '-q', '--only-binary', ':all:', 'pyarrow'
            ])
        except:
            print("Note: Installing pyarrow (may take longer if building from source)...")
            subprocess.check_call([
                sys.executable, '-m', 'pip', 'install', '-q', 'pyarrow'
            ])
        # Install other packages
        subprocess.check_call([
            sys.executable, '-m', 'pip', 'install', '-q', '-r', 'requirements.txt'
        ])
        print("Packages installed!")
    
    # Set environment
    env = os.environ.copy()
    env['STREAMLIT_BROWSER_GATHER_USAGE_STATS'] = 'false'
    
    print()
    print("Starting application...")
    print("The browser will open automatically.")
    print("To close, press Ctrl+C or close this window.")
    print()
    
    # Run Streamlit - this will open browser automatically
    try:
        subprocess.run([
            sys.executable, '-m', 'streamlit', 'run', 'app.py',
            '--server.headless', 'false',
            '--browser.gatherUsageStats', 'false'
        ], env=env)
    except KeyboardInterrupt:
        print("\nApplication closed.")
    except Exception as e:
        print(f"\nError: {e}")
        input("Press Enter to exit...")

if __name__ == "__main__":
    main()

