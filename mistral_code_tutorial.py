"""  
                                 Chat, Edit, and Autocomplete tutorial
"""


# —————————————————————————————————————————————————     Chat      ————————————————————————————————————————————————— #

## Highlight the code below
## Press [Cmd/Ctrl + J] to add to Chat
## Try asking Mistral Code "what sorting algorithm is this?"
def sorting_algorithm(x):
    for i in range(len(x)):
        for j in range(len(x) - 1):
            if x[j] > x[j + 1]:
                x[j], x[j + 1] = x[j + 1], x[j]
    return x


# —————————————————————————————————————————————————     Edit      ————————————————————————————————————————————————— #

## Highlight the code below
## Press [Cmd/Ctrl + I] to Edit
## Try asking Mistral Code to "make this more readable"
def sorting_algorithm(x):
    for i in range(len(x)):
        for j in range(len(x) - 1):
            if x[j] > x[j + 1]:
                x[j], x[j + 1] = x[j + 1], x[j]
    return x

# —————————————————————————————————————————————     Autocomplete     —————————————————————————————————————————————— #

## Place cursor after `sorting_algorithm...` below and press [Enter]
## Press [Tab] to accept the Autocomplete suggestion

# Basic assertion for sorting_algorithm...
