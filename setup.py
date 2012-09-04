# mig -- SQLAlchemy migrations
# Copyright (C) 2012 mig contributors.  See AUTHORS.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from setuptools import setup, find_packages

import os

READMEFILE = 'README.rst'

long_desc = None

try:
    long_desc = open(READMEFILE).read()
except:
    print('ERROR: Can\'t generate long description')

setup(
        name='mig',
        version='0.0.3',
        packages=find_packages(),
        install_requires=[
            'setuptools',
            'sqlalchemy',
            'sqlalchemy-migrate'],
        author='mig contributors',
        author_email='joar@talka.tv',
        long_description=long_desc)
