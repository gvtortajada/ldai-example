from google.api_core.client_options import ClientOptions
from google.cloud import documentai_v1 as documentai
import json

LOCATION='us'
PROJECT_ID='<PROJECT_ID>'
PROCESSOR_ID='<PROCESSOR_ID>'
FILE_PATH='./samples/W9.pdf'


def process_document_specialized_sample():
    # Online processing request to Document AI
    document = process_document()

    # Extract entities from a specialized document
    # Most specalized processors follow a similar pattern.
    # For a complete list of processors see:
    # https://cloud.google.com/document-ai/docs/processors-list
    #
    # OCR and other data is also present in the quality processor's response.
    # Please see the OCR and other samples for how to parse other data in the
    # response.

    print(f"Found {len(document.entities)} entities:")
    for entity in document.entities:
        print_entity(entity)
        # Print Nested Entities (if any)
        for prop in entity.properties:
            print_entity(prop)


def print_entity(entity: documentai.Document.Entity) -> None:
    # Fields detected. For a full list of fields for each processor see
    # the processor documentation:
    # https://cloud.google.com/document-ai/docs/processors-list
    key = entity.type_
    # some other value formats in addition to text are availible
    # e.g. dates: `entity.normalized_value.date_value.year`
    text_value = entity.text_anchor.content
    confidence = entity.confidence
    normalized_value = entity.normalized_value.text
    print(f"    * {repr(key)}: {repr(text_value)}({confidence:.1%} confident)")

    if normalized_value:
        print(f"    * Normalized Value: {repr(normalized_value)}")


def process_document():
    # You must set the api_endpoint if you use a location other than 'us', e.g.:
    opts = ClientOptions(api_endpoint=f"{LOCATION}-documentai.googleapis.com")

    client = documentai.DocumentProcessorServiceClient(client_options=opts)

    # The full resource name of the processor, e.g.:
    # projects/project_id/locations/location/processor/processor_id
    # You must create new processors in the Cloud Console first
    name = client.processor_path(PROJECT_ID, LOCATION, PROCESSOR_ID)

    # Read the file into memory
    with open(FILE_PATH, "rb") as image:
        image_content = image.read()

    # Load Binary Data into Document AI RawDocument Object
    raw_document = documentai.RawDocument(content=image_content, mime_type='application/pdf')

    # Configure the process request
    request = documentai.ProcessRequest(name=name, raw_document=raw_document)

    result = client.process_document(request=request)

    # For a full list of Document object attributes, please reference this page:
    # https://cloud.google.com/python/docs/reference/documentai/latest/google.cloud.documentai_v1.types.Document
    json_result = json.loads(documentai.Document.to_json(result.document))
    with open('w9.json', 'w') as f:
        json.dump(json_result, f, indent=2)
    return result.document


if __name__ == "__main__":
    process_document_specialized_sample()