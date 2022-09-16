# yandoa - Yet Another Disk Open API
Backend school task

* Stack:
  * Python 3.10
  * MongoDB 6.0.1
  * Docker & docker-compose


* Uses MongoDB and persistent docker volume to store data, there are two buckets:
  1) `docs` to store actual state
  2) `history` to store history

* Every request field is validated using Pydantic
* Additional validations are implemented (e.g. check if parent document exists)
* Carefully deals with timestamps
* Auto-documented according to openapi.yaml provided
  * Access docs here: `http://base_url/docs`

To run, execute in this directory: `docker-compose up -d`  

Todo: reorganize mongo scheme for more efficient children and parents search
