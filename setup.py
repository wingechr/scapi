from setuptools import find_packages, setup

if __name__ == "__main__":

    with open("README.md", encoding="utf-8") as file:
        long_description = file.read()

    setup(
        packages=find_packages(),
        keywords=[],
        install_requires=["click", "coloredlogs"],
        name="scapi",
        description="TODO",
        long_description=long_description,
        long_description_content_type="text/markdown",
        version="0.0.1",
        author="Christian Winger",
        author_email="c@wingechr.de",
        url="https://github.com/wingechr/scapi",
        platforms=["any"],
        license="Public Domain",
        project_urls={"Bug Tracker": "https://github.com/wingechr/scapi"},
        classifiers=[
            "Programming Language :: Python :: 3",
            "Programming Language :: Python :: 3.8",
            "Programming Language :: Python :: 3.9",
            "Programming Language :: Python :: 3.10",
            "License :: CC0 1.0 Universal (CC0 1.0) Public Domain Dedication",
            "Operating System :: OS Independent",
        ],
        entry_points={"console_scripts": ["scapi-build = scapi.build:main"]},
        package_data={
            "test": ["example/**"],
            "scapi": ["schema/**", "shared/**", "shared/doc/**"],
        },
    )
