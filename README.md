# flagship

The current state:

```py
def main(
  foo: (int, "wow such description"),
  bar: ((int, int), "wow such description"),
  baz: ((int, ...), "wow such description"),
):
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

