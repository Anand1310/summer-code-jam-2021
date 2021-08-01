from distutils.core import setup

setup(
    name="maze-gitb",  # temp name
    packages=["maze-gitb"],
    version="0.1",
    license="MIT",
    description="A maze game that required users to think inside the box to win",
    author="Benevolent Bonobos",
    author_email="jasonho1308@gmail.com",
    url="https://github.com/Anand1310/summer-code-jam-2021",
    download_url="https://github.com/Anand1310/summer-code-jam-2021/archive/v_01.tar.gz",
    keywords=["game", "maze", "box", "think inside the box", "sound", "3d-sound"],
    install_requires=[
        'blessed',
        'numpy',
        'pyperclip',
        'PyTweening',
        'PyOpenAL',
    ],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: Unix",
        "Programming Language :: Python :: 3.8",
        "Topic :: Games/Entertainment :: Puzzle Games",
    ],
)
