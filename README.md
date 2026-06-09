# databricks_optimizations

Repository for Terraform, Delta Live Tables pipeline code, and a Python data generator to demonstrate Databricks liquid clustering on ADLS Gen2.

This repository will contain:
- terraform/: Terraform code to create clusters and a DLT pipeline in an existing Databricks workspace
- dlt_pipeline/: Delta Live Tables pipeline code (Python)
- data_generator/: Python Faker-based data generator that writes CSV files to ADLS Gen2

Replace the placeholder variables in terraform/variables.tf before applying.
