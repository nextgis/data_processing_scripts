#!/bin/bash   

echo "$(date)" >> cronruns.txt
cd data_processing_scripts/OSM_NGW/

python update_dump.py
python tree/main.py

