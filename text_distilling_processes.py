#
# Text processing classes compatible with the 'DistillerNode' class.
# Copyright (C) 2019  Claudio Romero
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
#

"""Text processing classes compatible with the 'DistillerNode' class.

This module contains text processing classes and methods. All data
processing classes contain the 'distill' method and also the 'help' and
'name' attributes (making them compatible with the 'Distillery' and
'DistillerNode' classes). Some classes also represent configurable
processes and as such also contain the optional 'config_process'
method.

"""


import re


def read_text(input_file):
    """Simple method that reads whitespace separated text fragment.

    This method receives and opened input file and reads it character
    by character until it finds a whitespaces or fails to read a new
    character.

    Args:
        inputFile: Alreadey opened text file.

    Returns
        A string of read characters (word).
    """
    word = ''

    while True:
        char = input_file.read(1)
        # pylint: disable=no-else-return
        if (char.isspace()) or (char == ''):
            return word
        else:
            word += char
    return word


class PrintText:
    """Reads and prints to console whitespace separeted text.

    The PrintText class simply reads text a whitespace separated
    text fragment and prints it to the console.

    Attributes:
        help: String that contains a short help text.
        name: String with the name that identifies this process.
    """
    def __init__(self):
        self.help = "Prints extracted data"
        self.name = "PRINTTEXT"

    def distill(self, process_input):
        """Reads and prints whitespace separated text.

        Args:
            input: File handle for a text file.
        Returns:
            The input file handle and a 'None' as a sample.
        """
        text = read_text(process_input)
        print(text)
        return process_input, None


class PrintLine:
    """Reads and prints to console a complete line of text.

    The PrintLine class simply reads a text line and prints it to the
    console.

     Attributes:
        help: String that contains a short help text.
        name: String with the name that identifies this process.
    """
    def __init__(self):
        self.help = "Reads and prints a line of text"
        self.name = "PRINTLINE"

    def distill(self, process_input):
        """Reads and prints to the console a complete line of text.

        Args:
            input: File handle for a text file.
        Returns:
            The input file handle and a 'None' as a sample.
        """
        line = process_input.readline()
        if line:
            print(line)
        else:
            process_input = None
        return process_input, None


class ReadLine:
    """Reads and samples a complete line of text.

    The ReadLine class reads a text line, strips it of any trailing
    whitespaces and samples it. The resulting sample depends on
    'sample_name' (False: str, True: dict).

    Attributes:
        help: String that contains a short help text.
        name: String with the name that identifies this process.
        sample_name: Optional name for the lines read by this process.
        strip_new_line_only: Optional flag that determines if all
            trailing whitespaces are removed or only '\n'.
    """
    def __init__(self, sample_name=None, strip_new_line_only=False):
        self.help = "Reads a line of text"
        self.name = "READLINE"
        self.sample_name = sample_name
        self.strip_new_line_only = strip_new_line_only

    def config_process(self, opt_list):
        """Configures the 'sample_name' and sample format.

        This method simply sets the 'sample_name' attribute, if this
        attribute is set then each line read will be sampled using a
        dictionary using the 'sample_name' attribute as key.

        Args:
            opt_list: List of size 1 that contains a string.
        """
        self.sample_name = opt_list[0]

    def distill(self, process_input):
        """Reads a text line from file handle.

        Args:
            input: File handle for a text file.

        Returns:
            The input file handle or 'None' if no data has been read.
            The read line stripped of all trailing whitespaces or
            only new line ('\n'). If a
            'sample_name' is provided then the line is returned inside
            a dictionary.
        """
        line_data = process_input.readline()

        if not line_data:
            process_input = None
        else:
            if self.strip_new_line_only:
                line_data = line_data.rstrip('\n')
            else:
                line_data = line_data.rstrip()
            if self.sample_name:
                line_data = {self.sample_name: line_data}

        return process_input, line_data


