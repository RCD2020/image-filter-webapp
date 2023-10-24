# Image Filter Webapp

This Flask application allows users to write custom filters using my custom micro programming language to alter their own images.


## Setup

To use Image Filter Webapp, clone the depository, and install the `requirements.txt` using pip (python3+). You can do that by running `pip install -r requirements.txt` in the terminal. After that, you can just run app.py and it will tell you the address to connect to in the terminal.


## Explanation

The most interesting part of this whole project would have to be the micro programming language I implemented using Python. If you take a look at `imgfilter.py`, you'll see a thousand lines of code, maticulously commented throughout that explains how it works, but for a general overview, you can look here.


### `InputStream`

The `InputStream` class is the basis of the whole programming language. You input the user generated code, and it gives you the ability to read through each character of the code, keeping track of the position that the cursor is, and won't allow us to go past the last character of the code. Useful functions are `next`, which will return the next character as well as move the cursor, and `peek` will also return the next character but without moving the cursor. This is useful because depending on what the next character is in the code can vastly change how to handle the current character.


### `Token` and friends

After the `InputStream`, I've implemented several slightly different Token classes that will become useful later for classifying segments of code in an interpretable way.


### `Tokenizer`

The `Tokenizer` will make use of our previously defined `Token` classes and utilizing the `InputStream`, convert chunks of characters into tokens, skip comments, handle newlines, and more. The first part is a handful of methods that validate whether inputted characters can potentially be the type specified by the method name. After those, we have our `readWhile` method, that when given a predicate (one of our previously defined validation methods), will keep reading the `InputStream` until we reach a character that does not pass the predicate, and then will return the collection of characters. After that, we have a few methods that will turn our data into Tokens or skip comments. Then the `readNext` method, that will read the next chunk of data and return a Token making use of all our previous methods. Then finally finishing off with a few methods that will allow us to navigate the Tokens.

### `Parser`

The `Parser` reads through all the tokens given by the `Tokenizer`, and groups them together in a very natural way to be interpreted. It will do things, like determine order of operations, bundle together if statements and for loops, and create different Tokens that will be even more useful to the interpreter. It starts with a few methods that will be useful for determining different code structures, like punctuation, keywords, operators, and then follows those methods with methods that will group together binary operations like assignment, comparisons, and operators. Then something that can parse delimited statements, as seen in function calls. Then we get into methods that will return tokens that indicate call a function and indexing our image. Then methods to parse statements like for loops, if statements, and lambdas. Then finally we end with our methods that loop through `Tokenizer` and puts everything in their buckets.

### `Environment`

The `Environment` class is basically a dictionary to keep track of all of our variables, except it has the additional functionality of keeping track of scope, and accessing variables even if they are in the parent scope.

### `ImgFilter`

Finally, the last part of our micro programming language, the interpreter. This will utilize everything that came before it to run our custom code. It uses the Pillow library to access a given image, it creates the global scope and fills it with useful variables and functions to alter our image, and then it will evaluate all the code using the tokens we've generated thus far.