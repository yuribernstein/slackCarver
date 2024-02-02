# Slack Channel Data Exporter & Dataset Creator
This Flask application serves as a bridge between Slack channels and data analysis, enabling the export of Slack channel messages and the creation of datasets for machine learning applications.

## Features
- **Slack Channel Export: Dump all messages from a specified Slack channel, anonymizing user data for privacy.
- **Dataset Creation: Generate datasets from Slack channel exports, tailored for machine learning models, with a focus on conversation context and code block extraction.
  
#Getting Started
Prerequisites
Python 3.x
Flask
Slack SDK for Python
Transformers by Hugging Face

#Installation
Clone the repository to your local machine.
Install the required Python packages using pip install -r requirements.txt.

#Configuration
Replace YOUR_SLACK_TOKEN_HERE in the code with your actual Slack API token.

#Running the Application
Run the Flask application with the following command:

sh
python app.py
The server will start on http://localhost:8080.

#Usage
- **Export Slack Channel
POST to /api/v1/slack/<channel> to export messages from the specified Slack channel.

- **Create Dataset
GET /api/v1/dataset/<channel> to download an existing dataset.
POST to the same endpoint to create a new dataset from the specified Slack channel's export.

#Contributing
Feel free to fork the repository, make changes, and submit pull requests. Contributions are welcome!

#License
This project is open-source and available under the Apache 2.0 License.
