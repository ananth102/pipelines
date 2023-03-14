from commonv2.sagemaker_component import SageMakerJobStatus

from unittest.mock import patch, MagicMock
import unittest
from EndpointConfig.src.EndpointConfig_spec import SageMakerEndpointConfigSpec
from EndpointConfig.src.EndpointConfig_component import SageMakerEndpointConfigComponent


class EndpointConfigComponentTestCase(unittest.TestCase):

    REQUIRED_ARGS = [
        "--region",
        "us-west-1",
        "--endpoint_config_name",
        "test",
        "--production_variants",
        "[]",
    ]

    @classmethod
    def setUp(cls):
        cls.component = SageMakerEndpointConfigComponent()

    @patch("EndpointConfig.src.EndpointConfig_component.super", MagicMock())
    def test_do_sets_name(self):

        named_spec = SageMakerEndpointConfigSpec(self.REQUIRED_ARGS)
        with patch(
            "EndpointConfig.src.EndpointConfig_component.SageMakerComponent._get_current_namespace"
        ) as mock_namespace:
            mock_namespace.return_value = "test-namespace"
            self.component.Do(named_spec)
            self.assertEqual("test", self.component.job_name)

    def test_get_job_status(self):
        with patch(
            "EndpointConfig.src.EndpointConfig_component.SageMakerComponent._get_resource"
        ) as mock_get_resource:
            mock_get_resource.return_value = {"arn": "arn"}

            self.assertEqual(
                self.component._get_job_status(),
                SageMakerJobStatus(
                    is_completed=True, raw_status="Completed", has_error=False
                ),
            )


if __name__ == "__main__":
    unittest.main()
