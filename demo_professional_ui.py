#!/usr/bin/env python3
"""
Professional UI Demo Script
Quick test of the enhanced interface without full MCP dependencies
"""

import subprocess
import sys
import os

def main():
    """Run the professional interface demo"""
    print("🚀 Starting Professional AI Customer Service Interface Demo")
    print("=" * 60)
    
    # Check if we're in the right directory
    if not os.path.exists("streamlit_app.py"):
        print("❌ Error: streamlit_app.py not found in current directory")
        print("Please run this script from the capstone project directory")
        return
    
    print("✅ Found streamlit_app.py")
    print("✅ Professional interface enhancements loaded")
    print("✅ Ready to launch!")
    print()
    
    print("🎨 Professional UI Features:")
    print("  • Modern typography with Inter font")
    print("  • Professional color schemes and gradients")
    print("  • Enhanced chat interface with avatars")
    print("  • Interactive navigation cards")
    print("  • Real-time status indicators")
    print("  • Responsive design for all devices")
    print("  • Smooth hover animations and transitions")
    print()
    
    print("🚀 Launching Streamlit application...")
    print("The professional interface will open in your browser shortly!")
    print()
    print("Note: If MCP agent fails to initialize, the interface will still")
    print("demonstrate all professional UI features in demo mode.")
    
    try:
        # Launch streamlit
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", 
            "streamlit_app.py",
            "--server.headless", "false",
            "--server.port", "8501",
            "--browser.gatherUsageStats", "false"
        ])
    except KeyboardInterrupt:
        print("\n👋 Demo ended by user")
    except Exception as e:
        print(f"\n❌ Error launching Streamlit: {e}")
        print("You can manually run: streamlit run streamlit_app.py")

if __name__ == "__main__":
    main()