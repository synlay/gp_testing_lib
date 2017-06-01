#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_gp_testing_lib
----------------------------------

Tests for `gp_testing_lib` module.
"""

import pytest


from gp_testing_lib import gp_testing_lib


@pytest.fixture
def response():
    """Sample pytest fixture.
    See more at: http://doc.pytest.org/en/latest/fixture.html
    """
    # import requests
    # return requests.get('https://github.com/audreyr/cookiecutter-pypackage')


def test_content(response):
    """Sample pytest test function with the pytest fixture as an argument.
    """
    # from bs4 import BeautifulSoup
    # assert 'GitHub' in BeautifulSoup(response.content).title.string
