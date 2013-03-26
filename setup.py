from distutils.core import setup
from setuptools import find_packages
from setuptools.command.test import test as TestCommand
import sys
import os.path

PACKAGE = "lite_mms"
NAME = "lite-mms"
DESCRIPTION = ""
AUTHOR = ""
AUTHOR_EMAIL = ""
URL = ""
VERSION = __import__(PACKAGE).__version__
DOC = __import__(PACKAGE).__doc__


class PyTest(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        import pytest

        errno = pytest.main(self.test_args)
        sys.exit(errno)

setup(
    name=NAME,
    version=VERSION,
    long_description=__doc__,
    description=DESCRIPTION,
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    license="",
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=open("requirements.txt").readlines(),
    scripts=['lite_mms/bin/lite-mms-admin.py'],
    data_files=[(os.path.join(sys.prefix, "share/lite-mms"),
                 ['lite_mms/data/readme.txt', 'lite_mms/data/config.py.sample',
                  'lite_mms/data/lite-mms-blt', 'lite_mms/data/lite-mms']),
                (os.path.join(sys.prefix, "share/lite-mms/tools"),
                 ['lite_mms/tools/build_db.py',
                  "lite_mms/tools/set_blt_as_service.py",
                  "lite_mms/tools/set_portal_as_service.py",
                  "lite_mms/tools/add_uwsgi_app.sh", 
                  'lite_mms/tools/make_test_data.py'])],
    tests_require=['pytest'],
    cmdclass={'test': PyTest},
    entry_points={
        "distutils.commands": [
            "make_test_data = lite_mms.tools.make_test_data:InitializeTestDB",
        ]
    }

)
