#! /usr/bin/env python2.5
# encoding: utf-8
# Version: $Id$
# TODO: Improve the rtf generation.

import logging
from package.config import Config 
from package.util.runtime import WORKING_DIR


DEFECT_ROW= """\\pard\\intbl\\pard\\plain \\intbl\\ltrpar\\s1\\cf0{\\*\\hyphen2\\hyphlead2\\hyphtrail2\\hyphmax0}\\aspalpha\\sb60\\ql\\rtlch\\af4\\afs17\\lang255\\ltrch\\dbch\\af4\\langfe1033\\hich\\f4\\fs17\\lang1046\\loch\\f4\\fs17\\lang1046 {\\rtlch \\ltrch\\loch\\f4\\fs17\\lang1046\\i0\\b0 #IDLOCAL#}
\\cell\\pard\\plain \\intbl\\ltrpar\\s1\\cf0{\\*\\hyphen2\\hyphlead2\\hyphtrail2\\hyphmax0}\\aspalpha\\sb60\\ql\\rtlch\\af4\\afs17\\lang255\\ltrch\\dbch\\af4\\langfe1033\\hich\\f4\\fs17\\lang1046\\loch\\f4\\fs17\\lang1046 {\\rtlch \\ltrch\\loch\\f4\\fs17\\lang1046\\i0\\b0 #IDCLIENT#}                                                                                                                        \\cell\\pard\\plain \\intbl\\ltrpar\\s1\\cf0{\\*\\hyphen2\\hyphlead2\\hyphtrail2\\hyphmax0}\\aspalpha\\ql\\rtlch\\af4\\afs17\\lang255\\ltrch\\dbch\\af4\\langfe1033\\hich\\f4\\fs17\\lang1046\\loch\\f4\\fs17\\lang1046 {\\rtlch \\ltrch\\loch\\f4\\fs17\\lang1046\\i0\\b0 #DESCRIPTION#}                                                                                                                       \\cell\\row\\pard"""
CELL = """\\pard\\intbl\\pard\\plain \\intbl\\ltrpar\\s1\\cf0{\\*\\hyphen2\\hyphlead2\\hyphtrail2\\hyphmax0}\\aspalpha\\sb60\\ql\\rtlch\\af4\\afs17\\lang255\\ltrch\\dbch\\af4\\langfe1033\\hich\\f4\\fs17\\lang1046\\loch\\f4\\fs17\\lang1046 {\\rtlch \\ltrch\\loch\\f4\\fs17\\lang1046\\i0\\b0 #CELL_CONTENT#}\\cell"""

FILE_SUFFIX = "_RN.rtf"
DEFECTS_START = '<!#DEFECTS_LIST#!>'
ERDR_START = '<!#ERDR_LIST#!>'
STEP_START = '<!#STEP_LIST#!>'

log = logging.getLogger("RNGenerator")

class Document:
    defects = None
    package = None
    defects = None
    requirements = None
    tags = None
    steps = None
    step_number = None

    def __init__(self, file):
        self.file = file
        self.defects = []
        self.requirements = []
        self.package = None
        self.tags = []
        self.steps = []
        self.step_number = 1

    def add_defect(self, defect_data):
        """ Add a defect to document.
            @param defect_data a tuple with defect data
            such as '(id local, id client, description)'
        """
        self.defects.append(defect_data)

    def add_requirement(self, req_data):
        """ Add a requirement to document.
            @param req_data a tuple with requirement data
            such as '(id, description)'
        """
        self.requirements.append(req_data)

    def add_step(self, step_data):
        """ Add a installation step to document.
            @param step_data a tuple with step data
            such as '(duration, description)'
        """
        step = (Cell(str(self.step_number)), step_data[0], step_data[1], Cell("Instalador"))
        print "added step:", step
        self.steps.append(step)
        self.step_number += 1
            
    def _replace(self, region, data):
        self.text = self.text.replace(region, data)

    def _fillPackage(self):
        log.debug("Filling package name [%s]..." % self.package)
        self._replace("#PACKAGE#", self.package)

    def _fillTag(self):
        log.debug("Fillig tag name [%s]..." % str(self.tags))
        self._replace("#TAG#", self._serialize(self.tags))

    def _fill_defects(self):
        defect_rows = ""
        for defect in self.defects:
            cells = [str(cell) for cell in defect]
            defect_rows += "".join(cells)
            defect_rows += "\\row\\pard"
        self._replace(DEFECTS_START, defect_rows)

    def _fill_requirements(self):
        req_rows = ""
        for  req in self.requirements:
            cells = [str(cell) for cell in req]
            req_rows += "".join(cells)
            req_rows += "\\row\\pard"
        self._replace(ERDR_START, req_rows)

    def _fill_steps(self):
        step_rows = ""
        for step in self.steps:
            cells = [str(cell) for cell in step]
            step_rows += "".join(cells)
            step_rows += "\\row\\pard"
        self._replace(STEP_START, step_rows)

    def _serialize(self, list):
        log.debug("Serializing list: %s" % str(list))
        convertedList = [str(i) for i in list]
        return ', '.join(convertedList)

    def write(self):
        template = WORKING_DIR/"resources/RN_TEMPLATE.rtf"
        self.text = template.text()
        self._fillPackage()
        self._fillTag()
        self._fill_defects()
        self._fill_requirements()
        self._fill_steps()
        self.file.write_text(self.text)

