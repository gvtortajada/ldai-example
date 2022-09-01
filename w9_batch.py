import re
from google.api_core.client_options import ClientOptions
from google.cloud import documentai_v1 as documentai
from google.cloud import storage

LOCATION='us'
PROJECT_ID='<PROJECT_ID>'
PROCESSOR_ID='<PROCESSOR_ID>'
FILE_PATH='./samples/W9.pdf'
gcs_input_uri='gs://<GCS_BUCKET>/W9.pdf'
gcs_output_bucket='gs://<GCS_BUCKET>'
gcs_output_uri_prefix='results'


def batch_process_documents(
    timeout: int = 300,
):

    # You must set the api_endpoint if you use a location other than 'us', e.g.:
    opts = ClientOptions(api_endpoint=f"{LOCATION}-documentai.googleapis.com")

    client = documentai.DocumentProcessorServiceClient(client_options=opts)

    gcs_document = documentai.GcsDocument(
        gcs_uri=gcs_input_uri, mime_type='application/pdf'
    )

    # Load GCS Input URI into a List of document files
    gcs_documents = documentai.GcsDocuments(documents=[gcs_document])
    input_config = documentai.BatchDocumentsInputConfig(gcs_documents=gcs_documents)

    # Cloud Storage URI for the Output Directory
    destination_uri = f"{gcs_output_bucket}/{gcs_output_uri_prefix}/"

    gcs_output_config = documentai.DocumentOutputConfig.GcsOutputConfig(
        gcs_uri=destination_uri
    )

    # Where to write results
    output_config = documentai.DocumentOutputConfig(gcs_output_config=gcs_output_config)

    # The full resource name of the processor, e.g.:
    # projects/project_id/locations/location/processor/processor_id
    # You must create new processors in the Cloud Console first
    name = client.processor_path(PROJECT_ID, LOCATION, PROCESSOR_ID)

    request = documentai.BatchProcessRequest(
        name=name,
        input_documents=input_config,
        document_output_config=output_config,
    )

    # BatchProcess returns a Long Running Operation (LRO)
    operation = client.batch_process_documents(request)

    # Continually polls the operation until it is complete.
    # This could take some time for larger files
    # Format: projects/PROJECT_NUMBER/locations/LOCATION/operations/OPERATION_ID
    print(f"Waiting for operation {operation.operation.name} to complete...")
    operation.result(timeout=timeout)

    # Once the operation is complete,
    # get output document information from operation metadata
    metadata = documentai.BatchProcessMetadata(operation.metadata)

    if metadata.state != documentai.BatchProcessMetadata.State.SUCCEEDED:
        raise ValueError(f"Batch Process Failed: {metadata.state_message}")

    storage_client = storage.Client()

    print("Output files:")
    # One process per Input Document
    for process in metadata.individual_process_statuses:
        # output_gcs_destination format: gs://BUCKET/PREFIX/OPERATION_NUMBER/INPUT_FILE_NUMBER/
        # The Cloud Storage API requires the bucket name and URI prefix separately
        matches = re.match(r"gs://(.*?)/(.*)", process.output_gcs_destination)
        if not matches:
            print(
                "Could not parse output GCS destination:",
                process.output_gcs_destination,
            )
            continue

        output_bucket, output_prefix = matches.groups()

        # Get List of Document Objects from the Output Bucket
        output_blobs = storage_client.list_blobs(output_bucket, prefix=output_prefix)

        # Document AI may output multiple JSON files per source file
        for blob in output_blobs:
            # Document AI should only output JSON files to GCS
            if ".json" not in blob.name:
                print(
                    f"Skipping non-supported file: {blob.name} - Mimetype: {blob.content_type}"
                )
                continue

            # Download JSON File as bytes object and convert to Document Object
            print(f"Fetching {blob.name}")
            document = documentai.Document.from_json(
                blob.download_as_bytes(), ignore_unknown_fields=True
            )

            # For a full list of Document object attributes, please reference this page:
            # https://cloud.google.com/python/docs/reference/documentai/latest/google.cloud.documentai_v1.types.Document

            # Read the text recognition output from the processor
            print("The document contains the following text:")
            print(document.text)


if __name__ == "__main__":
    batch_process_documents()