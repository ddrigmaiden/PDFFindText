#!/usr/bin/env python3

# PDFFindText v.1.0 by Daniel Rigmaiden (danielrigmaiden at protonmail dot com)
# Source: https://github.com/ddrigmaiden/PDFFindText
#
# This script is licensed under The MIT License (see LICENSE for more information).


import sys, getopt, os, fitz, json
from collections import namedtuple
from fitz import Point


# function to display usage

def usage():
    print('Usage: python3 pdffindtext.py -i <FULL_PATH_to_input_PDF> -s <FULL_PATH_to_search_terms_JSON_file> -o <FULL_PATH_to_output_PDF> [--quiet | -q] [--emphasis | -e [highlight | outline ]] | [--help | -h]')


# function to process the input pdf

def process_pdf():

    # import the already defined constants into the function (Q: You're not using function parameters and return values? A: No. The values never change, so it would just be a distraction. We instead force Python to support constants.)

    constants = ConstantsNamespace().constants

    # check if the input pdf file exists and exit if it does not

    if not os.path.exists(constants.INPUT_PDF):
        print('The input PDF file does not exist.')
        sys.exit(2)

    # check if the json search terms file exists and exit if it does not

    if not os.path.exists(constants.SEARCH_TERMS_JSON):
        print('The JSON search terms file does not exist.')
        sys.exit(2)

    # check if the path to the output pdf file exists and exit if it does not

    if not os.path.exists(os.path.dirname(constants.OUTPUT_PDF)):
        print('The path to the output PDF file does not exist.')
        sys.exit(2)

    # load the input pdf into a variable using MuPDF

    loadedpdf = fitz.open(constants.INPUT_PDF)

    # define variables to track page count and to store output pdf table of contents

    page_count = 0
    toc = []

    # for each page in the loaded pdf file

    for page in loadedpdf:

        # advance the page count

        page_count = page_count + 1

        # print to the terminal the page number being worked on

        if not constants.QUIET:
            print('\nPDF Page: ' + str(page_count))

        # re[set] the search term set match count

        term_set_count = 0

        # set the search term match count

        term_match_count = 0

        # open the json search terms file

        f = open(constants.SEARCH_TERMS_JSON)
        
        # return json object dictionary

        data = json.load(f)

        # close the json file 

        f.close()

        # load the text search terms as a list

        search_terms = data['text_terms'];

        # search the loaded pdf for the terms and add coordinates of each found term into term_instances list

        term_instances = [page.search_for(term) for term in search_terms]

        # iterate through each set of matches for each found search term

        for set in term_instances:

            # check if the set is an empty list (i.e., no matches found on the pdf page)

            if not set:

                # advance the term_set_count and skip to next set

                term_set_count = term_set_count +1

                continue

            # iterate through each match within the set for the applicable search term

            for match in set:

                # advance the term match count for the page

                term_match_count = term_match_count + 1

                # use MuPDF to highlight or box outline the search term match on the pdf page
                # see https://stackoverflow.com/questions/47497309/find-text-position-in-pdf-file

                if constants.EMPHASIS == 'highlight':
                    annot = page.add_highlight_annot(match)
                
                if constants.EMPHASIS == 'outline':
                    annot = page.add_rect_annot(match)
                    
                annot.update()

                # get the vertical position of the matched term on the page using the second Rect value of match location

                vertical_position = match[1]

                # use MuPDF to add a table of contents entry for the matched search term, linking to the page and vertical position of the match
                # see https://pymupdf.readthedocs.io/en/latest/document.html#Document.set_toc
                # see https://github.com/pymupdf/PyMuPDF/discussions/1301

                toc = toc + [[1,search_terms[term_set_count],page_count,{"kind":1, "page":page_count-1, "to": Point(0,vertical_position)}]]

            # print to the terminal which search term matches are being processed

            if not constants.QUIET:
                print('Processed ' + str(term_match_count) + ' search term matches for: ' + search_terms[term_set_count])

            # starting next set of matches so advance the term set count to reference the next matched term

            term_set_count = term_set_count +1

            # starting next set of matches so reset the term match count so it can count the occurances of the term match

            term_match_count = 0

    # alphabetize the toc

    toc.sort(key=lambda x:x[1])

    # add the created table of contents to the pdf file

    loadedpdf.set_toc(toc)

    # save the pdf output to the output file location

    loadedpdf.save(constants.OUTPUT_PDF)


