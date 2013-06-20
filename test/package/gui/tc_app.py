from test.framework import TestCase
from test.mock import Mock
from test.package.gui.util import refresh_gui, display

from kiwi.ui.delegates import GladeSlaveDelegate

from package.domain.pack import Package
from package.domain.file import File, InstallScript
from package.ui.gui import PackageProcessorGUI
from package.ui.listslave import FileListSlave, MainDataStep, ReleaseNotesStep, ManageFilesStep, ProcessorThread

class AppGuiTests(TestCase):

    def _testFilelistAttach(self):
        """ Given I create a the App a Filelist should be attached"""
        self.given_i_have_an_app_instance()

        self.assertTrue(hasattr(self.app, 'filelist'), "No filelist attached to app")

    def given_i_have_an_app_instance(self):
        PackageProcessorGUI._load_repos = lambda s: []
        self.app = PackageProcessorGUI()

class MainDataStepTests(TestCase):

    def setUp(self):
        self.model = Package()
        load_repos = Mock()
        MainDataStep._load_repos = load_repos
        self.main_step = MainDataStep(model=self.model)

        # Context
        self.repositories = []
        self.tags = []
        self.selected_repository = None
        self.removed_repository = None
        self.selected_tag = None
        self.removed_tag = None

    def testAddRepository(self):
        """When a repository is added to list it should be added to model"""
        repo = self.when_i_add_a_repository()

        self.then_it_should_add_repository_to_model(repo)

    def testRemoveRepository(self):
        """When a repository is removed it should be removed from model"""
        self.given_i_have_n_repositories(4)

        self.given_i_have_selected_repository(3)

        self.when_i_remove_repository()

        self.then_it_should_remove_repository_from_model()

    def testRemoveRepositoryFromEmptyList(self):
        """When I click remove_repository button and the list is empty it should be ignored"""
        self.given_i_have_n_repositories(0)

        self.when_i_remove_repository()

        self.then_it_should_do_nothing()


    def testAddTag(self):
        """When a tag is added to list it should be added to model"""
        repo = self.when_i_add_a_tag()

        self.then_it_should_add_tag_to_model(repo)

    def testRemoveTag(self):
        """When a tag is removed it should be removed from model"""
        self.given_i_have_n_tags(4)

        self.given_i_have_selected_tag(3)

        self.when_i_remove_tag()

        self.then_it_should_remove_tag_from_model()

    def testRemoveTagFromEmptyList(self):
        """When I click remove_repository button and the list is empty it should be ignored"""
        self.given_i_have_n_tags(0)

        self.when_i_remove_tag()

        self.then_it_should_do_nothing()

    def testPackageNameProxy(self):
        """When I change content of package entry it should update the model"""
        self.when_i_change_package_entry()

        self.then_it_should_change_model_name()

    def testPathProxy(self):
        """When I change content of path entry it should update the model"""
        self.when_i_change_path_entry()

        self.then_it_should_change_model_path()

    def testCheckoutProxyDefaultValue(self):
        """When I enter main step model's checkout property should be set"""
        self.assertTrue(self.model.checkout, "Default value not set")

    def testCheckoutProxy(self):
        """When I check the checkout button model's checkout property should be set"""
        self.main_step.checkout_chk.set_active(False)
        self.assertFalse(self.model.checkout, "Checkout value not changed")

    def testProcessProxyDefaultValue(self):
        """When I enter main step model's process property should be set"""
        self.assertTrue(self.model.process, "Default value not set")

    def testProcessProxy(self):
        """When I check the process button model's process property should be set"""
        self.main_step.process_chk.set_active(False)
        self.assertFalse(self.model.process, "Process value not changed")

    #############
    # Behaviors #
    #############

    def given_i_have_n_repositories(self, n):
        self.repositories = []
        for i in range(n):
            self.main_step.on_add_repository_button__clicked()
            repo = self.main_step.repository_list[-1]
            repo.root = 'root %i' % i
            repo.module = 'module %i' % i
            self.repositories.append(repo)
        self.assertEquals(self.repositories[:], self.main_step.repository_list[:],
                          "Problem adding repositories")

    def given_i_have_n_tags(self, n):
        self.tags = []
        for i in range(n):
            self.main_step.on_add_tag_button__clicked()
            tag = self.main_step.tag_list[-1]
            tag.name = "Tag %i" % i
            self.tags.append(tag)
        self.assertEquals(self.tags[:], self.main_step.tag_list[:],
                          "Problem adding tags")

    def given_i_have_selected_repository(self, position):
        self.selected_repository = self.repositories[position]
        self.main_step.repository_list.select(self.selected_repository)
        self.assertEquals(self.selected_repository, self.main_step.repository_list.get_selected())

    def given_i_have_selected_tag(self, position):
        self.selected_tag = self.tags[position]
        self.main_step.tag_list.select(self.selected_tag)
        self.assertEquals(self.selected_tag, self.main_step.tag_list.get_selected())

    def when_i_add_a_repository(self):
        self.main_step.on_add_repository_button__clicked()
        return self.main_step.repository_list[-1]

    def when_i_add_a_tag(self):
        self.main_step.on_add_tag_button__clicked()
        return self.main_step.tag_list[-1]

    def when_i_remove_repository(self):
        self.main_step.on_del_repository_button__clicked()
        if self.selected_repository:
            self.repositories.remove(self.selected_repository)
        self.removed_repository = self.selected_repository

    def when_i_remove_tag(self):
        self.main_step.on_del_tag_button__clicked()
        if self.selected_tag:
            self.tags.remove(self.selected_tag)
        self.removed_tag = self.selected_tag

    def when_i_change_package_entry(self):
        self.main_step.package_entry.set_text('changed package value')

    def when_i_change_path_entry(self):
        self.main_step.path_entry.set_text('changed path value')

    def then_it_should_add_repository_to_model(self, repository):
        self.assertTrue(repository in self.model.repositories, "Repository not added to model")
 
    def then_it_should_add_tag_to_model(self, tag):
        self.assertTrue(tag in self.model.tags, "Tag not added to model")

    def then_it_should_remove_repository_from_model(self):
        self.assertTrue(self.removed_repository not in self.model.repositories,
                        "Repository not removed from model")
        self.assertEquals(self.repositories, self.model.repositories,
                          "Problem removing repository")

    def then_it_should_remove_tag_from_model(self):
        self.assertTrue(self.removed_tag not in self.model.tags,
                        "Tag not removed from model")
        self.assertEquals(self.repositories, self.model.repositories,
                          "Problem removing tag")

    def then_it_should_do_nothing(self):
        pass

    def then_it_should_change_model_name(self):
        self.assertEquals('changed package value', self.model.name, "Model not updated")

    def then_it_should_change_model_path(self):
        self.assertEquals('changed path value', self.model.path, "Model not updated")


