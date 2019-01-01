# flagship

Flagship provides a concise way of defining your command line interface (CLI).
Using the `argparse` API is verbose and full of repetition. Flagship uses
python's type annotations and doc string support to generate your CLI with a
decorator.

## Example
```py
from enum import Enum
from typing import List, Tuple
from flagship import derive_flags

Suite = Enum("Suite", "Hearts Spades Clubs Diamonds")

@derive_flags()
def main(
    p1: (int, "description for p1"),
    p2: List[float],
    p3: Suite = Suite.Diamonds,
    p4: (Tuple[int, int], "description for p4") = (3, 2),
    p5: (bool, "description for p5") = True,
):
    """This is main."""
    pass

if __name__ == "__main__":
    main()
```

produces (via. `argparse`)

```
usage: flagship.py [-h] [--p3 {Hearts, Spades, Clubs, Diamonds}] [--p4 P4 P4]
                   [--p5]
                   p1 [p2 [p2 ...]]

This is main.

positional arguments:
  p1                    description for p1 (type: `int`)
  p2                    (type: `List[float]`)

optional arguments:
  -h, --help            show this help message and exit
  --p3 {Hearts, Spades, Clubs, Diamonds}
                        (type: `Suite`) (default: `Suite.Diamonds`)
  --p4 P4 P4            description for p4 (type: `Tuple[int, int]`) (default:
                        `(3, 2)`)
  --p5                  description for p5 (action: `store_false`) (default:
                        `True`)
```

## Logic
`@derive_flags` takes your main function and turns it into a CLI. The help
description comes from `main.__doc__`. Flag names are derived from the parameter
names. Positional arguments become positional flags and kew word arguments
become optional flags. The flag's accepted types and number of arguments are
derived from the annotation, using python's `typing` and `enum` packages. The
annotation may be a tuple of the type and a string description. This description
is attached to the flag argument.

### TODO
* Document `init_objects_from_commandline`
* Design a way to facilitate multiple entrance with mutually exclusive flags
* Reveal more argparse features like metavar, short flags
