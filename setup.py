import io

from setuptools import setup

with io.open("README.md", "rt", encoding="utf8") as f:
    readme = f.read()

setup(
    name="restsftp",
    version="1.0.0",
    url="https://github.com/rodolfocugler/python-rest-sftp",
    license="Apache 2.0",
    maintainer="Rodolfo Cugler",
    maintainer_email="rodolfocugler@outlook.com",
    description="Rest API module to connect in a Rest-SFTP server",
    long_description=readme,
    packages=['rest_sftp'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'setuptools~=41.2.0',
        'requests~=2.25.1',
    ]
)
