ALTER TABLE tickets ADD CONSTRAINT tickets_repository_id_number_key UNIQUE (repository_id, number);
