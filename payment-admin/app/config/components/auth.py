AUTH_USER_MODEL = "billing.User"
AUTHENTICATION_BACKENDS = [
    "billing.backends.CustomBackend",
]