# set constants (Q: I thought Python's inferiority prevented constants? A: This is how you do constants in Python.)

class ConstantsNamespace:

    _instance = None
    constants = None

    # use namedtuple to prevent the constants from being modified in place after the class is initiated
    # see https://realpython.com/python-constants/

    Namespace = namedtuple('Namespace', ['INPUT_PDF', 'SEARCH_TERMS_JSON', 'OUTPUT_PDF', 'QUIET', 'EMPHASIS'])

    # receive five command line arguments to become constants

    def __init__(self, inputpdf = None, searchtermsjson = None, outputpdf = None, quiet = None, emphasis = None):

        # only set the namedtuple if still equals None because class is a singleton (Q: Why do you use singletons when my professor told me they are bad? A: This is how you do constants in Python.)

        if self.constants is None:
            self.constants = self.Namespace(inputpdf, searchtermsjson, outputpdf, quiet, emphasis)
        
    # make the class a singleton so constants cannot be redefined with new instances
    # see https://www.pythonforthelab.com/blog/singletons-instantiate-objects-only-once/

    def __new__(cls, *args, **kwargs):
        if not isinstance(cls._instance, cls):
            cls._instance = object.__new__(cls)

        return cls._instance


# function to read and process command line arguments

def main(argv):

    inputpdf = None
    searchtermsjson = None
    outputpdf = None
    quiet = False
    emphasis = 'outline'

    error = False

    try:
        opts, args = getopt.getopt(argv,'hi:s:o:qe:',['help','input=','search=','output=','quiet','emphasis='])
    except getopt.GetoptError as err:
        print(err)
        usage()
        sys.exit(2)

    if len(opts) != 0:
        for opt, arg in opts:
            if opt in ('-h', '--help'):
                usage()
                sys.exit(2)
            elif opt in ('-i', '--input'):
                inputpdf = arg
            elif opt in ('-s', '--search'):
                searchtermsjson = arg
            elif opt in ('-o', '--output'):
                outputpdf = arg
            elif opt in ('-q', '--quiet'):
                quiet = True
            elif opt in ('-e', '--emphasis'):
                emphasis = arg
        if not inputpdf: # if no input pdf file specified
            error = True
            print('You must specify an input PDF file to process.')
        elif not searchtermsjson: # if no json file of search terms specified
            error = True
            print('You must specify a JSON file containing search terms.')
        elif not outputpdf: # if output file not specified
            error = True
            print('You must specify an output PDF file name.')
        elif emphasis != 'highlight' and emphasis != 'outline': # if emphasis has unsupported argument
            error = True
            print('Emphasis option takes argument of either "highlight" or "outline".'+emphasis)
    else:
        # if no arguments specified
        error = True

    if (error):
        usage()
        sys.exit(2)
    else:

        # turn the variables defined from the command line arguments into constants ("constants.constants.INPUT_PDF", etc.)

        constants = ConstantsNamespace(inputpdf, searchtermsjson, outputpdf, quiet, emphasis)

        # shorten this

        constants = constants.constants

        # try and fail to change the constants as a test if you like

        '''
        constants = ConstantsNamespace("you","can't","change","these","constants").constants
        print(str(constants))
        '''

        # try and fail to change them in place

        '''
        constants.INPUT_PDF = "you can't change this"
        print(constants.INPUT_PDF)
        '''

        # try and fail to change them using a new object with a new instance

        '''
        constants2 = ConstantsNamespace("you","can't","define","new","constants").constants
        print(str(constants2))
        '''

        # process the PDF file

        process_pdf()

if __name__ == '__main__':
    main(sys.argv[1:])
