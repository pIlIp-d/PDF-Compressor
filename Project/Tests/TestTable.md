# Test Table Documentation

## Console Test for PDFCompressor.py

| Parameter      | Condition                                  | Precondition                       | result     |
|:---------------|:-------------------------------------------|:-----------------------------------|------------|
| -p/--path      | valid path                                 | testFile                           | true       |
|                | valid path - seperated by spaces '""'      | testFile with space                | true       |
|                | invalid path - seperated by space, no '""' | testFile with space                | false      |
|                | invalid path - doesn't exist               |                                    | false      |
|                | directory as input                         | valid testFiles in directory       | true       |
|                | directory as input                         | empty directory                    | false      |
|                |                                            |                                    |            |
| -m/--mode      | valid mode (min)                           | testFile together with --force-ocr | true       |
|                | valid mode (max)                           | testFile together with --force-ocr | true       |
|                | invalid mode 0                             | together with --force-ocr          | false      |
|                | invalid mode 11                            | together with --force-ocr          | false      |
|                | size comparison 1 and 10                   | testFile together with --force-ocr | comparison |
|                |                                            |                                    |            |
| -o/--output    | already existing output file               |                                    | true?      |
|                | new output file                            |                                    | true       |
|                | directory as output file                   | input file                         | true       |
|                | directory as output file                   | input path                         | true       |
|                | file as output file                        | directory as input                 | true?      |
|                |                                            |                                    |            |
| -s/--force-ocr | enabled                                    | compression succeeded              | true       |
|                | enabled                                    | compression didn't succeed         | true       |
|                | enabled                                    | --no-ocr active                    | false      |
|                | disabled but created ocr                   | compression succeeded              | true       |
|                | disabled and no ocr                        | compression didn't succeed         | true       |
|                | disabled                                   | --no-ocr active                    | true       |
|                |                                            |                                    |            |
| -n/--no-ocr    | enabled                                    | compression succeeded              | true       |
|                | enabled                                    | compression didn't succeed         | true       |
|                | enabled                                    | -force-ocr active                  | false      |
|                | disabled                                   | compression succeeded              | true       |
|                | disabled                                   | compression didn't succeed         | true       |
|                | disabled                                   | -force-ocr active                  | true       |
|                |                                            |                                    |            |
| -c/--continue  | compresses all files                       | testFiles directory                | true       |
|                | -1                                         |                                    | false      |
|                | continue in range of file amount available | testFiles directory                | true       |
|                | larger than amount of available files      | testFiles directory                | false      |
|                |                                            |                                    |            |

_______________________________
##  Test for ConsoleUtility.py

### `print` method
| Parameter   | Condition                   | Precondition       | result | test_print_is_active     | test_print_is_not_active |
|:------------|:----------------------------|:-------------------|--------|--------------------------|--------------------------|
| string: str | prints string to console    | QUIET_MODE = False | true   | print("test") -> "test"  |                          |
|             | prints no string to console | QUIET_MODE = True  | true   |                          | print("test") -> ""      |

### `get_error_string` method
| Parameter   | Condition                                  | Precondition                      | result | test_valid_get_error_string | test_valid_string_already_ansi_colored_get_error_string |
|:------------|:-------------------------------------------|:----------------------------------|--------|-----------------------------|---------------------------------------------------------|
| string: str | string has added RED and END ANSI code     |                                   | true   | "testString is turned red"  |                                                         |
|             | string already has RED and END ANSI code   | string with RED and END ANSI code | ????   |                             | RED"testString is turned red"END                        |

### `get_file_string` method
| Parameter   | Condition                                  | Precondition                      | result | test_valid_get_error_string | test_valid_string_already_ansi_colored_get_error_string |
|:------------|:-------------------------------------------|:----------------------------------|--------|-----------------------------|---------------------------------------------------------|
| string: str | string has added RED and END ANSI code     |                                   | true   | "testString is turned red"  |                                                         |
|             | string already has RED and END ANSI code   | string with RED and END ANSI code | ????   |                             | RED"testString is turned red"END                        |

### `print_stats` method
| Parameter | Condition                    | Precondition    | result |
|:----------|:-----------------------------|:----------------|--------|
| orig      | valid file equals result     | existing file   | true   |
|           | valid file same size         | valid result    | true   |
|           | valid file smaller           | existing files  | true   |
|           | valid file bigger            | existing files  | true   |
|           | invalid file - doesn't exist |                 | false  |
|           |                              |                 |        |
| result    | valid file same size         | valid result    | true   |
|           | valid file smaller           | existing files  | true   |
|           | valid file bigger            | existing files  | true   |
|           | invalid file - doesn't exist |                 | false  |
|           |                              |                 |        |



