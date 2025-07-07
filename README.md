# postgres-sample-dbs

A collection of sample Postgres databases for learning, testing, and development.

# How the dataset files were created

Data was loaded into [Neon Serverless Postgres](https://neon.tech/) (Postgres 15). The data was then dumped using the [pg_dump](https://www.postgresql.org/docs/current/app-pgdump.html) utility. For example:

```bash
pg_dump "postgres://<user>:<password>@<hostname>/<dbname>" --file=[file_name].sql --format=p --no-owner --no-privileges
```

For larger datasets, such as the [employees](#employees-database) database, the following format option was used: `--format=c`

### Clone the repository to your local machine

```bash
git clone https://github.com/danieltprice/postgres-sample-dbs.git
```

### Download an individual dump file

You can download an individual dump file from this repo on the GitHub site or using `wget`.

From this repo on the GitHub site:

1. Click on the dump file to open it.
2. Above the content of the file, you should see a button labeled "Raw". Click it. This will open a new tab or window in your browser displaying the raw contents of the file.
3. Right-click anywhere in the window or tab displaying the raw file contents, and select "Save As..." or "Save Page As ..." from the context menu. Choose a location on your computer to save the file, and click "Save".

Using `wget`:

```bash
wget -O [file_name].sql https://raw.githubusercontent.com/danieltprice/postgres-sample-dbs/main/[file_name].sql
```

### Restore a dump file to your Postgres database

```bash
psql -U <user> -d <dbname> -h <hostname> -p <port> < [file_name].sql
```

## Available Databases

- [Chinook](#chinook-database)
- [Employees](#employees-database)
- [Lego](#lego-database)
- [Netflix](#netflix-database)
- [Pagila](#pagila-database)
- [Postgres Air](#postgres-air-database)
- [Titanic](#titanic-database)
- [World Happiness](#world-happiness-database)

---

## Chinook Database

- Source: [https://github.com/lerocha/chinook-database](https://github.com/lerocha/chinook-database)
- License: [MIT License](https://github.com/lerocha/chinook-database/blob/master/LICENSE.txt)

---

## Employees Database

- Source: This database was originally created by Patrick Crews and Giuseppe Maxia of MySQL. The most recent version can be found in XML format at this location: [http://timecenter.cs.aau.dk/software.htm](http://timecenter.cs.aau.dk/software.htm). Designing the relational schema was undertaken by Giuseppe Maxia while Patrick Crews was responsible for transforming the data into a format compatible with MySQL. Their work can be accessed here: [https://github.com/datacharmer/test_db](https://github.com/datacharmer/test_db). Subsequently, this information was adapted to a format suitable for PostgreSQL: [https://github.com/h8/employees-database](https://github.com/h8/employees-database). The data was generated, and there are inconsistencies.
- License: This work is licensed under the Creative Commons Attribution-Share Alike 3.0 Unported License. To view a copy of this license, visit [http://creativecommons.org/licenses/by-sa/3.0/](http://creativecommons.org/licenses/by-sa/3.0/) or send a letter to Creative Commons, 171 Second Street, Suite 300, San Francisco, California, 94105, USA.

---

## Lego Database

- Source: [https://github.com/bricker/lego-database](https://github.com/bricker/lego-database)
- License: [MIT License](https://github.com/bricker/lego-database/blob/master/LICENSE)

---

## Netflix Database

- Source: [https://github.com/gregbaker/netflix-database](https://github.com/gregbaker/netflix-database)
- License: [MIT License](https://github.com/gregbaker/netflix-database/blob/main/LICENSE)

---

## Pagila Database

- Source: [https://github.com/devrimgunduz/pagila](https://github.com/devrimgunduz/pagila)
- License: [PostgreSQL License](https://github.com/devrimgunduz/pagila/blob/master/LICENSE)

---

## Postgres Air Database

- Source: [https://github.com/postgres/postgres-air](https://github.com/postgres/postgres-air)
- License: [PostgreSQL License](https://github.com/postgres/postgres-air/blob/main/LICENSE)

---

## Titanic Database

- Source: [https://www.kaggle.com/c/titanic/data](https://www.kaggle.com/c/titanic/data)
- License: [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/)

---

## World Happiness Database

- Source: [https://www.kaggle.com/unsdsn/world-happiness](https://www.kaggle.com/unsdsn/world-happiness)
- License: [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/)

---

## Licensing

This repository is provided under the MIT License. However, please note that each individual database included in this repository is subject to its own license terms.

The MIT License applies to the scripts and other components that we created. We respect the rights of the original creators of the databases, and we only redistribute these databases in compliance with their respective licenses.

For each individual database, we have clearly indicated where the full text of the license can be found. If you choose to use any of these databases, you must comply with the terms specified in their respective licenses.
