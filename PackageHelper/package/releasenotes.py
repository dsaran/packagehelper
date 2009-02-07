#! /usr/bin/env python2.5
# Version: $Id: releasenotes.py,v 1.2 2009-02-07 17:40:27 daniel Exp $
# TODO: Improve the rtf generation.

import logging
from package.config import Config 


DEFECT_ROW= """\\pard\\intbl\\pard\\plain \\intbl\\ltrpar\\s1\\cf0{\\*\\hyphen2\\hyphlead2\\hyphtrail2\\hyphmax0}\\aspalpha\\sb60\\ql\\rtlch\\af4\\afs17\\lang255\\ltrch\\dbch\\af4\\langfe1033\\hich\\f4\\fs17\\lang1046\\loch\\f4\\fs17\\lang1046 {\\rtlch \\ltrch\\loch\\f4\\fs17\\lang1046\\i0\\b0 #IDPTIN#}
\\cell\\pard\\plain \\intbl\\ltrpar\\s1\\cf0{\\*\\hyphen2\\hyphlead2\\hyphtrail2\\hyphmax0}\\aspalpha\\sb60\\ql\\rtlch\\af4\\afs17\\lang255\\ltrch\\dbch\\af4\\langfe1033\\hich\\f4\\fs17\\lang1046\\loch\\f4\\fs17\\lang1046 {\\rtlch \\ltrch\\loch\\f4\\fs17\\lang1046\\i0\\b0 #IDVIVO#}                                                                                                                        \\cell\\pard\\plain \\intbl\\ltrpar\\s1\\cf0{\\*\\hyphen2\\hyphlead2\\hyphtrail2\\hyphmax0}\\aspalpha\\ql\\rtlch\\af4\\afs17\\lang255\\ltrch\\dbch\\af4\\langfe1033\\hich\\f4\\fs17\\lang1046\\loch\\f4\\fs17\\lang1046 {\\rtlch \\ltrch\\loch\\f4\\fs17\\lang1046\\i0\\b0 #DESCRIPTION#}                                                                                                                       \\cell\\row\\pard"""
FILE_SUFFIX = "_RN.rtf"
DEFECTS_START = '<!#DEFECTS_LIST#!>'

log = logging.getLogger("RNGenerator")

class RNGenerator:
    packageName = ""
    packageType = ""
    tagName = ""

    def __init__(self, package):
        try:
            self.package = package
            self.packageName = package.get_name() or ""
            self.tagName = self._serialize(self.package.get_tags())
        except:
            log.error("Error initializing RNGenerator.", exc_info=1)
            raise

    def writeRN(self):
        file = None
        try:
            log.debug("writting RN...")
            working_dir = Config().WORKING_DIR
            file = open(working_dir.joinpath("resources/RN_TEMPLATE.rtf"), "r")
            content = file.read()
        except:
            log.error("Error writing Release Notes.", exc_info=1)
            raise
        finally:
            if file:
                file.close()

        content = self._fillPackage(content)
        content = self._fillTag(content)
        content = self._writeDefects(content)
        content = self._fillErdr(content)

        self._save_file(content)
        log.debug("Done.")

    def _writeDefects(self, content):
        log.debug("Writing defects: %s" % str(self.package.get_defects()))
        defects = ""
        for defect in self.package.get_defects():
            row = self._write_defect(defect)
            defects += row
        return content.replace(DEFECTS_START, defects)

    def _fillPackage(self, text):
        log.debug("Filling package name [%s]..." % self.packageName)
        return text.replace("#PACKAGE#", self.packageName)

    def _fillType(self, text):
        log.debug("Filling type")
        return text.replace("#FIXED#", self.packageType)

    def _fillTag(self, text):
        log.debug("Fillig tag name [%s]..." % self.tagName)
        return text.replace("#TAG#", self.tagName)

    def _fillErdr(self, text):
        log.debug("Filling ERDRs")
        return text.replace("#ERDR#", "")

    def _write_defect(self, defect):
            log.debug("Writing defect: %s" % defect)
            row = DEFECT_ROW
            row = row.replace('#IDPTIN#', defect.id_ptin)
            row = row.replace('#IDVIVO#', defect.id_vivo)
            row = row.replace("#DESCRIPTION#", defect.description.decode('utf-8'))
            log.debug("Generated row: %s" % row)
            return row 

    def _serialize(self, list):
        log.debug("Serializing list: %s" % str(list))
        convertedList = [str(i) for i in list]
        return ', '.join(convertedList)

    def _save_file(self, content):
        log.debug("Saving file...")
        package_dir = self.package.get_full_path()
        if not package_dir.exists():
            package_dir.mkdir()

        file = self.package.get_full_path().joinpath(self.packageName + FILE_SUFFIX)
        file.write_text(content, linesep=None)


if __name__ == "__main__":
    rn = RNGenerator()
    rn.writeRN()
