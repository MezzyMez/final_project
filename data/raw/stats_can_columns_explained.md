# Understanding Statistics Canada Data Columns

## Core Columns

### Ref_date
- **What it is**: The time period the data represents
- **Examples**:
  - Single month: "2024-01"
  - Quarter: "2024-Q1"
  - Year: "2024"
  - Fiscal year: "2023/2024"
- **Why it matters**: Helps track data over time and align different datasets

### Dimension name
- **What it is**: Categories that break down the data
- **Examples**:
  - Geography: "Canada", "Ontario", "Toronto"
  - Industry: "Manufacturing", "Retail", "Agriculture"
  - Age groups: "0-14", "15-24", "25-54"
- **Why it matters**: Allows you to analyze data by different categories

### DGUID
- **What it is**: A unique identifier for geographic areas
- **Format**: `VVVV T SSSS GGGGGGGGGGG`
  - VVVV: Vintage (year of the geographic framework)
  - T: Type (1=province, 2=territory, etc.)
  - SSSS: Schema (geographic classification system)
  - GGGGGGGGGGG: Unique geographic identifier
- **Example**: "2021.1.1.1" (Canada in 2021)
- **Why it matters**: Ensures consistent geographic references across datasets

## Measurement Columns

### Unit of measure & Unit of measure ID
- **What they are**: How the data is measured
- **Examples**:
  - Unit: "dollars", "percentage", "number of persons"
  - ID: "28" (dollars), "2" (percentage)
- **Why they matter**: Ensures correct interpretation of values

### Scalar factor & Scalar_ID
- **What they are**: Multipliers for the values
- **Examples**:
  - Factor: "thousands", "millions", "units"
  - ID: "2" (thousands), "6" (millions)
- **Why they matter**: Prevents misinterpretation of scale (e.g., 1,000 vs 1,000,000)

### Vector
- **What it is**: A unique identifier for a specific time series
- **Format**: 'V' followed by numbers
- **Example**: "V1234567890"
- **Why it matters**: Links data points across time

### Coordinate
- **What it is**: Combination of dimension values
- **Format**: Numbers separated by periods
- **Example**: "1.1.1.36.1" might represent:
  - 1: Canada
  - 1: Manufacturing
  - 1: Full-time
  - 36: Ontario
  - 1: January
- **Why it matters**: Uniquely identifies each data point

## Data Quality Columns

### Value
- **What it is**: The actual data point
- **Examples**:
  - "12397.13" (with decimals)
  - "1500" (whole number)
- **Why it matters**: The core data you're analyzing

### Status
- **What it is**: Indicates data quality or special conditions
- **Examples**:
  - "A": Good quality
  - "B": Acceptable quality
  - "C": Use with caution
  - "D": Too unreliable
  - "X": Suppressed for confidentiality
- **Why it matters**: Helps assess data reliability

### Symbol
- **What it is**: Additional data quality indicators
- **Examples**:
  - "p": Preliminary data
  - "r": Revised data
- **Why it matters**: Indicates if data might change

### Terminated
- **What it is**: Indicates discontinued series
- **Symbol**: "t"
- **Why it matters**: Identifies data that won't be updated

### Decimals
- **What it is**: Number of decimal places
- **Example**: "2" means values have 2 decimal places
- **Why it matters**: Ensures correct precision in calculations

## Practical Example
Here's how these columns might look together in a row:

| Ref_date | Dimension | DGUID | Unit | Value | Status |
|----------|-----------|-------|------|-------|--------|
| 2024-01 | Ontario | 2021.1.1.36 | dollars | 12397.13 | A |

This represents:
- January 2024 data
- For Ontario
- In current dollars
- Value of 12,397.13
- Good quality data 