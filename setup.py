from setuptools import setup

settings = {
    "name": "AutoTestnator",
    "version": "1.6",
    "description": "A tool to automatically test and replicate such tests on demand for (any) websites.",
    "url": "https://github.com/PvMDragonic/AutoTestnator",
    "author": "João Pedro Droval",
    "license": "Apache License 3.0",
    "python_requires" : ">=3.9.10",
    "install_requires": [
        "SSIM-PIL>=1.0.14",
        "numpy>=1.23.1",
        "screeninfo>=0.8.1",
        "h5py>=3.7.0",
        "Pillow>=9.2.0",
        "pynput>=1.7.6"
    ],
    "packages": [
        "AutoTestnator"
    ]
}

setup(**settings)