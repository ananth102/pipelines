import pytest
import os
import utils
import json

from utils import kfp_client_utils
from utils import minio_utils
from utils import sagemaker_utils



@pytest.mark.parametrize(
    "test_file_dir",
    [
        pytest.param("resources/config/kmeans-mnist-update-endpoint"),
        pytest.param(
            "resources/config/kmeans-mnist-endpoint",
            marks=[pytest.mark.canary_test, pytest.mark.shallow_canary],
        ),
    ],
)
def test_create_endpoint(
    kfp_client, experiment_id, boto3_session, sagemaker_client, test_file_dir
):

    download_dir = utils.mkdir(os.path.join(test_file_dir + "/generated"))
    test_params = utils.load_params(
        utils.replace_placeholders(
            os.path.join(test_file_dir, "config.yaml"),
            os.path.join(download_dir, "config.yaml"),
            shallow_canary=True,
        )
    )

    # Generate random prefix for model, endpoint config and endpoint name
    # to avoid errors if resources with same name exists
    test_params["Arguments"]["model_name"] = test_params["Arguments"][
        "endpoint_config_name"
    ] = test_params["Arguments"]["endpoint_name"] = input_endpoint_name = (
        utils.generate_random_string(5) + "-" + test_params["Arguments"]["model_name"]
    )

    try:
        print(f"running test with model/endpoint name: {input_endpoint_name}")

        _, _, workflow_json = kfp_client_utils.compile_run_monitor_pipeline(
            kfp_client,
            experiment_id,
            test_params["PipelineDefinition"],
            test_params["Arguments"],
            download_dir,
            test_params["TestName"],
            test_params["Timeout"],
        )

        outputs = {"sagemaker-deploy-model": ["endpoint_name"]}

        output_files = minio_utils.artifact_download_iterator(
            workflow_json, outputs, download_dir
        )

        output_endpoint_name = utils.read_from_file_in_tar(
            output_files["sagemaker-deploy-model"]["endpoint_name"]
        )
        print(f"endpoint name: {output_endpoint_name}")

        # Verify output from pipeline is endpoint name
        assert output_endpoint_name == input_endpoint_name

        # Verify endpoint is running
        assert (
            sagemaker_utils.describe_endpoint(sagemaker_client, input_endpoint_name)[
                "EndpointStatus"
            ]
            == "InService"
        )
        # Verify that the update was successful by checking that InstanceType changed
        if "ExpectedInstanceType" in test_params.keys():
            new_endpoint_config_name = sagemaker_utils.describe_endpoint(
                sagemaker_client, input_endpoint_name
            )["EndpointConfigName"]
            response = sagemaker_utils.describe_endpoint_config(
                sagemaker_client, new_endpoint_config_name
            )
            prod_variant = response["ProductionVariants"][0]
            print(f"Production Variant item: {prod_variant}")
            instance_type = prod_variant["InstanceType"]
            print(f"Production Variant item InstanceType: {instance_type}")
            assert instance_type == test_params["ExpectedInstanceType"]

        # Validate the model for use by running a prediction
        result = sagemaker_utils.run_predict_mnist(boto3_session, input_endpoint_name, download_dir)
        print(f"prediction result: {result}")
        assert json.dumps(result, sort_keys=True) == json.dumps(
            test_params["ExpectedPrediction"], sort_keys=True
        )
        utils.remove_dir(download_dir)
    finally:
        endpoints = sagemaker_utils.list_endpoints(
            sagemaker_client, name_contains=input_endpoint_name
        )["Endpoints"]
        endpoint_names = list(map((lambda x: x["EndpointName"]), endpoints))
        # Check endpoint was successfully created
        if input_endpoint_name in endpoint_names:
            sagemaker_utils.delete_endpoint(sagemaker_client, input_endpoint_name)
