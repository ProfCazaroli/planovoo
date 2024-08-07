import os
from qgis.PyQt import uic
from qgis.PyQt import QtWidgets

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'PlanoVoo_dialog_base.ui'))

class PlanoVooDialog(QtWidgets.QDialog, FORM_CLASS):
    def __init__(self, parent=None):
        super(PlanoVooDialog, self).__init__(parent)
        
        self.setupUi(self)
