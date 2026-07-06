# GitHub Actions workflow added: build-release.yml

This workflow builds the React frontend and installs server production dependencies, packages them into release.zip, and optionally creates a GitHub Release and uploads the ZIP.

How to run:
1. Go to the repository on GitHub -> Actions -> Build and Release M-USDT-TRC20
2. Click "Run workflow" and provide the tag (default v1.0.0) and whether to include node_modules and publish the release.

Security note: Do NOT store private keys in the repository. To enable custodial server operations during CI, add SERVER_PRIVATE_KEY as a repository secret (Settings -> Secrets and variables -> Actions). The workflow will not echo or store secrets in the repository.
