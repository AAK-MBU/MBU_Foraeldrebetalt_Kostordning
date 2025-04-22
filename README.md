# Kostordning

A process designed to streamline two processes when working with kostordning in SAP.

## Overview Creation

This process creates invoices for parent-paid lunch in SAP.

### Usage

You can run the process either locally or from OpenOrchestrator.
Make sure to include the following process arguments:

#### Upload To Queue

- `"transactionCode": "zdkd_opret_faktura"`
- `"process": "queue_uploader"`

This process retrieves the relevant Excel files from SharePoint and extracts the necessary data. 
The extracted data is then uploaded as individual elements to a queue for further processing.

#### Handle queue

- `"transactionCode": "zdkd_opret_faktura"`
- `"process": "queue_uploader"`

This process retrieves queue elements and creates invoices for parent-paid lunches in SAP based on the data.