class SkipLine:
    """Reads a complete line of text from a file handle, no sampling.

    The SkipLine class reads a text line simply reads a text line, no
    sampling is performed. This is used to literally skip an undesired
    line in a text fiel.

    Attributes:
        help: String that contains a short help text.
        name: String with the name that identifies this process.
    """
    def __init__(self):
        self.help = "Skips a single line"
        self.name = "SKIPLINE"

    def distill(self, process_input):
        """Reads a text line from file handle.

        Args:
            input: File handle for a text file.

        Returns:
            The input file handle or 'None' if no data has been read.
            Sample is always 'None'.
        """
        if not process_input.readline():
            process_input = None
        return process_input, None


class SkipUntilToken:
    """Reads lines until it finds one containing a specific token.

    The SkipUntilToken class reads text lines until it finds one that
    contains a specific token, no sampling is performed.

    Attributes:
        help: String containing a short help text.
        name: String containing the name that identifies this process.
        token: String token that identifies last line to be skipped.
    """
    def __init__(self, token=None):
        self.help = "Skips lines until it finds a specific token"
        self.name = "SKIPUNTIL"
        self.token = token

    def config_process(self, opt_list):
        """Configures the skip until 'token'.

        This method simply sets the 'token' attribute, this attribute
        is used to identify the last line to be read by this process.

        Args:
            opt_list: List of size 1 that contains a string.
        """
        self.token = opt_list[0]

    def distill(self, process_input):
        """Reads lines until it finds one containing a specific token.

        Args:
            input: File handle for a text file.

        Returns:
            The input file handle or 'None' if no data has been read.
            Sample is always 'None'.
        """
        token_found = False
        line = process_input.readline()
        eof = not bool(line)

        while (not eof) and (not token_found):
            if self.token in line:
                token_found = True
            else:
                line = process_input.readline()
                eof = not bool(line)

        if eof:
            process_input = None

        return process_input, None


class RegexRead:
    """Reads a line of text and extract text using regular expressions.

    The RegexRead class reads a text line, strips it of all
    whitespaces then extracts text using.

    Attributes:
        help: String containing a short help text.
        name: String containing the name that identifies this process.
        regex: String containing the regular expression.
    """
    def __init__(self, regex=None):
        self.help = "Reads text using Regular Expressions"
        self.name = "REGEXREAD"
        self.regex = regex

    def config_process(self, opt_list):
        """Configures the 'regex' variable.

        This method simply sets the 'regex' attribute, this attribute
        is used to extract text using regular expressions.

        Args:
            opt_list: List of size 1 that contains a string.
        """
        self.regex = opt_list[0]

    def _match_regex(self, text_line):
        """Applies regular expression from 'regex' variable.

        Args:
            text_line: Line of text to be processed.

        Returns:
            All instances that match the desired regular expression.
        """
        return re.findall(self.regex, text_line)


    def _cleanup_whitespaces(self, line):
        """Removes all whitespaces from a string.

        Args:
            line: Line of text, possibly with whitespaces..

        Returns:
            The received text string with whitespaces removed.
        """
        return re.sub(r"\s+", "", line)

    def distill(self, process_input):
        """Reads a line and extract data between delimiting tokens.

        Args:
            input: File handle for a text file.

        Returns:
            The input file handle or 'None' if no data has been read.
            Sample contains the extracted data either as a list or a
            dictionary depending on wheter the 'store_names' flag is
            set.
        """
        line = process_input.readline()
        if line:
            clean_line = self._cleanup_whitespaces(line)
            #data = re.findall("\[(.*?)\]", stripTemp)
            #data = re.findall("\\" + self.token1 + "(.*?)\\" + self.token2,
                              #stripTemp)

            data = self._match_regex(clean_line)

        else:
            process_input = None
            data = None

        return process_input, data


