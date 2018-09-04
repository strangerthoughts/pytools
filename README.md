# Pytools
A colleciton of tools to make common tasks simpler and more convienient.
It is organized into several subpackages:
- datatools
- filetools
- geotools
- numbertools
- tabletools
- timetools

### Datatools
This package contains an overwritten `dataclass` function as a drop-in replacement for `dataclasses.dataclass`
This dataclass addes dictionary-like properties to newly created dataclasses.
#### Sample Usage:

```python
from pytools.datatools import dataclass

@dataclass
class Example:
    first: str
    second: int
    third: float
   
>>> example = Example('abc', 123, 3.14)

>>> example['second']
123
>>> example.to_yaml()
{first: abc, instanceOf: Example, second: 123, third: 3.14} 
```

### Filetools
This package has a few functions usefull unctions when operating with system files.

Available Functions:

- memoryUsage

    Retrieves the current RAM usage.
- generateFileMd5

    Generates a file's MD5sum

- checkDir

    Ensures that the given folder exists.

### Numbertools
Common number operations

Useful functions:
- human_readable

    Converts a number or numerical string to a more easily-readable format.
    ```python
    >>> human_readable(12345.678, base = 'K')
    '12.35K'

    >>> human_readable(10.456E-5, base = 'u')
    '104.56u'

    >> >human_readable(10.4561940387432E-5, precision = 4)
    '104.5619u'
    ```
 
- to_number

    Attempts to convert the input into a number
    ```python
    >>> to_number('187')    
    187
  
    >>> to_number('abcdef')
    nan
  
    ```

- is_number

    Tests if the input string is a number. Works with floats.
    ```python
    >>> is_number('123.456')
    True

    >>> is_number('abc')
    False
    ```

### tabletools
Contains the Table class, a drop-in replacement for a pandas DataFrame with additional methods for selecting data.

### timetools
Contains time and date methods with simple importing and exporting methods.

Available Classes:

- Timestamp

    Represents a single time and date. 
    ```python
    >>> from pytools import timetools
    >>> timestamp = timetools.Timestamp.now()
    >>> str(timestamp)
    '2018-09-03T20:22:05.405436-04:00'

    ```
    
- Duration
    
    Represents differences in time
    ```python
    >>> from pytools import timetools
    >>> duration = timetools.Duration('P11DT4H3S')
    Duration('P1W4DT4H3.0S')
    ```
    
- Timer

    A simple time with convienient methods for benchmarking functions
