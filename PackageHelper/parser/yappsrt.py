#
# Yapps 2 Runtime, part of Yapps 2 - yet another python parser system
# Copyright 1999-2003 by Amit J. Patel <amitp@cs.stanford.edu>
#
# This version of the Yapps 2 Runtime can be distributed under the
# terms of the MIT open source license, either found in the LICENSE file
# included with the Yapps distribution
# <http://theory.stanford.edu/~amitp/yapps/> or at
# <http://www.opensource.org/licenses/mit-license.php>
#

"""Run time libraries needed to run parsers generated by Yapps.

This module defines parse-time exception classes, a scanner class, a
base class for parsers produced by Yapps, and a context class that
keeps track of the parse stack.

"""

# TODO: it should be possible to embed yappsrt into the generated
# grammar to make a standalone module.

import sys, re

class SyntaxError(Exception):
    """When we run into an unexpected token, this is the exception to use"""
    def __init__(self, charpos=-1, msg="Bad Token", context=None):
        Exception.__init__(self)
        self.charpos = charpos
        self.msg = msg
        self.context = context
        
    def __str__(self):
        if self.charpos < 0: return 'SyntaxError'
        else: return 'SyntaxError@char%s(%s)' % (repr(self.charpos), self.msg)

class NoMoreTokens(Exception):
    """Another exception object, for when we run out of tokens"""
    pass

class Scanner:
    """Yapps scanner.

    The Yapps scanner can work in context sensitive or context
    insensitive modes.  The token(i) method is used to retrieve the
    i-th token.  It takes a restrict set that limits the set of tokens
    it is allowed to return.  In context sensitive mode, this restrict
    set guides the scanner.  In context insensitive mode, there is no
    restriction (the set is always the full set of tokens).
    
    """
    
    def __init__(self, patterns, ignore, input):
        """Initialize the scanner.

        Parameters:
          patterns : [(terminal, uncompiled regex), ...] or None
          ignore : [terminal,...]
          input : string

        If patterns is None, we assume that the subclass has
        defined self.patterns : [(terminal, compiled regex), ...].
        Note that the patterns parameter expects uncompiled regexes,
        whereas the self.patterns field expects compiled regexes.
        """
        self.tokens = [] # [(begin char pos, end char pos, token name, matched text), ...]
        self.restrictions = []
        self.input = input
        self.pos = 0
        self.ignore = ignore
        self.first_line_number = 1
        
        if patterns is not None:
            # Compile the regex strings into regex objects
            self.patterns = []
            for terminal, regex in patterns:
                self.patterns.append( (terminal, re.compile(regex)) )

    def get_token_pos(self):
        """Get the current token position in the input text."""
        return len(self.tokens)

    def get_char_pos(self):
        """Get the current char position in the input text."""
        return self.pos
    
    def get_prev_char_pos(self, i=None):
        """Get the previous position (one token back) in the input text."""
        if self.pos == 0: return 0
        if i is None: i = -1
        return self.tokens[i][0]
    
    def get_line_number(self):
        """Get the line number of the current position in the input text."""
        # TODO: make this work at any token/char position
        return self.first_line_number + self.get_input_scanned().count('\n')

    def get_column_number(self):
        """Get the column number of the current position in the input text."""
        s = self.get_input_scanned()
        i = s.rfind('\n') # may be -1, but that's okay in this case
        return len(s) - (i+1)
    
    def get_input_scanned(self):
        """Get the portion of the input that has been tokenized."""
        return self.input[:self.pos]

    def get_input_unscanned(self):
        """Get the portion of the input that has not yet been tokenized."""
        return self.input[self.pos:]

    def token(self, i, restrict=None):
        """Get the i'th token in the input.

        If i is one past the end, then scan for another token.
        
        Args:

        restrict : [token, ...] or None; if restrict is None, then any
        token is allowed.  You may call token(i) more than once.
        However, the restrict set may never be larger than what was
        passed in on the first call to token(i).
        
        """
        #print "LOG ", i, " ", restrict
        if i == len(self.tokens):
            self.scan(restrict)
        if i < len(self.tokens):
            # Make sure the restriction is more restricted.  This
            # invariant is needed to avoid ruining tokenization at
            # position i+1 and higher.
            if restrict and self.restrictions[i]:
                for r in restrict:
                    if r not in self.restrictions[i]:
                        #print " R: ", r, " not in ", self.restrictions[i]
                        #print self.restrictions
                        raise NotImplementedError("Unimplemented: restriction set changed")
            return self.tokens[i]
        raise NoMoreTokens()
    
    def __repr__(self):
        """Print the last 10 tokens that have been scanned in"""
        output = ''
        for t in self.tokens[-10:]:
            output = '%s\n  (@%s)  %s  =  %s' % (output,t[0],t[2],repr(t[3]))
        return output
    
    def scan(self, restrict):
        """Should scan another token and add it to the list, self.tokens,
        and add the restriction to self.restrictions"""
        #print "Scanning: ", restrict
        # Keep looking for a token, ignoring any in self.ignore
        while 1:
            # Search the patterns for the longest match, with earlier
            # tokens in the list having preference
            best_match = -1
            best_pat = '(error)'
            for p, regexp in self.patterns:
                # First check to see if we're ignoring this token
                if restrict and p not in restrict and p not in self.ignore:
                    continue
                m = regexp.match(self.input, self.pos)
                if m and len(m.group(0)) > best_match:
                    # We got a match that's better than the previous one
                    best_pat = p
                    best_match = len(m.group(0))
                    
            # If we didn't find anything, raise an error
            if best_pat == '(error)' and best_match < 0:
                msg = 'Bad Token'
                if restrict:
                    msg = 'Trying to find one of '+', '.join(restrict)
                raise SyntaxError(self.pos, msg)

            # If we found something that isn't to be ignored, return it
            if best_pat not in self.ignore:
                # Create a token with this data
                token = (self.pos, self.pos+best_match, best_pat,
                         self.input[self.pos:self.pos+best_match])
                self.pos = self.pos + best_match
                # Only add this token if it's not in the list
                # (to prevent looping)
                if not self.tokens or token != self.tokens[-1]:
                    self.tokens.append(token)
                    self.restrictions.append(restrict)
                return
            else:
                # This token should be ignored ..
                self.pos = self.pos + best_match

