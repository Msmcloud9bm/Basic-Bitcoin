## Sweep script and Docker instructions

This branch now includes:
- server/sweep.js : helper script to sweep all USDT from the private-key-controlled address to a target.
- server/index.js : updated to serve client/dist when present (so the server can serve the built SPA).
- Dockerfile : builds server and expects client/dist to be copied in during build.
- docker-compose.yml : example compose file to run the server container (pass env vars at runtime).

Important: I will NOT add your private key to the repo or any release. Set SERVER_PRIVATE_KEY locally or as a secret in your environment.

Quick usage examples

1) Local run with private key in env (recommended):

export SERVER_PRIVATE_KEY="your_private_key_here"
export TRONGRID_URL="https://api.trongrid.io"
export USDT_CONTRACT="TXLAQ63Xg1NAzckPwKHvzw7CSEmLMEqcdj"
node server/index.js

2) Use sweep script (CLI arg overrides SWEEP_TARGET env):

# dry run
node server/sweep.js TRECIPIENTADDRESS --dry-run

# actual sweep
node server/sweep.js TRECIPIENTADDRESS

3) Docker

# Build (ensure client/dist exists or copy in)
docker build -t m-usdt-wallet .

# Run (pass private key at runtime, do NOT bake into image)
docker run -d -p 4000:4000 -e SERVER_PRIVATE_KEY="your_private_key_here" -e TRONGRID_URL="https://api.trongrid.io" m-usdt-wallet

4) Docker Compose (create a .env file or export vars)

# Example .env (do NOT commit this file):
# SERVER_PRIVATE_KEY=your_private_key_here
# TRONGRID_URL=https://api.trongrid.io
# USDT_CONTRACT=TXLAQ63Xg1NAzckPwKHvzw7CSEmLMEqcdj

docker-compose up -d --build

Security reminders
- Never commit private keys or add them to the repository. Use environment variables or a secrets manager.
- Test with a small amount first before sweeping full balances.
- Ensure the source address has a small TRX balance to cover bandwidth/energy fees.

