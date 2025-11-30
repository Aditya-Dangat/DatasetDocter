# Example Datasets

This folder contains sample datasets for testing DatasetDoctor.

## Creating a Test Dataset

You can create a simple test CSV file to try DatasetDoctor:

```csv
name,age,city,email
John,25,New York,john@example.com
Jane,,Los Angeles,jane@example.com
Bob,30,NY,bob@example.com
Alice,25,New York,alice@example.com
Charlie,abc,San Francisco,charlie@example.com
```

Save this as `test_data.csv` and run:
```bash
python src/main.py examples/test_data.csv
```

## What to Look For

DatasetDoctor should detect:
- Missing age value (row 2)
- Duplicate city names ("New York" vs "NY")
- Wrong data type in age column ("abc" instead of number)
- Duplicate rows (John and Alice have same age and city)

