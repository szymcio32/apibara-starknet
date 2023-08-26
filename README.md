# Apibara performance test
Check the performance for python and typescript apibara indexer
## How to set up
### Python
1. Create virtual env: `python3 -m venv venv`
2. Activate it: `source venv/bin/activate`
3. Install poetry: `python3 -m pip install poetry`
4. Install packages: `poetry install`
5. Set env variables:
```
export SERVER_URL=mainnet.starknet.a5a.ch
export MONGO_URL=mongodb://apibara:apibara@localhost:27017
export RPC_URL=
export APIBARA_AUTH_TOKEN=
```
6. Run mongo db: `docker-compose up`
7. Run indexer `poetry run swap-indexer indexer`

### Typescript
1. Set in the docker compose file apibara auth token
2. `cd` to `typescript-test`
3. Run `docker-compose up`