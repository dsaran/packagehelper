from test.framework import TestCase
from package.types.loader import Loader

class LoaderTests(TestCase):

    def setUp(self):
        self.xml = """<package-helper>
                        <type name="type_name">
                        <category name="DataManipulation"/>
                        <matcher class="package.types.matchers.PathRegexMatcher">
                            <constructor-arg name="regex">ACT_BD.*DML</constructor-arg>
                         </matcher>
                         </type>
                         <type name="type_name_two">
                            <category name="Source"/>
                            <matcher class="package.types.matchers.PathRegexMatcher">
                                <constructor-arg name="regex">ACT_BD.*DML</constructor-arg>
                             </matcher>
                         </type>
                       </package-helper>"""

    def testLoaderConstructor(self):
        """ Loader constructor need either a file or a string to work"""
        self.assertRaises(Exception, Loader)

    def testLoaderShouldReturnAllTypes(self):
        """ Loader should return all 'types' from xml"""
        loader = Loader(text=self.xml) 
        types = loader.loadTypes()
        self.assertEquals(len(types), 2)

    def testLoaderShouldGetMatchersForEachType(self):
        """Loader should correctly load the matcher instance"""
        pass

    def testLoaderShouldGetParserForEachType(self):
        """Loader should correctly load the parser instance"""
        pass

