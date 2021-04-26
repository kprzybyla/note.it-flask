from setuptools import setup


def main():
    with open("requirements.in") as handle:
        install_requires = handle.read()

    setup(
        include_package_data=True,
        install_requires=install_requires,
    )


if __name__ == "__main__":
    main()