class ManageFilesStepTests(TestCase):
    def setUp(self):
        self.processor = Mock()
        self.processor.checkout_files.return_value = []
        self.processor.process_files.return_value = []
        # Make it run synchronously
        ProcessorThread.start = ProcessorThread.run

        self.model = Package()
        self.step = ManageFilesStep(self.model, logger=Mock())
        self.step.processor = self.processor
        self.model.path = "/tmp/"
        self.model.name = 'packagename'

    def testShouldProcessAndCheckoutPackageOnPostInit(self):
        """ Given I have a package to checkout and process it should be done"""
        self.given_i_have_to_checkout_package()

        self.given_i_have_to_process_package()

        self.when_i_enter_step()

        self.then_it_should_call_checkout()

        self.then_it_should_call_process()

    def testShouldCheckoutPackageOnPostInit(self):
        """ Given I have a package to checkout it should be done"""
        self.given_i_have_to_checkout_package()

        self.when_i_enter_step()

        self.then_it_should_call_checkout()

    def testShouldProcessPackageOnPostInit(self):
        """ Given I have a package to process it should be done"""
        self.given_i_have_to_process_package()

        self.when_i_enter_step()

        self.then_it_should_call_process()

    def testShouldLoadCheckedOutFiles(self):
        """ Given I have checked out files they should be loaded into lists"""
        self.given_i_have_to_checkout_package()

        self.given_i_have_checkedout_files()

        self.when_i_enter_step()

        self.then_it_should_load_checkedout_files()

    def testShouldLoadScripts(self):
        """ Given I have processed files they should be loaded into lists"""
        self.given_i_have_to_process_package()

        self.given_i_have_processed_files()

        self.when_i_enter_step()

        self.then_it_should_load_processed_scripts()

    def testShouldLoadCheckedOutAndProcessedFiles(self):
        """ Given I have checked out and processed files they should be loaded into lists"""

        self.given_i_have_to_checkout_package()

        self.given_i_have_to_process_package()

        self.given_i_have_checkedout_files()

        self.given_i_have_processed_files()

        self.when_i_enter_step()

        self.then_it_should_load_checkedout_files()

        self.then_it_should_load_processed_scripts()


    #############
    # Behaviors #
    #############

    def given_i_have_to_checkout_package(self):
        self.model.checkout = True

    def given_i_have_to_process_package(self):
        self.model.process = True

    def given_i_have_checkedout_files(self):
        f1 = File('/tmp/file1.sql')
        f2 = File('/tmp/file2.sql')
        f3 = File('/tmp/file3.sql')
        self.checked_out_files = [f1, f2, f3]

        self.model.files = self.checked_out_files

    def given_i_have_processed_files(self):
        s1 = InstallScript('Script 1', content=[File('File 1')])
        s2 = InstallScript('Script 2', content=[File('File 2'), File('File 3')])
        self.processed_scripts = [s1, s2]
        self.processor.process_files.return_value = self.processed_scripts

    def when_i_enter_step(self):
        self.step.post_init()

    def then_it_should_call_checkout(self):
        checkout_called = self.processor.checkout_files.called
        self.assertTrue(checkout_called, "Files should be checked out.")

    def then_it_should_call_process(self):
        process_called = self.processor.process_files.called
        self.assertTrue(process_called, "Files should be processed.")

    def then_it_should_load_checkedout_files(self):
        self.assertEquals(self.checked_out_files, self.step.filelist.get_data())

    def then_it_should_load_processed_scripts(self):
        self.assertEquals(self.processed_scripts, self.step.filetree.get_data())


