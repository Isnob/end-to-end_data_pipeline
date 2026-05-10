# Legacy standalone ingestion

This folder contains the first standalone version of the ingestion script.
The current project entrypoint is the Airflow DAG in `../dags/main_dag.py`.

To build the legacy container from the repository root:

```bash
docker build -f legacy/Dockerfile .
```
