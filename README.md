# boib-extractor
A Python tool to extract Balearic Islands official bulletin data

## Requirements
* [Docker](https://docs.docker.com/engine/) and [docker-compose](https://docs.docker.com/compose/)


## Project setup
```bash
docker-compose build
```

## Usage

### Extract yearly bulletins
```bash
docker-compose run --rm app fetch 2025
```

The output will be every bulletin published in 2025 grouped by sections and all its articles: 

```
Bulletin: 2025-01-30 - ORDINARY - https://www.caib.es/eboibfront/ca/2025/12049/
==== SectionType.GENERAL =====
	 * AJUNTAMENT D'INCA - https://intranet.caib.es/eboibfront/eli/es-ib-01070276/odnz/2025/01/30/(1)/dof/cat/pdf

==== SectionType.PERSONNEL =====
	 * CONSELL INSULAR DE FORMENTERA
 - https://www.caib.es/eboibfront/pdf/ca/2025/14/1181487
```

### Extract monthly bulletins
```bash
docker-compose run --rm app fetch 2025 1
```

The output will be like the previous one

