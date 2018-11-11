from django.conf import settings
from django.urls import include, path
from django.conf.urls.static import static
from django.contrib import admin
from django.views.generic import RedirectView
from django.views import defaults as default_views
from rest_framework import routers

import pizzeria_dangelo.customer_orders.views
import pizzeria_dangelo.pizza.views
import pizzeria_dangelo.extras.views

router = routers.DefaultRouter()
router.register(r'sizes', pizzeria_dangelo.pizza.views.PizzaSizeViewSet)
router.register(r'crusts', pizzeria_dangelo.pizza.views.PizzaCrustViewSet)
router.register(r'toppings', pizzeria_dangelo.pizza.views.PizzaToppingViewSet)
router.register(r'pizzacomponents', pizzeria_dangelo.pizza.views.PizzaComponentViewSet)
router.register(r'pizzas', pizzeria_dangelo.pizza.views.PizzaViewSet)
router.register(r'extras', pizzeria_dangelo.extras.views.ExtraViewSet)
router.register(r'extracategories', pizzeria_dangelo.extras.views.ExtraCategoryViewSet)
router.register(r'orders', pizzeria_dangelo.customer_orders.views.OrderViewSet)


urlpatterns = [
    path("", RedirectView.as_view(url="/api/1/"), name="home"),
    # Django Admin, use {% url 'admin:index' %}
    path(settings.ADMIN_URL, admin.site.urls),
    # User management
    path(
        "users/",
        include("pizzeria_dangelo.users.urls", namespace="users"),
    ),
    path("accounts/", include("allauth.urls")),
    # Your stuff: custom urls includes go here
    path(
        "api/1/",
        include((router.urls, 'api'), namespace='api1'),
    ),
    path(
        "api-auth/",
        include('rest_framework.urls', namespace='rest_framework'),
    ),
] + static(
    settings.MEDIA_URL, document_root=settings.MEDIA_ROOT,
)

if settings.DEBUG:
    # This allows the error pages to be debugged during development, just visit
    # these url in browser to see how these error pages look like.
    urlpatterns += [
        path(
            "400/",
            default_views.bad_request,
            kwargs={"exception": Exception("Bad Request!")},
        ),
        path(
            "403/",
            default_views.permission_denied,
            kwargs={"exception": Exception("Permission Denied")},
        ),
        path(
            "404/",
            default_views.page_not_found,
            kwargs={"exception": Exception("Page not Found")},
        ),
        path("500/", default_views.server_error),
    ]
    if "debug_toolbar" in settings.INSTALLED_APPS:
        import debug_toolbar

        urlpatterns = [path("__debug__/", include(debug_toolbar.urls))] + urlpatterns
