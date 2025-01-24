# CV Reader

A Python tool that extracts text from PDF CVs, analyzes them using OpenAI's API, and generates structured output in either JSON or CSV format.

## Features

- Extracts text from PDF files using pypdf
- Analyzes extracted text using OpenAI GPT API with a predefined schema
- Supports output in JSON or CSV formats
- Handles nested list fields and formats them into structured bullet lists for Excel compatibility
- Accepts command-line arguments for flexible execution

## Prerequisites

Ensure you have the following installed:

- Python 3.8 or later
- Required dependencies (install via pip)
- An OpenAI API key stored in a .env file

## Installation

1. Clone the repository:

   ```
   git clone https://github.com/bruno-farias/cv-reader.git
   cd cv-reader
   ```

2. Install dependencies:

   ```pip install -r requirements.txt```

3. Create a .env file in the project root with your OpenAI API key:

   ```OPENAI_API_KEY=your_openai_api_key_here```

## Usage

### Command-line Execution

Run the script by providing the folder path containing PDF CVs:

```python main.py /path/to/cv-folder --output csv```

#### Arguments:

| Argument   | Description                           | Default  |
| ---------- | ------------------------------------- | -------- |
| folder     | Path to the folder containing CV PDFs | Required |
| --output   | Output format: json or csv            | csv      |

**Example:**

python main.py ./cv-folder --output json

If no output format is specified, CSV is used by default.

### Sample Output

#### JSON Output (Example):

```
[
  {
    "filename": "resume1.pdf",
    "name": "John Doe",
    "email": "john.doe@example.com",
    "programing_languages": [
      {
        "name": "Python",
        "years_xp": "3 years"
      },
      {
        "name": "JavaScript",
        "years_xp": "2 years"
      }
    ]
  }
]
```

#### CSV Output (Excel-friendly):

| filename    | name     | email               | programing_languages                  |
| ----------- | -------- | ------------------- | -------------------------------------- |
| resume1.pdf | John Doe | john.doe@example.com | • Python=3 years\n• JavaScript=2 years |

## Project Structure

cv-analyzer/
├─ response_schema.json  # JSON schema for expected CV analysis format or replace with your own
├─ main.py        # Main script
├─ requirements.txt      # Project dependencies
├─ .env                  # API key storage (not included in repository)
├─ README.md             # Project documentation
└─ cv-folder/ # you can add pdf files in here or use you own folder

## Customization

- Modify response_schema.json to define a different expected CV analysis structure.
- Adjust the process_cvs method to customize data processing, formatting, and error handling.

## Troubleshooting

If the script cannot find the API key, ensure:

1. The .env file is correctly set up.

If the script doesn't process files:

- Ensure the correct folder path is provided.
- Check that the folder contains valid PDF files.

## License

This project is licensed under the MIT License. See the LICENSE file for more details.

## Contributing

Feel free to open issues or submit pull requests to improve the project.

## Contact

For questions or support, reach out to:

- Email: brunofarias1@gmail.com
- GitHub: bruno-farias
