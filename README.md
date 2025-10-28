# Pydantic Models for IOR

This project is a very simple library designed only to parse results
from IOR into Pydantic models, with the following conversions:

- Field names are converted to consistent snake case (e.g.,
  `Tests[x]->TestID`, `Parameters->testID` fields in IOR are both
  converted to `test_id`).
- Size strings are always converted to integer bytes (`4 KiB` -> `4096`)
- Fields with an implicit unit (e.g., `xsizeMiB`) are always converted
  to bytes.
- Output values which are derived from integer-only parameters, such as
  the transfer size, are returned as integers instead of floats.
- Timestamps are converted to native Python datetime objects
- Boolean parameters such as `readFile`/`writeFile` are still returned
  as integers, but you can still use them in an `if x:` as if it were a
  boolean.
- Converts the `(null)` options string to `None`.
- Some categorical fields are enumerated in the schema (currently only
  access type)

It mainly allows you to benefit from autocomplete in your editor and
makes tasks such as result aggregation and exploration easier.

## Usage

At the top level of the repository:

```
pip install ./pkg
```

There is a IOR output JSON file in `test/result.json` which you can use
to verify functionality:

```python
from iorpyd import IOROutput, pprint_size, pprint_num

with open("test/result.json", "r") as f:
    data = IOROutput.model_validate_json(f.read())

print(data.tests[0].results[0].bw_bytes) # -> 6050265274.7776

# There are also functions to make values human-readable. You should use 
# pprint_size for byte values only, and pprint_num for others, such as 
# IOPS. These functions only handle positive numbers.

print(f"{pprint_size(data.tests[0].results[0].bw_bytes)}/s") # -> 5.63 GiB/s
print(f"{pprint_num(data.tests[0].results[0].iops)}IOPS") # -> 5.80 KIOPS

```

## License

MIT