class ReadBetweenTokens(RegexRead):
    """Reads a line of text and extract text between tokens.

    The ReadBetweenTokens class reads a text line, strips it of all
    whitespaces then extracts text between tokens. Optionally it may
    attempt to extract field names by extracting everything except
    the text between tokens.

    Attributes:
        help: String containing a short help text.
        name: String containing the name that identifies this process.
        token1: String containing the first delimiter token.
        token2: String containing the second delimiter token.
        store_names: Flag the indicates if names should be extracted.
    """
    def __init__(self, token1=None, token2=None, store_names=False):
        super().__init__()
        self.help = "Reads text between token1 and token2, optionally reads field names"
        self.name = "READBTWTOKENS"
        self.token1 = token1
        self.token2 = token2
        self._set_regex(token1, token2)
        self.store_names = store_names

    def _set_regex(self, token1, token2):
        tk1 = None
        tk2 = None
        if token1 is not None:
            tk1 = token1
        if token2 is not None:
            tk2 = token2
        else:
            tk2 = tk1

        if (tk1 is not None) and (tk2 is not None):
            self.regex = "\\" + tk1 + "(.*?)\\" + tk2

    def config_process(self, opt_list):
        """Configures the delimiter tokens and the store name option.

        This method sets 'token1' and 'token2' attributes, optionally
        the 'store_names' attribute is also set. The attributes are
        set according to 'len(opt_list)':
            1 - 'token1' == 'token2' == 'opt_list[0]'.
            2 - 'token1' == 'opt_list[0] and 'token2' == 'opt_list[1]'.
            3 - The same as 2 and store_names is set to True if
                'opt_list[2]' == 'yes'.

        Args:
            opt_list: List of size 1,2, or 3 that contains strings.
        """
        list_size = len(opt_list)
        if list_size == 1:
            #self.token1 = opt_list[0]
            #self.token2 = opt_list[0]
            self._set_regex(opt_list[0], opt_list[0])
        elif list_size in (2, 3):
            #self.token1 = opt_list[0]
            #self.token2 = opt_list[1]
            self._set_regex(opt_list[0], opt_list[1])
            if list_size == 3:
                self.store_names = opt_list[2] == "yes"
        else:
            raise ValueError(self.name +
                             " process accepts only up to 3 options")

    def distill(self, process_input):
        """Reads a line and extract data between delimiting tokens.

        Args:
            input: File handle for a text file.

        Returns:
            The input file handle or 'None' if no data has been read.
            Sample contains the extracted data either as a list or a
            dictionary depending on wheter the 'store_names' flag is
            set.
        """
        line = process_input.readline()
        if line:
            clean_line = self._cleanup_whitespaces(line)
            # data = re.findall("\[(.*?)\]", stripTemp)
            data = re.findall("\\" + self.token1 + "(.*?)\\" + self.token2,
                              clean_line)

            if self.store_names:
                names = re.sub("\\"+self.token1 + "(.*?)\\" + self.token2,
                               " ",
                               clean_line)
                names = names.split()
                dict_data = dict()
                for i, name in enumerate(names):
                    dict_data[name] = data[i]
                data = dict_data
        else:
            process_input = None
            data = None

        return process_input, data

    def _apply_regex(self, text_line):
        """Applies regular expression from 'regex' variable.

        Args:
            text_line: Line of text to be processed.

        Returns:
            All instances that match the desired regular expression.
        """
        return re.findall(self.regex, text_line)


