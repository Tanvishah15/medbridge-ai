from config import azure_cloud_credentials_configured, azure_configured, bootstrap_environment


def test_azure_configured_false_when_endpoint_missing(monkeypatch):
    monkeypatch.delenv("AZURE_AI_PROJECT_ENDPOINT", raising=False)
    bootstrap_environment()
    import config

    monkeypatch.setattr(config, "PROJECT_ENDPOINT", "", raising=False)
    assert azure_configured() is False


def test_azure_cloud_credentials_requires_service_principal(monkeypatch):
    monkeypatch.delenv("AZURE_TENANT_ID", raising=False)
    monkeypatch.delenv("AZURE_CLIENT_ID", raising=False)
    monkeypatch.delenv("AZURE_CLIENT_SECRET", raising=False)
    assert azure_cloud_credentials_configured() is False

    monkeypatch.setenv("AZURE_TENANT_ID", "tenant")
    monkeypatch.setenv("AZURE_CLIENT_ID", "client")
    monkeypatch.setenv("AZURE_CLIENT_SECRET", "secret")
    assert azure_cloud_credentials_configured() is True
