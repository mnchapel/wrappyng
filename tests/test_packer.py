"""
author: Marie-Neige Chapel
"""

# Python
import json
import os
import pathlib
import pytest
import re
from unittest.mock import MagicMock, Mock
from zipfile import is_zipfile, ZipFile

# PyQt
from PyQt6.QtCore import QSettings, QStandardPaths

# PackY
import model.task
from model.preferences import PreferencesKeys
from model.task import Task
from model.files_model import FilesModel
from model.zip_packer import ZipPacker

###############################################################################
# FILE HIERARCHY
# -----------------------------------------------------------------------------
#
# tmp_path
# ├─ folder
# │  ├─ file1.txt
# │  └─ dir1
# │     ├─ file2.txt
# │     └─ file3.txt
# └─ results
#
# - tmp_path/folder: contains the files and the folders that will be packed.
# - tmp_path/results: contains the archive (result of the packer). 
#
###############################################################################

###############################################################################
# GLOBAL VARIABLES
###############################################################################

test_data_folder = pathlib.Path("tests", "data", "packer")

###############################################################################
# UTIL FUNCTIONS
###############################################################################

# -----------------------------------------------------------------------------
def camelCaseToSnakeCase(value: str) -> str:
	return re.sub(r"(?<!^)(?=[A-Z])", "_", value).lower()

###############################################################################
# MODULE FIXTURE SCOPE
###############################################################################

# -----------------------------------------------------------------------------
@pytest.fixture
def loadFileHierarchy(request, tmp_path):
	file = pathlib.Path(request.config.rootdir, test_data_folder, "file_hierarchy").with_suffix(".json")
	file_txt = file.read_text()
	a_tmp_path = str(tmp_path).replace("\\", "/")
	file_txt = file_txt.replace("tmp_path", a_tmp_path)
	data = json.loads(file_txt)

	yield data

# -----------------------------------------------------------------------------
@pytest.fixture
def loadTestData(request, tmp_path):
	json_filename = camelCaseToSnakeCase(request.cls.__name__[4:])
	file = pathlib.Path(request.config.rootdir, test_data_folder, json_filename).with_suffix(".json")
	file_txt = file.read_text()
	a_tmp_path = str(tmp_path).replace("\\", "/")
	file_txt = file_txt.replace("tmp_path", a_tmp_path)
	data = json.loads(file_txt)

	yield data

# -----------------------------------------------------------------------------
def recursive(fh_dict):
	for node in fh_dict:
		type = node["type"]

		match type:
			case "file":
				open(node["path"], "w").close()
			case "folder":
				os.makedirs(node["path"])
			case _:
				raise Exception("")

		if "children" in node:
			recursive(node["children"])

# -----------------------------------------------------------------------------
@pytest.fixture
def createFileHierarchy(loadFileHierarchy):
	fh_dict = loadFileHierarchy

	recursive(fh_dict["root"])

# -----------------------------------------------------------------------------
@pytest.fixture
def checkArchiveHierarchy(loadTestData, outputPath, test_name):
	data = loadTestData[test_name]["expected"]
	expected_hierarchy = data["archive_hierarchy"]

	output_path = outputPath
	print(f"output_path = {output_path}")
	zip = ZipFile(output_path)

	output_name = os.path.basename(output_path)
	output_name = output_name.rsplit(".", 1)[0]
	expected_hierarchy = [output_name + "/" + item for item in expected_hierarchy]

	assert zip.namelist() == expected_hierarchy

###############################################################################
# TEST ZIP PACKER
#
# -----------------------------------------------------------------------------
# test_pack_file_1
# -----------------------------------------------------------------------------
#
# Description:
#		Pack a file at the root.
#
# Expected:
#		tmp_path/output_<snapshot_retention_options>.zip
#
# -----------------------------------------------------------------------------
# test_pack_file_2
# -----------------------------------------------------------------------------
#
# Description:
#		Pack a file inside a folder.
#
# Expected:
#		tmp_path/output_<snapshot_retention_options>.zip
#
# -----------------------------------------------------------------------------
# test_pack_folder_1
# -----------------------------------------------------------------------------
#
# Description:
#		Pack a folder and the files inside.
#
# Expected:
#		tmp_path/output_<snapshot_retention_options>.zip
#
###############################################################################
class TestZipPacker():

	# -------------------------------------------------------------------------
	@pytest.fixture
	def runZipPacker(self, loadTestData, test_name):
		task_dict = loadTestData[test_name]["data"]
		task = Task(task_dict["id"], task_dict)
		zip_packer = ZipPacker(task)
		zip_packer.run()

	# -------------------------------------------------------------------------
	@pytest.fixture
	def outputPath(self, loadTestData, test_name):
		data = loadTestData[test_name]["expected"]
		dirname = data["dst_folder"]

		suffix_pattern_date = "_[0-9]{4}_[0-9]{2}_[0-9]{2}"
		suffix_pattern_version = "_[0-9]+"

		file_pattern_date = data["dst_raw_basename"] + suffix_pattern_date + ".zip"
		file_pattern_version = data["dst_raw_basename"] + suffix_pattern_version + ".zip"

		snapshot_date = [f for f in filter(re.compile(file_pattern_date).match, os.listdir(dirname))]
		snapshot_version = [f for f in filter(re.compile(file_pattern_version).match, os.listdir(dirname))]

		snapshot = snapshot_date + snapshot_version
		print(f"dirname = {dirname}")

		if len(snapshot) == 1:
			yield os.path.join(dirname, snapshot[0])
		else:
			yield ""

	# -------------------------------------------------------------------------
	@pytest.mark.parametrize("test_name", ["test_pack_file_1", "test_pack_file_2", "test_pack_folder_1"])
	def testPackFile(self, createFileHierarchy, runZipPacker, outputPath, checkArchiveHierarchy, test_name):
		output_path = outputPath

		assert output_path
		assert is_zipfile(output_path)

