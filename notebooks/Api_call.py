dbutils.secrets.get("data_platform_ingestion_sp", "admin_client_secret")
displayHTML("<span/>".join(secret_token))