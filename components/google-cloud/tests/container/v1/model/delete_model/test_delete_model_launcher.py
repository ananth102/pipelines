# Copyright 2022 The Kubeflow Authors. All Rights Reserved.
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
"""Test Vertex AI Batch Prediction Job Launcher Client module."""

import os

from google_cloud_pipeline_components.container.v1.model.delete_model import launcher
from google_cloud_pipeline_components.container.v1.model.delete_model import remote_runner

import unittest
from unittest import mock


class LauncherDeleteModelUtilsTests(unittest.TestCase):

  def setUp(self):
    super(LauncherDeleteModelUtilsTests, self).setUp()
    self._gcp_resources = os.path.join(
        os.getenv('TEST_UNDECLARED_OUTPUTS_DIR'),
        'test_file_path/test_file.txt')
    self._input_args = [
        '--type', 'DeleteModel', '--project', '', '--location',
        '', '--payload', 'test_payload', '--gcp_resources',
        self._gcp_resources
    ]

  @mock.patch.object(
      remote_runner, 'delete_model', autospec=True)
  def test_launcher_on_delete_model_type(self, mock_delete_model):
    launcher.main(self._input_args)
    mock_delete_model.assert_called_once_with(
        type='DeleteModel',
        project='',
        location='',
        payload='test_payload',
        gcp_resources=self._gcp_resources)
