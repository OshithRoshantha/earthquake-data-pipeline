# Earthquake ETL Pipeline with Apache Airflow

This project implements a robust **ETL pipeline** for processing real-time earthquake data using **Apache Airflow**. The pipeline automates fetching data from the **USGS Earthquake API**, processes and transforms it, and stores the results in **Azure Data Lake**. The final dataset is optimized for downstream **Machine Learning** model training.

---

## Key Features

- **Real-time Data Fetching**: Retrieves earthquake data every hour from the **USGS Earthquake API** with a minimum magnitude of 4.  
- **Data Cleaning and Preprocessing**: Ensures the data is consistent, removes duplicates, and formats it for storage.  
- **Transformation and Feature Engineering**: Includes:
  - Conversion to **Parquet** format for efficient storage.
  - Feature scaling using **MinMaxScaler**.
  - Encoding categorical variables with **OneHotEncoder**.
  - Categorizing earthquake magnitudes into custom-defined levels.  
- **Cloud Integration**: Utilizes **Azure Blob Storage** with **Hierarchical Namespace enabled** for staging, and **Azure Data Lake** for production-ready data.  
- **Scalable Architecture**: Built using **Apache Airflow**, ensuring modularity and task orchestration.

---

## Pipeline Workflow

1. **Fetch Data**:
   - Fetches earthquake data from the **USGS Earthquake API** using the specified time range.
   - Raw data is uploaded to Azure Blob Storage (staging).

2. **Preprocess Data**:
   - Cleans the raw JSON data and converts it into a structured **Pandas DataFrame**.
   - Removes invalid or incomplete entries.

3. **Transform Data**:
   - Converts the cleaned data to **Parquet** format.
   - Performs feature scaling and one-hot encoding.
   - Adds derived features such as magnitude categories.

4. **Push to Production**:
   - Transfers the final dataset to **Azure Data Lake** for downstream ML tasks.

---

## Tech Stack

- **Apache Airflow**: Workflow orchestration.
- **Azure Blob Storage**: For staging raw and intermediate data.
- **Azure Data Lake**: For storing production-ready data.
- **Pandas**: Data cleaning and manipulation.
- **Scikit-learn**: Feature engineering and preprocessing.
- **Requests**: API interaction with the USGS API.

---