###############################################################################
# TEST SNAPSHOT RETENTION
#
# -----------------------------------------------------------------------------
# testNoRemove
# -----------------------------------------------------------------------------
#
# Description:
#		TODO
#
# Expected:
#		TODO
#
###############################################################################
# class TestSnapshotRetention():

# 	# -------------------------------------------------------------------------
# 	@pytest.fixture
# 	def setPreferences(self, loadTestData, test_name):
# 		settings = QSettings()
# 		snapshot_retention = settings.value(PreferencesKeys.GENERAL_SR.value, type = int)
# 		nb_snapshot = settings.value(PreferencesKeys.GENERAL_NB_SNAPSHOT.value, type = int)
		
# 		data = loadTestData[test_name]["data"]

# 		settings.setValue(PreferencesKeys.GENERAL_SR.value, data["preferences"]["general_sr"])
# 		settings.setValue(PreferencesKeys.GENERAL_NB_SNAPSHOT.value, data["preferences"]["nb_snapshot"])

# 		yield settings

# 		settings.setValue(PreferencesKeys.GENERAL_SR.value, snapshot_retention)
# 		settings.setValue(PreferencesKeys.GENERAL_NB_SNAPSHOT.value, nb_snapshot)

# 	# -------------------------------------------------------------------------
# 	@pytest.mark.parametrize("test_name", ["test_no_remove_1"])
# 	def testNoRemove(self, createFileHierarchy, setPreferences, test_name):
# 		task_dict = loadTestData[test_name]["data"]["task"]
# 		task = Task(task_dict["id"], task_dict)
# 		zip_packer = ZipPacker(task)

# 		for :
# 			zip_packer.run()

# 		assert False
	
# 	# -------------------------------------------------------------------------
# 	def testRemove(self):
# 		assert False
		
###############################################################################
# TEST TMP FOLDER PATH
#
# -----------------------------------------------------------------------------
# Description:
#
###############################################################################
class TestTmpFolderPath():

	test_list = [
		"simple_test",
		"complex_test",
		"spaces_test"
	]

	# -------------------------------------------------------------------------
	@pytest.mark.parametrize("test_name", test_list)
	def test(self, loadTestData, test_name):
		input = loadTestData[test_name]["input"]
		expected = loadTestData[test_name]["expected"]

		mock_task = Mock(Task)
		mock_task.destFile = MagicMock(return_value = input)
		
		zip_packer = ZipPacker(mock_task)
		tmp_folder_path = zip_packer._Packer__tmpFolderPath()

		expected = os.path.join(os.path.dirname(model.task.__file__), expected)

		assert tmp_folder_path == expected

###############################################################################
# TEST FILTER SELECTED FILES
#
# -----------------------------------------------------------------------------
# Description:
#		The function selects the items (files and directories) that are checked
#		or partially checked to be packed.
#
# -----------------------------------------------------------------------------
# - no_item: 
# - item_checked: 
# - item_partially_checked: 
# - item_unchecked: 
# - item_mixed: 
#
###############################################################################
class TestFilterSelectedFiles():

	test_list = [
		"no_item",
		"item_checked",
		"item_partially_checked",
		"item_unchecked",
		"item_mixed"
	]

	# -------------------------------------------------------------------------
	@pytest.mark.parametrize("test_name", test_list)
	def test(self, loadTestData, test_name):
		input = loadTestData[test_name]["input"]
		expected = loadTestData[test_name]["expected"]

		mock = Mock(Task)
		mock_files_model = Mock(FilesModel)
		mock_files_model.checks = MagicMock(return_value = input)
		mock.filesSelected = MagicMock(return_value = mock_files_model)

		zip_packer = ZipPacker(mock)
		items_to_pack = zip_packer._Packer__filterSelectedFiles()

		assert items_to_pack == expected


###############################################################################
# TEST COPY ITEMS TO TMP FOLDER
#
# Description:
#		TODO.
#
# -----------------------------------------------------------------------------
# no_item
# -----------------------------------------------------------------------------
#
# "input":{}
#
# "expected":
#
###############################################################################
class TestCopyItemsToTmpFolder():

	test_list = [
		"no_item",
		"one_file",
		"complete_dir"
	]

	# -------------------------------------------------------------------------
	@pytest.mark.parametrize("test_name", test_list)
	def test(self, createFileHierarchy, loadTestData, test_name, tmp_path):
		input = loadTestData[test_name]["input"]
		expected = loadTestData[test_name]["expected"]
		
		mock_files_model = Mock(FilesModel)
		mock_files_model.rootPath = MagicMock(return_value = os.path.join(tmp_path, "folder").replace("\\", "/"))

		mock_task = Mock(Task)
		mock_task.filesSelected = MagicMock(return_value = mock_files_model)

		zip_packer = ZipPacker(mock_task)
		tmp_path_task = os.path.join(tmp_path, "results", test_name).replace("\\", "/")
		zip_packer._Packer__copyItemsToTmpFolder(input, tmp_path_task)

		for item in expected:
			assert os.path.exists(item)