class Parser:
    """Base class for Yapps-generated parsers.

    """
    
    def __init__(self, scanner):
        self._scanner = scanner
        self._pos = 0
        
    def _peek(self, *types):
        """Returns the token type for lookahead; if there are any args
        then the list of args is the set of token types to allow"""
        tok = self._scanner.token(self._pos, types)
        return tok[2]
        
    def _scan(self, type):
        """Returns the matched text, and moves to the next token"""
        tok = self._scanner.token(self._pos, [type])
        if tok[2] != type:
            raise SyntaxError(tok[0], 'Trying to find '+type+' :'+ ' ,'.join(self._scanner.restrictions[self._pos]))
        self._pos = 1 + self._pos
        return tok[3]

class Context:
    """Class to represent the parser's call stack.

    Every rule creates a Context that links to its parent rule.  The
    contexts can be used for debugging.

    """
    
    def __init__(self, parent, scanner, tokenpos, rule, args=()):
        """Create a new context.

        Args:
        parent: Context object or None
        scanner: Scanner object
        pos: integer (scanner token position)
        rule: string (name of the rule)
        args: tuple listing parameters to the rule

        """
        self.parent = parent
        self.scanner = scanner
        self.tokenpos = tokenpos
        self.rule = rule
        self.args = args

    def __str__(self):
        output = ''
        if self.parent: output = str(self.parent) + ' > '
        output += self.rule
        return output
    
def print_line_with_pointer(text, p):
    """Print the line of 'text' that includes position 'p',
    along with a second line with a single caret (^) at position p"""

    # TODO: separate out the logic for determining the line/character
    # location from the logic for determining how to display an
    # 80-column line to stderr.
    
    # Now try printing part of the line
    text = text[max(p-80, 0):p+80]
    p = p - max(p-80, 0)

    # Strip to the left
    i = text[:p].rfind('\n')
    j = text[:p].rfind('\r')
    if i < 0 or (0 <= j < i): i = j
    if 0 <= i < p:
        p = p - i - 1
        text = text[i+1:]

    # Strip to the right
    i = text.find('\n', p)
    j = text.find('\r', p)
    if i < 0 or (0 <= j < i): i = j
    if i >= 0:
        text = text[:i]

    # Now shorten the text
    while len(text) > 70 and p > 60:
        # Cut off 10 chars
        text = "..." + text[10:]
        p = p - 7

    # Now print the string, along with an indicator
    print >>sys.stderr, '> ',text
    print >>sys.stderr, '> ',' '*p + '^'
    
def print_error(input, err, scanner):
    """Print error messages, the parser stack, and the input text -- for human-readable error messages."""
    # NOTE: this function assumes 80 columns :-(
    # Figure out the line number
    line_number = scanner.get_line_number()
    column_number = scanner.get_column_number()
    print >>sys.stderr, '%d:%d: %s' % (line_number, column_number, err.msg)

    context = err.context
    if not context:
        print_line_with_pointer(input, err.charpos)
        
    while context:
        # TODO: add line number
        print >>sys.stderr, 'while parsing %s%s:' % (context.rule, tuple(context.args))
        print_line_with_pointer(input, context.scanner.get_prev_char_pos(context.tokenpos))
        context = context.parent

def wrap_error_reporter(parser, rule):
    try:
        return getattr(parser, rule)()
    #except SyntaxError, e:
    #    input = parser._scanner.input
    #    print_error(input, e, parser._scanner)
    except NoMoreTokens:
        print >>sys.stderr, 'Could not complete parsing; stopped around here:'
        print >>sys.stderr, parser._scanner
