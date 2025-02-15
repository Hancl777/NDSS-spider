# NDSS Papers Spider

A web crawler for downloading papers from the Network and Distributed System Security Symposium (NDSS).

## Features

- Download papers from specified NDSS conference year
- Automatically download PDF papers and presentation slides(Video is alternative, just add a button in the paper detail page)
- Save paper information to CSV file
- Support resume download (skip existing files)
- Support Summer/Fall Cycle papers identification
- Automatic filename sanitization and formatting

## Usage

1. Run the program:

```bash
python spider.py
```

2. Enter the year to crawl (e.g., 2024)
3. The program will automatically:
   - Create necessary directories
   - Fetch paper list
   - Download papers and slides
   - Generate CSV file

## Directory Structure

ndss{year}/
├── papers/ # Store paper PDFs
├── slides/ # Store presentation slides
└── paper_list.csv # Paper information list

## CSV File Format

paper_list.csv contains the following columns:

- index: Sequence number (starting from 1)
- title: Paper title
- authors: Author list
- cycle: Paper cycle (Summer/Fall)
- details_url: Paper detail page URL

## Dependencies

```
requests >= 2.31.0
beautifulsoup4 >= 4.12.2
pandas >= 2.1.0
lxml >= 4.9.3
```


## Notes

1. Python 3.8 or higher recommended
2. Existing files will be skipped during download

## Error Handling

The program includes comprehensive error handling for:

- Network connection errors
- File download failures
- Parsing errors
- File saving errors

All errors are logged and displayed without interrupting program execution.

## Code Structure

- `NDSSSpider` class: Main spider class
  - `__init__`: Initialize configuration and paths
  - `create_dirs`: Create necessary directories
  - `sanitize_filename`: Clean filenames
  - `get_paper_list`: Get paper list
  - `download_file`: Download files
  - `get_paper_details`: Get paper details
  - `save_paper_list_to_csv`: Save CSV file
  - `run`: Main execution function
