# PDFFindText
PDFFindText is a python3 script that searches a PDF for a series of search terms loaded from a JSON file. Each time a search term is found, it is highlighted in yellow or emphasized with a red box inside the PDF and a bookmark is added to the PDF table of contents linking to the search term's exact location.

PDFFindText executes from the command line. Usage:

```
python3 pdffindtext.py -i <FULL_PATH_to_input_PDF> -s <FULL_PATH_to_search_terms_JSON_file> -o <FULL_PATH_to_output_PDF> [--quiet | -q] [--emphasis | -e [highlight | outline ]] | [--help | -h]
```
