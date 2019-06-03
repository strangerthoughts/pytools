# Infotools
A collection of tools to make common tasks simpler and more convienient.
It is organized into several subpackages:

- filetools
- numbertools
- timetools


### Filetools
This package has a few functions useful unctions when operating with system files.

Available Functions:

- memoryUsage

    Retrieves the current RAM usage.
- generateFileMd5

    Generates a file's MD5sum

- checkDir

    Ensures that the given folder exists.

## Numbertools
Common number operations

Useful functions:
- human_readable

    Converts a number or numerical string to a more easily-readable format.
    ```python
    >>> from infotools import numbertools
    >>> numbertools.human_readable(12345.678, base = 'K')
    '12.35K'

    >>> numbertools.human_readable(10.456E-5, base = 'u')
    '104.56u'

    >>> numbertools.human_readable(10.4561940387432E-5, precision = 4)
    '104.5619u'
    ```
 
- to_number

    Attempts to convert the input into a number
    ```python
    >>> from infotools import numbertools
    >>> numbertools.to_number('187')    
    187
  
    >>> numbertools.to_number('abcdef')
    nan
  
    >> numbertools.to_number('asdas', default = 0)
    0
    ```

- is_number

    Tests if the input string is a number. Works with floats.
    ```python
    >>> from infotools import numbertools
    >>> numbertools.is_number('123.456')
    True

    >>> numbertools.is_number('abc')
    False
    ```

## timetools
Contains time and date methods with simple importing and exporting methods.

Available Classes:

- Timestamp

    Represents a single time and date. 
    ```python
    >>> from infotools import timetools
    >>> timestamp = timetools.Timestamp.now()
    >>> str(timestamp)
    '2018-09-03T20:22:05.405436-04:00'
    ```
    
- Duration
    
    Represents differences in time
    ```python
    >>> from infotools import timetools
    >>> duration = timetools.Duration('P11DT4H3S')
    'Duration("P1W4DT4H3.0S")'
    ```
    
- Timer

    A simple time with convienient methods for benchmarking functions
