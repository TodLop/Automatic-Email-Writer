# Automatic Email Writer

This is a Python application built with PyQt5 that automates the process of generating and sending emails. It uses the Ollama API to generate professional email content using a language model (Llama 3.1) and the Google Gmail API to send emails via Gmail.

## Features

- **Email Generation**: Automatically generates professional email content based on the recipient, subject, and purpose using the Ollama API (Llama 3.1).
- **Email Sending**: Sends the generated email directly via Gmail, using Google's Gmail API for authentication.
- **Progress Bar**: Displays a progress bar while the email is being generated.
- **Validation**: Ensures that the recipient's email address is valid before sending the email.
- **OAuth 2.0 Authentication**: Integrates Google OAuth for Gmail API access, securely managing tokens.
- **Logout Functionality**: Allows users to log out and delete their OAuth token, followed by automatic application restart.

## Prerequisites

- Python 3.x
- PyQt5: Install PyQt5 using the following command:
  ```
  pip install PyQt5
  ```
- Ollama API: This application uses the Ollama API to generate emails. Make sure you have access to the API and install the Ollama Python library:
  ```
  pip install ollama
  ```
- Google API Client: The Gmail API is used to send emails. You need to install the Google API client:
  ```
  pip install --upgrade google-api-python-client google-auth google-auth-oauthlib google-auth-httplib2
  ```
- Gmail API Setup:
  1. Enable Gmail API for your Google account.
  2. Download the credentials.json file (OAuth 2.0 client secret) and place it in the root directory of this project.
  3. Rename the credentials.json file to `ollama_email_auto_response.json`.
  4. Run the program to authenticate your Google account and create the `token.json` file automatically.

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/TodLop/automatic-email-writer.git
   cd automatic-email-writer
   ```
2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Make sure you have the Google OAuth credentials file (`ollama_email_auto_response.json`) in the root directory.
4. Run the application:
   ```
   python main.py
   ```

## Usage

1. Open the application.
2. Enter the recipient's email, subject, and purpose of the email in the respective fields.
3. Click on "Generate Email" to create the email content. A progress bar will appear while the email is being generated.
4. Once the email content is generated, it will appear in the text area. Review it and click "Send Email" to send the email.
5. Use the "Logout" button to log out of the Gmail account, which will also restart the application.

## Application Structure

- **OllamaWorker Class**: This class handles the interaction with the Ollama API to generate email content. It runs in a separate thread to keep the UI responsive.
- **EmailSender Class**: Manages authentication and sending emails using the Gmail API.
- **AutoEmailApp Class**: This is the main UI class that handles user input, email generation, and sending.
- **Main.py**: Contains the entry point for the PyQt application.

## Security

- **OAuth 2.0**: This application uses Google's OAuth 2.0 authentication system to securely access Gmail. Ensure that your `token.json` and `ollama_email_auto_response.json` files are kept private.
- **Sensitive Data**: Never share your OAuth tokens or credentials files publicly. Add these files to your `.gitignore` before uploading to a repository.

## Troubleshooting

- If you encounter issues with Gmail API authentication, ensure that your credentials file is valid and correctly configured.
- If the generated email content is not what you expect, check the Ollama API response or adjust the email generation prompt.

## License

This project is licensed under the MIT License.
