"""
Loops through each metadata file and curates its location by splitting a column called location into 
"""

import subprocess

segments = ["pb2", "pb1", "pa", "ha", "np", "na", "mp", "ns", "genome"]

for segment in segments:
    input_path = f"source/intermediate/vic/{segment}/metadata_qc.tsv"
    output_path = f"source/intermediate/vic/{segment}/metadata_qc_location.tsv"

    cmd = [
        "python",
        "scripts/format-location.py",
        "-i", input_path,
        "-o", output_path
    ]

    try:
        subprocess.run(cmd, check=True)
        print(f"Processed {segment} successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error processing {segment}: {e}")
