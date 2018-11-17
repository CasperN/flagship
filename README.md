# flagship

The current state:

```py
@derive_flags
def main(
    foo: int,
    bar: ((int, int), "wow such description") = 40,
    baz: (int, ...) = 400,
):
    """This is main.
    """
```

produces (via. `argparse`)

```
python3 flagship.py --help
usage: flagship.py [-h] [--bar BAR BAR] [--baz BAZ [BAZ ...]] foo

This is main.

positional arguments:
  foo                  (type:`int`)

optional arguments:
  -h, --help           show this help message and exit
  --bar BAR BAR        wow such description (type:`(int, int)`) (default:
                       `40`)
  --baz BAZ [BAZ ...]  wow cool (type:`(int, ...)`) (default: `400`)
```

Logic:

  - If it's a tuple of length 2, we check if the second value is a description
    by checking if it's a string
  - Otherwise, it's just a type

