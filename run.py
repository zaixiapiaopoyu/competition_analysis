"""
Launch script for the enterprise competitor analysis system.

This script provides a convenient way to start the application.
"""

import subprocess
import sys
from pathlib import Path


def main():
    """Launch the Streamlit application."""
    # Get the path to the main app
    app_path = Path(__file__).parent / "app" / "main.py"
    
    if not app_path.exists():
        print(f"❌ Error: Application file not found at {app_path}")
        sys.exit(1)
    
    # Launch Streamlit
    print("🚀 Launching Enterprise Competitor Analysis System...")
    print("="*70)
    
    try:
        subprocess.run([
            sys.executable,
            "-m",
            "streamlit",
            "run",
            str(app_path),
            "--server.port=8501",
            "--server.address=localhost",
            "--theme.base=light"
        ], check=True)
    except KeyboardInterrupt:
        print("\n\n👋 Application stopped by user")
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Error launching application: {e}")
        sys.exit(1)
    except FileNotFoundError:
        print("\n❌ Error: Streamlit is not installed")
        print("   Install with: pip install streamlit")
        sys.exit(1)


if __name__ == "__main__":
    main()
