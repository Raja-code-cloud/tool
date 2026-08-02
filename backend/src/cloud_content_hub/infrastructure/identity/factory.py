"""Identity provider factory and composition helpers."""

from __future__ import annotations

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

from .config import IdentitySettings
from .interfaces.identity_provider import IdentityProvider
from .jwt import JwtService
from .providers.entra.provider import EntraIdentityProvider
from .providers.google.provider import GoogleIdentityProvider
from .providers.mock.provider import MockIdentityProvider
from .providers.placeholder import PlaceholderIdentityProvider
from .registry import ProviderRegistry
from .tokens import TokenService


def generate_rsa_key_pair() -> tuple[str, str]:
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    ).decode("ascii")
    public_pem = (
        private_key.public_key()
        .public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )
        .decode("ascii")
    )
    return private_pem, public_pem


class IdentityFactory:
    def __init__(self, settings: IdentitySettings) -> None:
        self._settings = settings
        private_pem = settings.signing_key_pem
        public_pem: str | None = None
        if private_pem is None:
            private_pem, public_pem = generate_rsa_key_pair()
        self._jwt = JwtService(settings, private_key_pem=private_pem, public_key_pem=public_pem)
        self._tokens = TokenService(settings, self._jwt)

    @property
    def jwt_service(self) -> JwtService:
        return self._jwt

    @property
    def token_service(self) -> TokenService:
        return self._tokens

    def build_registry(self) -> ProviderRegistry:
        registry = ProviderRegistry()
        if self._settings.mock_enabled:
            registry.register(
                MockIdentityProvider(self._settings, self._jwt, self._tokens)
            )
        if self._settings.entra_enabled:
            registry.register(
                EntraIdentityProvider(self._settings, self._jwt, self._tokens)
            )
        if self._settings.google_enabled:
            registry.register(
                GoogleIdentityProvider(self._settings, self._jwt, self._tokens)
            )
        if self._settings.placeholder_enabled:
            registry.register(PlaceholderIdentityProvider())
        return registry

    def default_provider(self, registry: ProviderRegistry) -> IdentityProvider:
        return registry.get(self._settings.default_provider)

    def build_provider(self, name: str) -> IdentityProvider:
        return self.build_registry().get(name)
