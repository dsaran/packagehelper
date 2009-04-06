from test.framework import TestCase
from test import mock

from package.domain.repository import Repository, ScmType
from package.config import Repositories

expected_data = """- {active: true, module: module, root: root, type: 1}
"""

class RepositoryConfigTests(TestCase):
    def setUp(self):
        self.repositories = Repositories()
        self.repositories.loader = mock.Mock()

    def testSaveConfig(self):
        """ Repositories should be saved correctly"""
        data = [Repository('root', 'module', ScmType.CVS, True)]
        self.repositories.save(data)
        arguments = self.repositories.loader.write_config_file.call_args
        self.assertEquals(expected_data, arguments[0][0]) 

    def testLoadConfig(self):
        """ Repositories should be loaded correctly"""
        data = [Repository('root', 'module', ScmType.CVS, True)]
        self.repositories.loader.read_config_file.return_value = expected_data

        loaded_data = self.repositories.load()

        self.assertEquals(data, loaded_data)

