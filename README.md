# climate-to-bufr

climate2bufr.py converts given climate file to bufr file (edition 4). The resulting bufr file is coded on
bufr sequnce 301150 and 307073, where 301150 is the wigos sequance and 307073 is the climate sequance.
climate2bufr.py uses subset_arrays.py and separate_keys_and_values.py in conversion.

## Installation

Use the yum/dnf package manager to install climate-to-bufr. It can be found from fmiforge repo.

## Usage

```bash
$ python3 climate2bufr.py path/to/the/climate/file

```
