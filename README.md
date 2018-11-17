# flagship

The current goal:

```py
def main(
  foo: (int, "wow such description"),
  bar: ((int, int), "wow such description"),
  baz: ((int, ...), "wow such description"),
):
```

Logic:

  - If it's a tuple of length 2, we check if the second value is a description
    by checking if it's a string
  - Otherwise, it's just a type

