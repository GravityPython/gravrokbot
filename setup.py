from setuptools import setup, find_packages

setup(
    name="gravrokbot",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "pyautogui==0.9.54",
        "opencv-python==4.8.0.76",
        "pytesseract==0.3.10",
        "PyQt6==6.5.2",
        "transitions==0.9.0",
        "numpy==1.24.3",
        "pillow==10.0.0",
        "pyscreeze==0.1.29",
        "python-dateutil==2.8.2",
        "logging-colorlog==6.0.0"
    ],
    entry_points={
        'console_scripts': [
            'gravrokbot=gravrokbot.gravrokbot:main',
        ],
    },
    author="Jalel Gatti",
    author_email="",
    description="Bot for automating actions in Rise of Kingdoms game",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Microsoft :: Windows",
        "Topic :: Games/Entertainment",
    ],
    python_requires='>=3.9',
    include_package_data=True,
) 