class Cell:
    special_characters = {
            u"ã": "\\'e3",
            u"Ã": "\\'c3",
            u"õ": "\\'f5",
            u"Õ": "\\'d5",
            u"í": "\\'ed",
            u"Í": "\\'cd",
            u"é": "\\'e9",
            u"É": "\\'c9",
            u"á": "\\'e1",
            u"Á": "\\'c1",
            u"ó": "\\'f3",
            u"Ó": "\\'d3",
            u"ú": "\\'fa",
            u"Ú": "\\'da",
            u"ç": "\\'e7",
            u"Ç": "\\'c7"}

    def __init__(self, value):
        if isinstance(value, unicode):
            self.value = self.encode(value)
        else:
            self.value = value

    def __str__(self):
        value = CELL.replace("#CELL_CONTENT#", self.value)
        return value

    def encode(self, data):
        converted_data = data
        for char in self.special_characters.keys():
            converted_data = converted_data.replace(char, self.special_characters[char])
        return converted_data


class RNGenerator:
    packageName = ""
    packageType = ""
    tagName = ""

    def __init__(self, package):
        self.package = package
        rn_filename = self.package.name + FILE_SUFFIX
        file = self.package.full_path/rn_filename
        self.document = Document(file)

    def writeRN(self):
        self.document.package = self.package.name
        self.document.tags = self.package.tags
        self._fill_defects()
        self._fill_erdr()
        self._fill_steps()

        self.document.write()
        log.debug("Done.")

    def _fill_defects(self):
        log.debug("Filling defects: %s" % str(self.package.defects))
        for defect in self.package.defects:
            row = (Cell(defect.id_local), Cell(defect.id_client),
                   Cell(defect.description))
            self.document.add_defect(row)

    def _fill_erdr(self):
        log.debug("Filling ERDRs: %s" % str(self.package.requirements))
        for req in self.package.requirements:
            row = (Cell(req.id), Cell(req.description))
            self.document.add_requirement(row)

    def _fill_steps(self):
        log.debug("Filling steps")
        pre_install_steps = [(Cell("10"), Cell(u"Baixar o Weblogic que serve as apps.")),
            (Cell("5"), Cell(u"Fazer backup dos EARs antigos das aplicacoes.")),
            (Cell("10"), Cell(u"Realizar deploy dos EARs existentes no diretorio DIST do pacote"))]
        package_steps = [] 

        if self.package.has_sql:
            step = (Cell("10"), Cell(u"Rodar os scripts SQL nos usuarios e bds indicados no nome do arquivo."))
            package_steps.append(step)
        if self.package.has_xml:
            step = (Cell("5"), Cell(u"Copiar, na máquina da BD <Preencher qual BD (BDA/BDB)> onde estiver instalado o Mediation, os arquivos XML da pasta\nXML."))
            package_steps.append(step)
        if self.package.has_shellscript:
            step = (Cell("5"), Cell(u"Copiar o(s) arquivo(s) contido(s) na pasta SH com o usuário <Preencher usuário>"))
            package_steps.append(step)

        post_install_steps = [
            (Cell("10"), Cell(u"Arrancar o Weblogic que serve as apps.")),
            (Cell("10"), Cell(u"Verificar correto funcionamento do sistema"))]
        steps = pre_install_steps + package_steps + post_install_steps
        for step in steps:
            self.document.add_step(step)
        
if __name__ == "__main__":
    rn = RNGenerator()
    rn.writeRN()