class ReadBetweenWhitespaces(RegexRead):
    """Reads a line of text and extract text between whitespaces.

    The ReadBetweenWhitespaces class is a special case of the
    ReadBetweenTokens class where whitespaces are significant. A text
    line is read, optionally stripped of repeated whitespaces (as well as
    'end of lines'), then it extracts text between the remaining
    whitespaces. This class explicitly does not attempt to extract field
    names (option is set to False).

    Attributes:
        help: String containing a short help text.
        name: String containing the name that identifies this process.
        clean_whitespaces: flag that indicates wheter repeated
            whitespaces shoould be removed.
    """
    def __init__(self, clean_whitespaces=True):
        whitespace_token = "(.*?)\\s"
        super().__init__(whitespace_token)
        self.help = "Reads text between whitespaces."
        self.name = "READBTWSPACES"
        self.clean_whitespaces = clean_whitespaces

    def config_process(self, opt_list):
        """Replaces base class implementation, should not be called.

        This method should not be called, ReadBetweenWhitespaces does
        not have optional parameters

        Args:
            opt_list: List of size 1,2, or 3 that contains strings.
        """
        raise ValueError(self.name + " does not accept options")

    def _cleanup_whitespaces(self, line):
        """Replaces repeated whitespaces with a single whitespace.

        Args:
            line: Line of text, possibly with whitespaces..

        Returns:
            The received text string with repeated whitespaces removed.
        """
        if self.clean_whitespaces:
            line = re.sub('\s+', ' ', line)
        line = line.rstrip()
        
        return line + " "

class MultipleRegexRead(RegexRead):
    """Reads and matches a line of text to multiple Regular expressions.

    The MultipleRegexRead class is very similar to the RegexRead class
    but instead of looking for matches to a single regular expression
    it check multiple regular expressions.

    Attributes:
        help: String containing a short help text.
        name: String containing the name that identifies this process.
        regex_dict: Dict of regular regular expressions and their identifiers.
        exclusive_match: flag that indicates wheter or not regular
            expression matching continues once a match is found.
        clean_whitespaces: flag that indicates if whitespaces should
            be cleaned or not.
    """
    def __init__(self, exclusive_match, clean_whitespaces=True, regex_dict = {}):
        super().__init__()
        self.help = "Reads text using multiple Regular Expressions"
        self.name = "MULTIREGEXREAD"
        self.exclusive_match = exclusive_match
        self.clean_whitespaces = clean_whitespaces
        self.regex_dict = regex_dict

    def config_process(self, opt_list):
        """Configures option flags and list of regular expressions.

        This method always sets the 'exclusive_match' and 'clean_whitespaces'
        attributes, optionally it also replaces the regular expressions present
        in 'regex_list'. The attributes are set according to 'len(opt_list)':
            2 - 'exclusive_match' is set to True if 'opt_list[0]' == 'yes',
                'clean_whitespaces' == is set to True if 'opt_list[1]' == 'yes'.
            4 or more (only even values are supported) - The same as 2 and
                regex_dict is built from 'opt_list[2:]'.

        Args:
            opt_list: List of size 2 or more that contains strings.

        """

        list_size = len(opt_list)
        list_size_is_even = (list_size % 2 == 0)
        if (list_size >= 2) and list_size_is_even:
            self.exclusive_match = opt_list[0] == "yes"
            self.clean_whitespaces = opt_list[1] == "yes"

            if list_size > 2:
                it = iter(opt_list[2:])
                listOfTuples = zip(it, it)
                self.regex_dict = dict(listOfTuples)
                #print(self.regex_dict)
        else:
            raise ValueError(self.name +
                             " process requires an even number of options")

    def _cleanup_whitespaces(self, line):
        """Clean_up as RegexRead or no clean_up.

        Args:
            line: Line of text, possibly with whitespaces..

        Returns:
            The received text string with whitespaces removed or unchanged.
        """
        if self.clean_whitespaces:
            line = super()._cleanup_whitespaces(line)

        return line

    def _match_regex(self, text_line):
        """Applies multiple regular expressions from 'regex_list' variable.

        Args:
            text_line: Line of text to be processed.

        Returns:
            If 'exclusive_match' is True then return a list with all
            instances that match the desired regular expression.
            If 'exclusive_match' is False then returns a list of tuples,
            each tuple contains the regular expression and all instances
            that matched it.
        """
        match_found = False
        result_dict = {}
        for regex_id, regex in self.regex_dict.items():
            if not (match_found and self.exclusive_match):
                self.regex = regex
                temp = super()._match_regex(text_line)

                if temp:
                    match_found = True
                    result_dict.update({regex_id : temp})

        return result_dict
