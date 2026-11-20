# Task A1: Design the Data Acquisition

## A1.1: Inspect the Source
### Structure of the Station CSV File
The station CSV file contains time-series environmental monitoring data with the following columns:
* `station_id` (string): Unique identifier for the monitoring station.
* `timestamp` (string/datetime): Date and time of the reading.
* `pm25` (float): Particulate Matter 2.5 concentration ($\mu g/m^3$).
* `pm10` (float): Particulate Matter 10 concentration ($\mu g/m^3$).
* `temperature` (float): Ambient temperature in Celsius.
* `humidity` (float): Relative humidity percentage.
* `status` (string): Operational status of the sensor (e.g., Active, Maintenance).

### Data-Quality Problems and Examples
1. **Missing Values**: Essential fields left blank or recorded as `null`/`NaN`.
   * *Example*: `ST001,2026-10-01 12:00:00,,45.2,22.5,60,Active` (missing `pm25`).
2. **Out-of-Range / Invalid Values**: Physical measurements outside realistic bounds.
   * *Example*: `ST002,2026-10-01 12:00:00,-15.5,120.0,25.0,-10.0,Active` (negative humidity `-10.0`).
3. **Inconsistent Timestamp Formats**: Variations in date formatting across files or rows.
   * *Example*: Mixing `2026-10-01 14:30:00` with `10/01/2026 2:30 PM`.
4. **Duplicate Records**: Identical readings logged multiple times for the same timestamp and station.
   * *Example*: Two identical rows for `ST001` at `2026-10-01 15:00:00`.

---

## A1.2: Design the Storage
### SQLite Table Schema

#### 1. `stations` Table
* `station_id` TEXT PRIMARY KEY
* `station_name` TEXT
* `latitude` REAL
* `longitude` REAL

#### 2. `readings` Table
* `reading_id` INTEGER PRIMARY KEY AUTOINCREMENT
* `station_id` TEXT NOT NULL
* `timestamp` DATETIME NOT NULL
* `pm25` REAL
* `pm10` REAL
* `temperature` REAL
* `humidity` REAL
* `status` TEXT
* FOREIGN KEY (`station_id`) REFERENCES `stations`(`station_id`)

### CSV to SQLite Mapping
* CSV `station_id` $\rightarrow$ `stations.station_id` and `readings.station_id`
* CSV `timestamp` $\rightarrow$ `readings.timestamp` (parsed to ISO-8601 DATETIME format)
* CSV `pm25`, `pm10`, `temperature`, `humidity` $\rightarrow$ Respective REAL columns in `readings`
* CSV `status` $\rightarrow$ `readings.status`

---

## A1.3: CSV or SQL?
### Comparison for Typical Queries (e.g., Average PM2.5 of one station in October)

* **CSV Approach (File-based scanning)**:
  * *Mechanism*: Load raw CSV files into memory (or stream line-by-line), parse strings, filter rows matching `station_id` and October dates, then compute the average.
  * *Drawbacks*: Requires a full file scan every time, high memory consumption, slow performance as data scales.
* **SQL Query Approach (Indexed Database)**:
  * *Mechanism*: Execute a structured query leveraging database indexes on `station_id` and `timestamp`.
  * *Example Query*:
    ```sql
    SELECT AVG(pm25) 
    FROM readings 
    WHERE station_id = 'ST001' 
      AND timestamp >= '2026-10-01 00:00:00' 
      AND timestamp <= '2026-10-31 23:59:59';
    ```
  * *Advantages*: Instant retrieval, optimized execution plans, low memory overhead.

---

## Alternative Concept and Complexity Analysis
### Pandas DataFrame (CSV-only) vs SQLite

* **Time Complexity**:
  * *Pandas / CSV*: Full scan $O(n)$ where $n$ is the total number of records across all CSV files. Every query forces a scan of the entire dataset.
  * *SQLite*: Indexed query $O(\log n)$ search time due to B-Tree indexing on primary keys and indexed columns.
* **Space Complexity**:
  * *Pandas / CSV*: Entire datasets must be loaded into RAM (Memory) during execution, risking Out-Of-Memory (OOM) errors for large archives.
  * *SQLite*: Data is persisted efficiently on Disk with pagination and buffer pool management, querying only the necessary disk pages into memory.
