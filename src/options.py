"""
author: Marie-Neige Chapel
"""

# PyQt
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QDialog, QDataWidgetMapper
from PyQt6.uic import loadUi

# PackY
from preferences import Preferences, PreferencesRows

###############################################################################
class Options(QDialog):

	# -------------------------------------------------------------------------
	def __init__(self, preferences: Preferences, parent=None):
		super(Options, self).__init__()

		# ----------------
		# MEMBER VARIABLES
		# ----------------
		self._ui = loadUi("../resources/options.ui", self)

		self._general_mapper = QDataWidgetMapper(self)
		self._general_mapper.setOrientation(Qt.Orientation.Vertical)

		self._task_mapper = QDataWidgetMapper(self)
		self._task_mapper.setOrientation(Qt.Orientation.Vertical)
		self._preferences = preferences

		self.initGeneralMapper()
		self.initTaskMapper()
	
	# -------------------------------------------------------------------------
	def initGeneralMapper(self):
		self._general_mapper.setModel(self._preferences)
		self._general_mapper.addMapping(self._ui.r_button_keep_all, PreferencesRows.SR_KEEP_ALL.value)
		self._general_mapper.addMapping(self._ui.r_button_nb_snapshots, PreferencesRows.SR_NB_SNAPSHOT.value)
		self._general_mapper.toFirst()

	# -------------------------------------------------------------------------
	def initTaskMapper(self):
		self._task_mapper.setModel(self._preferences)
		self._task_mapper.addMapping(self._ui.r_button_current_date, PreferencesRows.T_CURR_DATE.value)
		self._task_mapper.addMapping(self._ui.r_button_version_num, PreferencesRows.T_VERSION_NUM.value)
		self._task_mapper.addMapping(self._ui.r_button_nothing, PreferencesRows.T_NOTHING.value)
		self._task_mapper.toFirst()