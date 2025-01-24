import argparse
import os
import json
import csv
import pypdf
import requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class CVAnalyzer:
    def __init__(self, pdf_folder, openai_api_key, openai_endpoint='https://api.openai.com/v1/chat/completions'):
        """Initialize CV Analyzer with PDF folder and OpenAI API details"""
        self.pdf_folder = pdf_folder
        self.openai_endpoint = openai_endpoint
        self.headers = {
            'Authorization': f'Bearer {openai_api_key}',
            'Content-Type': 'application/json'
        }

        # Load response schema
        with open('response_schema.json', 'r') as f:
            self.response_schema = json.load(f)

        self.extraction_features = {
            key: True for key in self.response_schema.keys()
        }

    def extract_pdf_text(self, pdf_path):
        """Extract text from PDF file"""
        with open(pdf_path, 'rb') as file:
            reader = pypdf.PdfReader(file)
            text = ''
            for page in reader.pages:
                text += page.extract_text()
        return text

    def analyze_cv_with_openai(self, cv_text):
        """Send CV text to OpenAI model for analysis"""

        with open('response_schema.json', 'r') as f:
            self.response_schema = json.load(f)

        try:
            payload = {
                'model': 'gpt-4o-mini',
                'messages': [
                    {"role": "system",
                        "content": "You are a helpful assistant trained to analyze CVs."},
                    {"role": "user", "content": cv_text}
                ],
                'response_format': {
                    "type": "json_schema",
                    # Passing the JSON schema loaded from the file
                    "json_schema": self.response_schema
                }
            }

            response = requests.post(self.openai_endpoint,
                                     headers=self.headers,
                                     json=payload)

            response_data = response.json()

            analysis = json.loads(
                response_data['choices'][0]['message']['content'])

            # Check for API errors in the response
            if 'error' in response_data:
                raise Exception(response_data['error']['message'])

            return analysis

        except Exception as e:
            print(f"Error analyzing CV: {e}")
            return {'parsing_error': str(e)}

    def process_cvs(self, output_format='json'):
        """Process all CVs in the specified folder"""
        analyzed_cvs = []

        for filename in os.listdir(self.pdf_folder):
            if filename.endswith('.pdf'):
                try:
                    print(f"Processing {filename}")
                    pdf_path = os.path.join(self.pdf_folder, filename)
                    cv_text = self.extract_pdf_text(pdf_path)

                    if len(cv_text) > 10000:
                        cv_text = cv_text[:10000]

                    analysis = self.analyze_cv_with_openai(cv_text)
                    analysis['filename'] = filename
                    analyzed_cvs.append(analysis)

                except Exception as e:
                    print(f"Error processing {filename}: {e}")
                    analyzed_cvs.append({
                        'filename': filename,
                        'error': str(e)
                    })

        if output_format == 'json':
            with open('cv_analysis.json', 'w') as f:
                json.dump(analyzed_cvs, f, indent=2)
        else:
            with open('cv_analysis.csv', 'w', newline='') as f:
                all_keys = set()
                for cv in analyzed_cvs:
                    all_keys.update(cv.keys())

                # Load response schema to dynamically detect list-based fields
                with open('response_schema.json', 'r') as schema_file:
                    schema = json.load(schema_file)

                list_fields = {
                    key: properties for key, properties in schema["schema"]["properties"].items()
                    if properties["type"] == "array"
                }

                def format_nested_list(data, level=0):
                    """Recursively format nested list items with bullet points and indentation."""
                    indent = '\t' * level  # Tab indentation for nested levels
                    bullet = "• "  # Bullet symbol for list items

                    if isinstance(data, list):
                        return '\n'.join([
                            f"{indent}{bullet}{format_nested_list(
                                item, level + 1)}" if isinstance(item, dict) else f"{indent}{bullet}{item}"
                            for item in data
                        ])
                    elif isinstance(data, dict):
                        return ', '.join([
                            f"{key}={format_nested_list(
                                value, level + 1)}" if isinstance(value, (list, dict)) else f"{key}={value}"
                            for key, value in data.items()
                        ])
                    return str(data)

                processed_cvs = []
                for cv in analyzed_cvs:
                    processed_cv = {}
                    for key, value in cv.items():
                        if key in list_fields and isinstance(value, list):
                            processed_cv[key] = format_nested_list(value)
                        else:
                            processed_cv[key] = value
                    processed_cvs.append(processed_cv)

                writer = csv.DictWriter(f, fieldnames=list(all_keys))
                writer.writeheader()
                writer.writerows(processed_cvs)

        return analyzed_cvs


def main():
    parser = argparse.ArgumentParser(
        description="Analyze CVs from a specified folder.")
    parser.add_argument('folder', type=str,
                        help='Path to the folder containing CV PDFs')
    parser.add_argument('--output', type=str, choices=[
                        'json', 'csv'], default='csv', help='Output format (json or csv, default is csv)')

    args = parser.parse_args()

    API_KEY = os.getenv('OPENAI_API_KEY')

    if not API_KEY:
        raise Exception(
            "OpenAI API key not found. Please set the OPENAI_API_KEY environment variable.")

    analyzer = CVAnalyzer(args.folder, API_KEY)
    results = analyzer.process_cvs(output_format=args.output)

    print(f"Processed {len(results)} CVs. Results saved in {
          args.output} format.")


if __name__ == '__main__':
    main()
