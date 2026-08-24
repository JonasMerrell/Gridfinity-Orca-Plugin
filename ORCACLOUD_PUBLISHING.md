# Orca Cloud Publishing

This repository includes a GitHub Actions workflow (`.github/workflows/publish-orcacloud.yml`) for zero-secret [OIDC trusted publishing to Orca Cloud](https://cloud.orcaslicer.com/wiki/#publish-from-github).

## Setup

1. Connect this repository in [Orca Cloud](https://cloud.orcaslicer.com) under **Shared Plugins > (Your Plugin) > Edit plugin > GitHub publishing** by entering `JonasMerrell/Gridfinity-Orca-Plugin`.
2. Publish a new GitHub Release, such as `v1.5.0`.

The workflow automatically compiles all six platform targets and uploads them directly to the Orca Cloud Plugin Hub.
