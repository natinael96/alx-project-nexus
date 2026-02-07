"""
Custom Swagger/OpenAPI schema configuration for organized API documentation.

Groups all API endpoints into logical sections for better readability.
"""
from drf_yasg.inspectors import SwaggerAutoSchema


class TaggedAutoSchema(SwaggerAutoSchema):
    """
    Custom auto schema that assigns descriptive tags to group
    API endpoints into logical sections in Swagger UI.
    """

    # Map view module paths → tag name
    MODULE_TAG_MAP = {
        'apps.accounts.views': 'Authentication',
        'apps.accounts.views_profile': 'User Profiles',
        'apps.accounts.views_security': 'Security',
        'apps.accounts.views_oauth': 'OAuth / Social Login',
        'apps.jobs.views_job_enhancements': 'Job Analytics & Insights',
        'apps.jobs.views_application_enhancements': 'Application Management',
        'apps.jobs.views_search': 'Search',
        'apps.core.views': 'Health & Monitoring',
        'apps.core.views_notifications': 'Notifications',
        'apps.core.views_export': 'Data Export',
        'apps.core.views_audit': 'Audit Logs',
        'apps.core.views_file_download': 'File Downloads',
    }

    # For modules with multiple ViewSets, map by class name keyword
    CLASS_TAG_MAP = {
        'apps.jobs.views': {
            'Category': 'Categories',
            'Job': 'Jobs',
            'Application': 'Applications',
        },
    }

    # Specific function-based view overrides (module.func_name → tag)
    FUNCTION_TAG_MAP = {
        # Split auth module: general auth vs user management
        'apps.accounts.views.register_user': 'Authentication',
        'apps.accounts.views.login_user': 'Authentication',
        'apps.accounts.views.refresh_token': 'Authentication',
        'apps.accounts.views.change_password': 'Authentication',
        'apps.accounts.views.get_current_user': 'Authentication',
        'apps.accounts.views.update_current_user': 'Authentication',
    }

    def get_tags(self, operation_keys=None):
        # Get the view's module and class/function name
        view = self.view
        view_cls = view.__class__
        module = view_cls.__module__
        cls_name = view_cls.__name__

        # For function-based views wrapped by DRF, the class is WrappedAPIView
        # Check if there's a specific function override
        if hasattr(view, 'initkwargs') and 'initkwargs' in dir(view):
            func_name = getattr(view, 'cls', view_cls).__name__
        else:
            func_name = cls_name

        # 1. Check specific function overrides
        func_key = f"{module}.{func_name}"
        if func_key in self.FUNCTION_TAG_MAP:
            return [self.FUNCTION_TAG_MAP[func_key]]

        # 2. Check class-level mapping for multi-ViewSet modules
        if module in self.CLASS_TAG_MAP:
            for keyword, tag in self.CLASS_TAG_MAP[module].items():
                if keyword in cls_name:
                    return [tag]

        # 3. Check module-level mapping
        if module in self.MODULE_TAG_MAP:
            return [self.MODULE_TAG_MAP[module]]

        # 4. Fallback: derive from operation_keys (URL path segments)
        if operation_keys and len(operation_keys) >= 2:
            # Use the second key as the tag (after 'api')
            tag = operation_keys[0]
            if tag in ('api', 'v1'):
                tag = operation_keys[1] if len(operation_keys) > 1 else tag
            return [tag.replace('_', ' ').replace('-', ' ').title()]

        return super().get_tags(operation_keys)
