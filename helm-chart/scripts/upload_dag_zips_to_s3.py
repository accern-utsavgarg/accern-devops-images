import accern_xyme

# Assumes that the full dag zips are downloaded to /tmp
# using the download_full_dag_zip.py

print("Uploading Dag Zips to S3")

accern_xyme.XYMEClient.upload_s3_from_file(
    ["/tmp/INFER_DAG.zip", "/tmp/KAFKA_DAG.zip", "/tmp/TRAIN_DAG.zip"],
    "upload_dag_zips_to_s3.json")
