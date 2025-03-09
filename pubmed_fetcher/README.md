
# PubMed Fetcher

A Python tool to fetch PubMed articles and extract author affiliations with pharmaceutical/biotech companies.

## Prerequisites

- Python 3.9 or higher
- Poetry (Python package manager)
- Gemini API key

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/pubmed-fetcher.git
cd pubmed-fetcher
```

2. Install dependencies using Poetry:
```bash
poetry install
```

3. Create a `.env` file in the project root and add your Gemini API key:
```bash
GEMINI_API_KEY=your_api_key_here
```

## Usage

1. Activate the Poetry virtual environment:
```bash
poetry shell
```

2. Run the script with your search query:
```bash
python fetch_pubmed.py "cancer drug resistance" -d -f output.csv
```

### Command Line Arguments

- `--query`: Your PubMed search query (required)
- `--output`: Output CSV file name (default: output.csv)
- `--debug`: Enable debug mode for verbose output (optional)

Example:
```bash
python fetch_pubmed.py --query "CRISPR cancer therapy" --output crispr_results.csv --debug
```

## Output

The script generates a CSV file containing:
- Article titles
- Authors and their affiliations
- Publication dates
- DOIs
- Company affiliations (if any)

## Project Structure

```
pubmed-fetcher/
├── .env                    # Environment variables (create this)
├── .gitignore             # Git ignore rules
├── README.md              # This file
├── pyproject.toml         # Poetry project configuration
├── poetry.lock           # Poetry lock file
└── fetch_pubmed.py       # Main script
```

## Dependencies

- requests: HTTP requests to PubMed API
- xmltodict: XML parsing
- pandas: Data handling and CSV export
- google-generativeai: Gemini AI for query processing
- python-dotenv: Environment variable management

## Development

To contribute to this project:

1. Fork the repository
2. Create a new branch for your feature
3. Make your changes
4. Submit a pull request

## Troubleshooting

If you encounter any issues:

1. Ensure Python 3.9+ is installed:
```bash
python --version
```

2. Verify Poetry is installed correctly:
```bash
poetry --version
```

3. Check if all dependencies are installed:
```bash
poetry show
```

4. Verify your `.env` file contains the correct API key

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Author

Suraj Kumar <ksuraj2235@gmail.com>
