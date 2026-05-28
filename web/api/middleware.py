"""Legacy API middleware placeholder.

This module remains present only for backwards compatibility with any
references that may still exist in omitted or archived deployments.

The application now uses DRF authentication via api.authentication.APIKeyAuthentication
and the api.permissions.HasAPIKeyOrIsAuthenticated permission class.
"""

__all__ = []
