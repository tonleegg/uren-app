from setuptools import setup

APP = ["begroeting_gui.py"]
OPTIONS = {
    "argv_emulation": False,
    "plist": {
        "CFBundleName": "Begroeting",
        "CFBundleDisplayName": "Begroeting",
        "CFBundleIdentifier": "nl.begroeting.app",
        "CFBundleVersion": "1.0.0",
        "LSBackgroundOnly": False,
    },
}

setup(
    app=APP,
    options={"py2app": OPTIONS},
    setup_requires=["py2app"],
)
