# mig - SQLAlchemy migrations
# Copyright 2012  mig contributors.  See NOTICE
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import sys


def simple_printer(string):
    """
    Prints a string, but without an auto \n at the end.

    Useful for places where we want to dependency inject for printing.
    """
    sys.stdout.write(string)
    sys.stdout.flush()
