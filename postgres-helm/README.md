# PostgreSQL Helm Chart

This Helm chart deploys a PostgreSQL instance and initializes it with multiple databases from SQL scripts.

## Prerequisites

- Kubernetes 1.19+
- Helm 3.2+

## Installing the Chart

To install the chart with the release name `my-release`:

```bash
helm install my-release . --namespace my-namespace
```

## Configuration

The following table lists the configurable parameters of the PostgreSQL chart and their default values.

| Parameter                | Description                                     | Default                                                                                                 |
| ------------------------ | ----------------------------------------------- | ------------------------------------------------------------------------------------------------------- |
| `replicaCount`           | Number of replicas to deploy                    | `1`                                                                                                     |
| `image.repository`       | PostgreSQL image repository                     | `postgres`                                                                                              |
| `image.tag`              | PostgreSQL image tag                            | `13`                                                                                                    |
| `image.pullPolicy`       | Image pull policy                               | `IfNotPresent`                                                                                          |
| `service.type`           | Kubernetes service type                         | `ClusterIP`                                                                                             |
| `service.port`           | Kubernetes service port                         | `5432`                                                                                                  |
| `postgres.user`          | PostgreSQL user                                 | `postgres`                                                                                              |
| `postgres.password`      | PostgreSQL password                             | `postgres`                                                                                              |
| `postgres.databases`     | List of databases to create                     | `chinook`, `pagila`, `periodic_table`, `happiness_index`, `unused_db`                                     |

Specify each parameter using the `--set key=value[,key=value]` argument to `helm install`.

For example:

```bash
helm install my-release . --set postgres.user=myuser,postgres.password=mypassword
```
