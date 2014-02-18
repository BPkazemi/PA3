README
======
ID: mlp5ab, bp5xj

We decided to use PLY for PA3 because it seemed to be a mature and easy to use package for our needs. The first thing that we did in creating out parser was to derive a clean and functional Context Free Grammar from the spec given in the Cool Reference Manual. We had to make a fair number of changes because the spec in the reference manual cuts corners and uses regular expression notations that we were unfortunately unable to use with PLY.  This grammar can be seen throughout the docstrings in the main.py file.

The second task was to implement a faux Lexer class that we could manually fill with the tokens that we lexed in PA2. We implemented the interface add_token(token) to add a new token to the underlying token queue, and token(self) to remove a token from the queue to be fed to the parser.

To implement the Abstract Syntax Tree, we implemented a Node class that held a type, list of children, and a leaf attribute that held other relevant information depending on the type of node. The most interesting production of the grammar was that of let. Not only were the grammar rules the most complex, but the nodes associated with let held much more information than any other node. The node held a dictionary with the let token for line number reasons, and a list of binding nodes. Overall, we found that we needed to customize many of the node types to make our implementation work, but the simple design of our node class made this very easy.

This was a difficult yet rewarding assignment, and getting hands on experience working with Context Free Grammars greatly helped in gaining understanding of a seemingly theoretical concept.