# Emergence of an Antigenically Drifted and Reassorted Influenza B Virus at the end of the 2024-25 Influenza Season

Elgin Akin, David A Villafuerte, Anne P. Werner, Matthew Pinsley, Amary Fall, Omar Abdullah, Julie M Norton, Richard Eric Rothman, Katherine Fenstermacher, Yu-Nong Gong, Eili Klein, Heba H Mostafa,  Andrew Pekosz

BioRxiv Preprint doi: https://doi.org/10.1101/2025.07.24.666632

## Organization of this repository

This repository houses all source code for the 8 segment and 1 genome [Nextstrain Build for Assessing C.3 Reassortment Rates](https://nextstrain.org/groups/PekoszLab/akine/ibvc3/vic/ha) along with all reassortment tanglegrams for the 2024-25 Influenza B season.

> [!IMPORTANT]  
> Repository Code of conduct for ALL collaborators using this repo:
> 1. **DO NOT** push commits to main. Please open a [pull request](https://github.com/elginakin/influenzab_c.3/compare). 
> 2. Please document any problems or issues you encounter by opening a [github issue](https://github.com/elginakin/influenzab_c.3/issues)

> [!WARNING]  
> This repository does NOT house the necessary data to construct the 9 IBV C.3-enriched nextstrain builds. These data are availible on a [private OneDrive](https://livejohnshopkins-my.sharepoint.com/:f:/r/personal/eakin1_jh_edu/Documents/01_Pekosz_Lab/01_Project_Notebooks/Project_5_2024-25_ibv_reassortment/03_repositories/nextstrain_snapshots?csf=1&web=1&e=tEbrf3). Contact Elgin Akin (eakin1@jh.edu) for access. 

This repository houses the nextstrain segment build and genome build snakemake pipeline. It functionally represents a typical [Pekosz Lab seasonal Influenza B nextstrain build](https://github.com/Pekosz-Lab/nextstrain) but replaces the [automated data ingest pipeline](https://github.com/Pekosz-Lab/nextstrain/blob/main/workflow/snakemake_rules/ingest.smk) with a **manual data ingest pipeline**. This pipeline can be found in the in the [01_ingest.qmd](notesbooks/01_ingest.qmd) notebook in order to accomodate sequences from GISAID. In the future, efforts will be made to automate the cleaning of publically sourced data.

# Tanglegram Quick Links

Instructions: Click on each link to visualize a HA:{segment} tanglegram in auspice.

> [!WARNING]
> You must have access to the Pekosz Lab private nextstrain account. Contact Dr. Andy Pekosz apekosz1@ jh.edu and cc Elgin Akin (eakin1@jh.edu) for access 

##### 4 Probable C.5.1 HA reassortments with a C.3 HA in NA, NP, NS and PA 

- [HA:NA](https://nextstrain.org/groups/PekoszLab/akine/ibvc3/vic/ha:groups/PekoszLab/akine/ibvc3/vic/na?f_subclade=C.3,C.5.1)
- [HA:NP](https://nextstrain.org/groups/PekoszLab/akine/ibvc3/vic/ha:groups/PekoszLab/akine/ibvc3/vic/np?f_subclade=C.3,C.5.1)
- [HA:NS](https://nextstrain.org/groups/PekoszLab/akine/ibvc3/vic/ha:groups/PekoszLab/akine/ibvc3/vic/ns?f_subclade=C.3,C.5.1)
- [HA:PA](https://nextstrain.org/groups/PekoszLab/akine/ibvc3/vic/ha:groups/PekoszLab/akine/ibvc3/vic/pa?f_subclade=C.3,C.5.1)

##### 3 Non C.3 Reassortments
- [HA:PB2](https://nextstrain.org/groups/PekoszLab/akine/ibvc3/vic/ha:groups/PekoszLab/akine/ibvc3/vic/pb2?f_subclade=C.3,C.5.1)
- [HA:PB1](https://nextstrain.org/groups/PekoszLab/akine/ibvc3/vic/ha:groups/PekoszLab/akine/ibvc3/vic/pb1?f_subclade=C.3,C.5.1)
- [HA:MP](https://nextstrain.org/groups/PekoszLab/akine/ibvc3/vic/ha:groups/PekoszLab/akine/ibvc3/vic/mp?f_subclade=C.3,C.5.1)

# How to execute this build

1. Archive the current version of the repository. 
    - This is important because the nextstrain pipeline will overwrite files in the `data/` and `source/intermediate/` directories.
    - Make a new directory in the snapshots folder naming it according to the date of the new build YYYMMDD (e.g. 20250615)
    - Copy the entire contents of your project into this new directory 
        - a script has been written to accomplish this: execute `python scripts/snapshot.py -s . -o snapshots/{YYYYMMDD}` changing the date to the current date. 
    - Once you have manually confirmed that the new directory is a complete copy of the project, you can safely delete the contents of the `data/`, `results`, and `source/intermediate/` directories using our safety-enhanced script:
        - Run `python scripts/snapshot.py`.
2. Download updated Influenza B Genomic data from [GISAID](https://www.gisaid.org/)
    - Dates should be filtered to 2020-10-05 to the **Present Date**.
    - Rename the sequences.fasta file to gisaid_vic_sequences.fasta
    - Rename the metadata.tsv file to gisaid_vic_metadata.tsv
    - Place these files in the `source/` directory of your project directory (this repository)
3. Manually curate the sequences and metadata files using the [01_ingest.qmd](notesbooks/01_ingest.qmd) notebook.
4. Execute the snakemake pipeline to build the 8 segment and 1 genome builds. 
    - The snakemake pipeline is located in the `workflow/` directory of this repository. 
    - The snakemake pipeline can be executed by running the following command in your terminal: 

```{shell}
snakemake --cores 8
```

# How are these data organized? 

The [01_ingest.qmd](notesbooks/01_ingest.qmd) explains how sequences were down-selected and curated to result in a high quality genomes for 8 segment-specific builds in augur. 

The most recently curated consensus dataset can be found in the `data/` directory of the most recent data snapshots HERE: [Link to OneDrive](https://livejohnshopkins-my.sharepoint.com/:f:/r/personal/eakin1_jh_edu/Documents/01_Pekosz_Lab/01_Project_Notebooks/Project_5_2024-25_ibv_reassortment/03_repositories/nextstrain_snapshots?csf=1&web=1&e=4QwbWC)

This folder represents various snapshots of data downsampling and will be periodically updated with circulating Influenza B strains deposited on GISAID. However, all current and historical builds will be deposited into this folder. 

Critically, the `data/` directory houses 8 `sequence.fasta` and 8 `metadata.tsv` which contain equivalent numbers of genomes across all 8 segment files. 

## Instructions to view non-HA:{segment} reassortments in Auspice/Nextstrain

1. In your browswer, click the URL window and delete its contents.
2. The formula for building a tanglegram in your browser is as follows: 
    - `https://nextstrain.org/groups/PekoszLab/akine/ibvc3/vic/**segment**:groups/PekoszLab/akine/ibvc3/vic/**segment**`
    - The segment must be in all lowercase. Options: pb2, pb1, pa, ha, np, na, mp, ns. 

For example: a PB2:PA tanglegram can be build and visualized by entering the following URL into your browswer:
(https://nextstrain.org/groups/PekoszLab/akine/ibvc3/vic/pb2:groups/PekoszLab/akine/ibvc3/vic/pa)

# Build Specific Enhancements and TODOs

## Steps required needed for Public Release
- [ ] refactor this repository's version [fludb]() to accomodate authorship into the nextstrain build
- [ ] Add a numerical conversion of glycosylation for HA and NA.  
    - We really should consider wrapping this up in a package to centralize version control across projects...

## Enter Pekosz Lab Nextstrain Pipeline Enhancements into the seasonal builds
- [ ] Custom ingest process for piping gisaid and jhh hospital sequence and metadata 
- [ ] update fludb upload scrupt `upload_jhh.py`: JHH location from "JHH" to GISAID-formatted Region / Country / Division / Location: "North America/United States/Maryland/Baltimore" 
- [ ] `upload_gisaid.py` enhancements: 
    - strain name spaces are removed. Former logic was to replace " " with "_". 
    - Change the default location entry from "JHH" to "North America / United States / Maryland / Baltimore" to match GISAID location formatting. 
- [ ] Augur export - 'locations' renamed to 'area' - need to update lat_long.tsv config file

To preview builds locally: 

```{shell}
auspice view \
    --datasetDir auspice/vic
```

Find and kill local server 
```{shell}
lsof -i tcp:4000

kill -9 <PID> 
```

Upload to private nextstrain
```{shell}
python scripts/c.3_nextstrain_upload_private_genomes.py
```

quick export edit
```{shell}
snakemake --cores 8 --forcerun export  
```