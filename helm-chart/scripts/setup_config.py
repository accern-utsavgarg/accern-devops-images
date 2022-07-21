import sys

import accern_xyme

print(sys.argv)
XYME_HOST = sys.argv[1] if len(sys.argv) > 1 else "http://xyme-monitor:8080/"


CONFIG = accern_xyme.XYMEClient.load_json("setup_config.json")

XYME_SERVER_TOKEN = accern_xyme.XYMEClient.get_env_str("XYME_SERVER_TOKEN")
XYME_CONFIG_TOKEN = accern_xyme.XYMEClient.get_env_str("XYME_CONFIG_TOKEN")
NAMESPACE = accern_xyme.XYMEClient.get_env_str("KUBERNETES_NAMESPACE")

AWS_ACCESS_KEY_ID = CONFIG["accern_aws_key"]
AWS_SECRET_ACCESS_KEY = CONFIG["accern_aws_access_key"]
S3_BUCKET = CONFIG["s3_bucket"]
FORECAST_S3_PATH = CONFIG["forecast_s3_path"]
if FORECAST_S3_PATH.strip() == "INVALID" or not FORECAST_S3_PATH:
    raise ValueError(
        f"FORECAST_S3_PATH is not set properly: {FORECAST_S3_PATH}")
ENDPOINT_URL = CONFIG.get("endpoint_url", None)
REGION_NAME = CONFIG.get("region_name", None)
USE_SSL = CONFIG.get("use_ssl", True)

DREMIO_KEY = CONFIG.get("dremio_key")
DREMIO_HOST = CONFIG.get("dremio_host", "")
DREMIO_USER = CONFIG.get("dremio_user", "")
DREMIO_PASSWORD = CONFIG.get("dremio_password", "")
XYME = accern_xyme.create_xyme_client(XYME_HOST, XYME_SERVER_TOKEN)

print("Set Secrets")

XYME.set_named_secret(
    XYME_CONFIG_TOKEN, "accern_aws_key", AWS_ACCESS_KEY_ID)
XYME.set_named_secret(
    XYME_CONFIG_TOKEN, "accern_aws_access_key", AWS_SECRET_ACCESS_KEY)
XYME.set_named_secret(
    XYME_CONFIG_TOKEN, "dremio_pw", DREMIO_PASSWORD)

XYME.set_settings(XYME_CONFIG_TOKEN, {
    "es": {},
    "s3": {
        "aws": {
            "api_version": None,
            "aws_access_key_id": "accern_aws_key",
            "aws_secret_access_key": "accern_aws_access_key",
            "aws_session_token": None,
            "buckets": {
                "accern-ml-forecast":
                    f"{S3_BUCKET}/{FORECAST_S3_PATH}/forecast",
                "accern-ml-inference":
                    f"{S3_BUCKET}/{FORECAST_S3_PATH}/forecast_inf",
                "accern-ml-inference-input":
                    f"{S3_BUCKET}/{FORECAST_S3_PATH}/forecast_inf_input",
                "accern-ml-inference-pred":
                    f"{S3_BUCKET}/{FORECAST_S3_PATH}/forecast_inf_pred",
                "accern-ml-input":
                    f"{S3_BUCKET}/{FORECAST_S3_PATH}/forecast_input",
                "accern-ml-test":
                    f"{S3_BUCKET}/{FORECAST_S3_PATH}/forecast_test",
                "accern-ml-test-metrics":
                    f"{S3_BUCKET}/{FORECAST_S3_PATH}/forecast_test_metrics",
                "accern-ml-nlp":
                    f"{S3_BUCKET}/nlp_models",
                "accern-ml-train":
                    f"{S3_BUCKET}/{FORECAST_S3_PATH}/forecast_train",
                "accern-ml-train-metrics":
                    f"{S3_BUCKET}/{FORECAST_S3_PATH}/forecast_train_metrics",
                "accern-auto-blobs":
                    f"{S3_BUCKET}/{FORECAST_S3_PATH}/forecast_auto_blobs",
            },
            "endpoint_url": ENDPOINT_URL,
            "region_name": REGION_NAME,
            "use_ssl": USE_SSL,
            "verify": None,
        },
    },
    "triton": {
        "aws": {
            "api_version": None,
            "aws_access_key_id": "accern_aws_key",
            "aws_secret_access_key": "accern_aws_access_key",
            "aws_session_token": None,
            "buckets": {
                "accern-ml-forecast":
                    f"{S3_BUCKET}/{FORECAST_S3_PATH}/forecast",
                "accern-ml-nlp": f"{S3_BUCKET}/model_repository",
            },
            "endpoint_url": ENDPOINT_URL,
            "region_name": REGION_NAME,
            "use_ssl": USE_SSL,
            "verify": None,
        },
    },
    "dremio": {
        DREMIO_KEY: {
            "host": DREMIO_HOST,
            "user": DREMIO_USER,
            "password": "dremio_pw",
        },
    } if DREMIO_KEY is not None else {},
    "versions": {
        "v4.2.0": ("xyme-backend", "v4.2.2"),
    },
})
