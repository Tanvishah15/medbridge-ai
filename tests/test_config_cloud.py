import config
from config import azure_cloud_credentials_configured, azure_configured, bootstrap_environment


def test_azure_configured_false_when_endpoint_missing(monkeypatch):
    monkeypatch.delenv("AZURE_AI_PROJECT_ENDPOINT", raising=False)
    monkeypatch.setattr(config, "_get_secret", lambda name, default="": default)
    assert azure_configured() is False


def test_azure_cloud_credentials_requires_service_principal(monkeypatch):
    monkeypatch.setattr(
        config,
        "_get_secret",
        lambda name, default="": "" if name.startswith("AZURE_") else default,
    )
    assert azure_cloud_credentials_configured() is False

    monkeypatch.setattr(
        config,
        "_get_secret",
        lambda name, default="": "value" if name.startswith("AZURE_") else default,
    )
    assert azure_cloud_credentials_configured() is True
