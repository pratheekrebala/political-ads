## Political File Pipeline 

Documenting the pipeline for processing the Political Files.

### Initial

 1. Fetch all available stations. (getAll)
 2. Filter to stations (based on affiliate)
 3. Fetch all available political files for a given criteria.
 
### Clean

 1. Check if OCR is needed.
 2. Do OCR if its needed.
 3. Run on Tabula
 4. Identify candidate cells.
 5. Find candidate cells.
 6. 
 
 
 Some other notes:
 
 In the Tabula pipeline, the line items do better with lattice based extraction but the meta information works better using stream extraction.