from setuptools import setup, find_packages

setup(
    name="gravrokbot",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        'pyqt6>=6.8.1',
        'numpy>=1.21.0',
        'pyautogui>=0.9.53',
        'opencv-python>=4.7.0',
        'transitions>=0.9.0',
        'pytesseract>=0.3.13',
        'pillow>=11.1.0',
        'colorlog>=6.7.0'
    ],
    entry_points={
        'console_scripts': [
            'gravrokbot=gravrokbot.gravrokbot:main',
        ],
    },
    author="Gravity",
    author_email="",
    description="Rise of Kingdoms automation bot",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/gravrokbot",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Microsoft :: Windows",
        "Topic :: Games/Entertainment",
    ],
    python_requires='>=3.8',
    include_package_data=True,
) 