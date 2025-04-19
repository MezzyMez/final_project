# Statistics Canada Data File Record Layout (non-Census cubes)

## Column Descriptions

### Ref_date
- Reference period for the series being released
- Spanned reference periods (2011/12) will be displayed in the same format as on the website

### Dimension name
- Name of dimension
- There can be up to 10 dimensions in a data table
- Example: Geography

### DGUID
- Dissemination Geography Unique Identifier
- Alphanumeric code, 10-20 characters in length
- Format: `VVVV T SSSS GGGGGGGGGGG`
  - Vintage (4)
  - Type (1)
  - Schema (4)
  - Geographic Unique Identifier (2-11)

### Unit of measure
- The unit of measure applied to a member given in text
- Multiple units of measure possible in a table
- Examples: acres, hectares

### Unit of measure ID
- Unique reference code for a particular unit of measure
- Example: 28 = acres

### Scalar factor
- The scalar factor associated with a data series, displayed as text
- Multiple scalar factors possible in a table
- Example: hundreds

### Scalar_ID
- Unique numeric reference code for a particular scalar factor
- Example: 2 = hundreds

### Vector
- Unique variable length reference code time-series identifier
- Format: 'V' followed by up to 10 digits
- Examples: V1234567890, V1

### Coordinate
- Concatenation of the member ID values for each dimension
- One value per dimension
- Maximum of 10 dimensions
- Example: 1.1.1.36.1

### Value
- Data point value (decimal applied where applicable)
- Example: 12397.13

### Status
- Shows various states of a data value using symbols
- Symbols are described in the symbol legend and notes
- Some symbols accompany data values, others replace them
- Examples: A, B, C, D, E, F, X, 0s

### Symbol
- Describes data points that are preliminary or revised
- Uses symbols 'p' and 'r'
- Accompanies a data value

### Terminated
- Indicates a data value that has been terminated (no longer updated)
- Displayed using the symbol 't'

### Decimals
- Displays the decimal precision for a given value 