import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel
from PyQt6.QtCore import Qt

def main():
    """
    YiBoClient Entry Point
    """
    app = QApplication(sys.argv)

    # Basic Window Setup for testing environment
    window = QMainWindow()
    window.setWindowTitle("YiBoClient - Environment Check")
    window.setGeometry(100, 100, 800, 600)

    # Central Widget
    label = QLabel("YiBoClient Development Environment\n\nFramework: PyQt6\nStatus: Initialized", window)
    label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    window.setCentralWidget(label)

    window.show()

    # Check dependencies
    print("Checking dependencies...")
    try:
        import vlc
        print(f"VLC Module: {vlc.__version__} (OK)")
    except ImportError:
        print("VLC Module: Not Found (Warning: Install python-vlc)")
    except OSError:
        print("VLC Module: Found but LibVLC not loaded (Warning: Ensure VLC is installed on system)")

    try:
        import requests
        print(f"Requests: {requests.__version__} (OK)")
    except ImportError:
        print("Requests: Not Found")

    sys.exit(app.exec())

if __name__ == "__main__":
    main()
