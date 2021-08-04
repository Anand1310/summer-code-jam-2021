import setuptools
from setuptools import setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()


setup(
    name="maze_gitb",  # temp name
    version="1.0.2",
    license="MIT",
    description="A maze game that required users to think inside the box to win",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Benevolent Bonobos",
    author_email="jasonho1308@gmail.com",
    url="https://github.com/Anand1310/summer-code-jam-2021",
    project_urls={
        "Bug Tracker": "https://github.com/Anand1310/summer-code-jam-2021/issues",
    },
    download_url="https://github.com/Anand1310/summer-code-jam-2021/archive/v1.0.2.tar.gz",
    keywords=["game", "maze", "box", "think inside the box", "sound", "3d-sound"],
    install_requires=[
        'blessed',
        'numpy',
        'PyOpenAL',
    ],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: Unix",
        "Programming Language :: Python :: 3",
        "Topic :: Games/Entertainment :: Puzzle Games",
    ],
    entry_points={
        'console_scripts': [
            'maze_gitb = maze_gitb.main:main'
        ]
    },
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    include_package_data=True,
    python_requires=">=3.8.6",
)