class ReleaseNotesStepTests(TestCase):
    def setUp(self):
        self.model = Package()
        self.rn_step = ReleaseNotesStep(self.model)

        # Context
        self.defects = []
        self.requirements = []
        self.selected_defect = None
        self.selected_requirement = None
        self.removed_defect = None
        self.removed_requirement = None

    def testAddDefect(self):
        """When I add a defect to list it should be added to model"""
        self.given_i_have_n_defects(0)

        self.when_i_add_a_defect()

        self.then_it_should_add_defect_to_model()

    def testRemoveDefect(self):
        """When I remove a defect from list it should be removed from model"""
        self.given_i_have_n_defects(3)

        self.given_i_have_selected_defect(1)

        self.when_i_remove_defect()

        self.then_it_should_remove_defect_from_model()

    def testAddRequirement(self):
        """When I add a requirement to list it should be added to model"""
        self.given_i_have_n_requirements(0)

        self.when_i_add_a_requirement()

        self.then_it_should_add_requirement_to_model()

    def testRemoveRequirement(self):
        """When I remove a requirement from list it should be removed from model"""
        self.given_i_have_n_requirements(3)

        self.given_i_have_selected_requirement(2)

        self.when_i_remove_requirement()

        self.then_it_should_remove_requirement_from_model()

    def given_i_have_n_defects(self, number):
        for i in range(number):
            self.when_i_add_a_defect()
        self.assertEquals(self.defects[:], self.rn_step.defectlist[:],
                          "Problem adding defects to list")

    def given_i_have_n_requirements(self, number):
        for i in range(number):
            self.when_i_add_a_requirement()
        self.assertEquals(self.requirements[:], self.rn_step.requirementlist[:],
                          "Problem adding requirements to list")

    def given_i_have_selected_defect(self, position):
        self.selected_defect = self.defects[position]
        self.rn_step.defectlist.select(self.selected_defect)
        self.assertEquals(self.selected_defect, self.rn_step.defectlist.get_selected(),
                          "Problem selecting defect.")

    def given_i_have_selected_requirement(self, position):
        self.selected_requirement = self.requirements[position]
        self.rn_step.requirementlist.select(self.selected_requirement)
        self.assertEquals(self.selected_requirement, self.rn_step.requirementlist.get_selected(),
                          "Problem selecting requirement.")

    def when_i_add_a_defect(self):
        self.rn_step.defect_local_entry.set_text('local id')
        self.rn_step.defect_client_entry.set_text('client id')
        self.rn_step.defect_desc_entry.update('desc')

        self.rn_step.on_add_defect_button__clicked()
        try:
            self.added_defect = self.rn_step.defectlist[:][-1]
        except Exception, e:
            self.fail("Defect not added (%s)" % str(e))
        self.defects.append(self.added_defect)

    def when_i_add_a_requirement(self):
        self.rn_step.req_id_entry.set_text('req id')
        self.rn_step.req_desc_entry.update('desc')

        self.rn_step.on_add_req_button__clicked()
        try:
            self.added_req = self.rn_step.requirementlist[:][-1]
        except Exception, e:
            self.fail("Requirement not added (%s)" % str(e))
        self.requirements.append(self.added_req)

    def when_i_remove_defect(self):
        self.defects.remove(self.selected_defect)
        self.removed_defect = self.selected_defect
        self.rn_step.on_del_defect_button__clicked()
 
    def when_i_remove_requirement(self):
        self.requirements.remove(self.selected_requirement)
        self.removed_requirement = self.selected_requirement
        self.rn_step.on_del_req_button__clicked()

    def then_it_should_add_defect_to_model(self):
        self.assertTrue(self.added_defect in self.model.defects,
                        "Defect not added to model")

    def then_it_should_add_requirement_to_model(self):
        self.assertTrue(self.added_req in self.model.requirements,
                        "Requirement not added to model")

    def then_it_should_remove_defect_from_model(self):
        self.assertTrue(self.removed_defect not in self.model.defects,
                        "Defect not removed from model")

    def then_it_should_remove_requirement_from_model(self):
        self.assertTrue(self.removed_requirement not in self.model.requirements,
                        "Requirement not removed from model")


