resource "postgresql_database" "chinook" {
  name  = "chinook"
  owner = "postgres"
}

resource "postgresql_database" "pagila" {
  name  = "pagila"
  owner = "postgres"
}

resource "postgresql_database" "happiness_index" {
  name  = "happiness_index"
  owner = "postgres"
}

resource "postgresql_database" "unused_db" {
  name  = "unused_db"
  owner = "postgres"
}
