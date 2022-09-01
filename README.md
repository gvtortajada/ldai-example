# Prerequisite

Create or get a GCP project ID.<br />
Enable DocumentAI API.<br />
Create a W9 and an OCR processors in Document AI.<br />
Create a gcs bucket<br />
Upload the samples/w9.pdf in the bucket<br />
You need Python3 installed.<br />
Replace in *.py files the project ID, the bucket and the processor IDs by the ones you've just created:<br />
- PROJECT_ID='<PROJECT_ID>'<br />
- PROCESSOR_ID='<PROCESSOR_ID>' (OCR or W9)<br />
- gcs_input_uri='gs://<GCS_BUCKET>/W9.pdf'<br />
- gcs_output_bucket='gs://<GCS_BUCKET>'<br />

# Installation

```
python3 -m virtualenv venv
source venv/bin/activate
pip install -r requirements.txt
```

# Run

Now you can run the 3 python scripts:
 - ocr.py parses the W9.pdf using the generic OCR processor and create ocr.json containing the json response from the API <br />
 - w9.py parses the W9.pdf using the W9 processor and create w9.json containing the json response from the API <br />
 - w9_batch.py parses the W9.pdf in a bucket using the W9 processor in batch mode and output the results in a the bucket <br />