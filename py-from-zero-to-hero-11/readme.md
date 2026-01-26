## Context

Classify police case reports based on unstructured text. From each document we needed to extract key pieces of information:  city, district, year, month, and the type of occurrence (hate crime, robbery followed by murder, traffic accident, femicide, etc.). These insights need to be aggregated month by month  to measure government performance and analyze trends in crime reduction across the state. 

# Building the output.json

```
python3.11 -m venv challenge
source challenge/bin/activate
pip install -r ./requirements.txt
python3.11 ./src/phase01.py
```

Attention!
Once the execution is fully completed we must be able to identify into the `src` folder a file named `output.json`

This is a sample of the `output.json` file
```json
[
  {
    "district": "Centro",
    "city": "São José dos Campos",
    "year": 2022,
    "month": 1,
    "occurrence": "cyber fraud",
    "source": "/Users/renatomatos/Desktop/projects/python-adventure/py-from-zero-to-hero-11/docs/case_001.pdf",
    "Success": true,
    "ERROR": null
  },
  {
    "district": "Jardins",
    "city": "Campinas",
    "year": 2024,
    "month": 1,
    "occurrence": "drug trafficking",
    "source": "/Users/renatomatos/Desktop/projects/python-adventure/py-from-zero-to-hero-11/docs/case_002.pdf",
    "Success": true,
    "ERROR": null
  },
  {
    "district": "Jardins",
    "city": "Ribeirão Preto",
    "year": 2023,
    "month": 3,
    "occurrence": "traffic accident",
    "source": "/Users/renatomatos/Desktop/projects/python-adventure/py-from-zero-to-hero-11/docs/case_003.pdf",
    "Success": true,
    "ERROR": null
  },
  {
    "district": "Industrial",
    "city": "Osasco",
    "year": 2023,
    "month": 2,
    "occurrence": "kidnapping",
    "source": "/Users/renatomatos/Desktop/projects/python-adventure/py-from-zero-to-hero-11/docs/case_004.pdf",
    "Success": true,
    "ERROR": null
  },
  {
    "district": "Leste",
    "city": "Santos",
    "year": 2023,
    "month": 6,
    "occurrence": "vehicle theft",
    "source": "/Users/renatomatos/Desktop/projects/python-adventure/py-from-zero-to-hero-11/docs/case_005.pdf",
    "Success": true,
    "ERROR": null
  },
  ....
]
```

# Building the dashboard

```
python3.11 ./src/phase02.py
```

**Summary report**

```python
== OVERALL SUMMARY ===
Total records:      200
Successful records: 200
Failed records:     0

=== ERRORS ===
No failures. :)

=== CASES BY CITY ===
Osasco                    -> 35
Guarulhos                 -> 33
São Paulo                 -> 30
Santos                    -> 28
São José dos Campos       -> 26
Campinas                  -> 23
Ribeirão Preto            -> 23
Santo                     -> 1
São Jós e dos Campos      -> 1

=== CASES BY OCCURRENCE TYPE ===
vandalism                      -> 25
vehicle theft                  -> 20
robbery followed by murder     -> 20
kidnapping                     -> 18
drug trafficking               -> 17
burglary                       -> 15
assault                        -> 15
traffic accident               -> 13
femicide                       -> 13
armed robbery                  -> 13
domestic violence              -> 9
cyber fraud                    -> 8
hate crime                     -> 8
Unknown                        -> 2
Robbery followed by murder     -> 1
ficide                         -> 1
murder followed by robbery     -> 1
fematicide                     -> 1

=== CASES BY CITY AND YEAR ===
- São José dos Campos:
    2022         -> 10
    2023         -> 6
    2024         -> 10
- Campinas:
    2022         -> 6
    2023         -> 8
    2024         -> 9
- Ribeirão Preto:
    2022         -> 10
    2023         -> 8
    2024         -> 5
- Osasco:
    2022         -> 8
    2023         -> 15
    2024         -> 12
- Santos:
    Unknown year -> 2
    2022         -> 5
    2023         -> 10
    2024         -> 11
- Guarulhos:
    2022         -> 13
    2023         -> 6
    2024         -> 14
- São Paulo:
    2022         -> 14
    2023         -> 7
    2024         -> 9
- Santo:
    2022         -> 1
- São Jós e dos Campos:
    2023         -> 1
```

# Why two separated apps?
The goal is to separate responsibilities between two phases of the system.
The first application is focused on classifying the documents, a process that is computationally 
heavy and may take a significant amount of time. 

Once this phase completes and the output file is produced, the data can then be consumed quickly to generate the final charts and visualizations.

In practice, the classification step behaves like a background job. It can be triggered by queue events, continuously ingesting police case PDFs and either updating a database table or writing intermediate results to JSON files using the corresponding PDF names.

With all classified data available, building the final analytical dashboard becomes a straightforward synchronous operation. An endpoint can then render the results and stream the final PDF or visualization output to the user with minimal processing time.

![alt text](image.png)