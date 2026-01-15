# nuScenes Headless Downloader & Extractor

This script automates the acquisition of the **nuScenes Full Dataset** on remote Linux servers. It bypasses the need for a local browser by authenticating via the terminal, managing signed AWS S3 links, and organizing the data into the official directory structure.

## Features
- **Headless Auth**: Authenticates with nuScenes via AWS Cognito directly from the CLI.
- **Smart URL Refresh**: Fetches a fresh signed URL for every file to prevent session timeouts during the 400GB+ download.
- **Integrity Verification**: Automatic MD5 checksum validation after every download.
- **Auto-Extraction**: Unpacks `.tgz` files into the standard hierarchy immediately upon verification.
- **Storage Management**: Option to delete compressed archives after extraction to save disk space.
- **Resume Support**: Skips files that are already successfully downloaded and verified.

---

## Prerequisites

Ensure you have Python 3 and the necessary libraries installed on your server:

```bash
pip install requests tqdm
```

## Use nohup to ensure the script continues running after disconnecting from SSH.
```bash
nohup python3 -u download_nuscenes.py > download.log 2>&1 &
```

## Expected Directory Structure
```bash
nuscenes_full/
├── maps/               # HD Map expansions
├── samples/            # Annotated keyframes (Images, LiDAR, Radar)
├── sweeps/             # Unannotated intermediate frames
├── v1.0-trainval/      # Database JSON tables (metadata)
└── v1.0-test/          # Test set metadata (if included)
```
## Credits & Acknowledgments

This script is based on and inspired by the logic developed by li-xl in the [nuscenes-download](https://github.com/li-xl/nuscenes-download) repository. 

Special thanks to the original author for:
- Mapping the AWS Cognito authentication flow for nuScenes.
- Identifying the Execute-API endpoints for generating signed S3 links.
- Providing the community with a headless alternative to the official web-based download process.