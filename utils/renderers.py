import typing

import rest_framework.renderers


class BrowsableAPIRenderer(rest_framework.renderers.BrowsableAPIRenderer):
    """Renders the browsable api pages, but skips the forms."""

    def get_context(self, *args: typing.Any, **kwargs: typing.Any) -> dict:
        ctx = super().get_context(*args, **kwargs)
        # ctx['display_edit_forms'] = False  # I prefer to keep json forms
        return ctx

    def get_rendered_html_form(self, *args: typing.Any, **kwargs: typing.Any) -> typing.Optional[str]:
        if args[2] == 'DELETE':
            return super().get_rendered_html_form(*args, **kwargs)
        return None
