import os
import unittest
from unittest.mock import patch, MagicMock

from commonv2.sagemaker_component import (
    SageMakerComponent,
)
from kubernetes.client.rest import ApiException


class SageMakerComponentUpgradeTest(unittest.TestCase):
    @classmethod
    def setUp(cls):
        """Bootstrap Unit test resources for testing runtime."""
        cls.component = SageMakerComponent()
        # Turn off polling interval for instant tests
        cls.component.STATUS_POLL_INTERVAL = 0

        # set up mock job_request_outline_location
        test_files_dir = os.path.join(
            os.path.dirname(os.path.relpath(__file__)), "files"
        )
        test_job_request_outline_location = os.path.join(
            test_files_dir, "test_job_request_outline.yaml.tpl"
        )
        cls.component.job_request_outline_location = test_job_request_outline_location

    def test_is_upgrade(self):
        self.component._get_resource = MagicMock(return_value={"status": "Active"})
        assert self.component._is_upgrade()
        self.component._get_resource = MagicMock(side_effect=ApiException(status=404))
        assert self.component._is_upgrade() == False

    def test_verify_resource_creation_upgrade(self):

        # Time change
        self.component._check_resource_conditions = MagicMock(return_value=None)
        self.component._get_resource = MagicMock(
            return_value={
                "status": {
                    "ackResourceMetadata": {
                        "arn": "arn:aws:sagemaker:eu-west-3:123456789103:stack/sample-endpoint"
                    }
                }
            }
        )
        self.component._get_condition_times = MagicMock(
            return_value=["1:30:1", "1:30:2"]
        )
        self.component.initial_resouce_condition_times = ["1:29:0", "1:29:0"]
        self.component.resource_upgrade = True
        assert self.component._verify_resource_creation() == True

        # Upgrade Case - same time initially
        with patch("time.sleep", return_value=None):
            self.component._get_condition_times = MagicMock(
                side_effect=[["1:29:0", "1:29:0"], ["1:30:1", "1:30:2"]]
            )
            assert self.component._verify_resource_creation() == True

    def test_get_condition_times(self):
        self.component._get_resource = MagicMock(
            return_value={
                "status": {
                    "conditions": [
                        {"lastTransitionTime": "1:30"},
                        {"lastTransitionTime": "1:31"},
                        {"bad_condition": "bad"},
                        {"lastTransitionTime": "1:32"},
                    ]
                }
            }
        )
        assert self.component._get_condition_times() == ["1:30", "1:31", "1:32"]
    

