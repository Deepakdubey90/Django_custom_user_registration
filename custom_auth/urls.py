from django.conf.urls import patterns, include, url
from django.contrib import admin

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'custom_auth.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    url(r'^home/', 'custom_auth.views.home', name='home'),
    url(r'^register/', 'custom_auth.views.register_user'),
    url(r'^accounts/register_success/', 'custom_auth.views.register_success'),
    url(r'^accounts/login/', 'custom_auth.views.auth_login'),
    url(r'^accounts/loggedin/', 'custom_auth.views.loggedin'),
    url(r'^accounts/invalid/', 'custom_auth.views.invalid_login'),
    url(r'^confirm/(?P<activation_key>\w+)/', 'custom_auth.views.confirm_registration'),
    url(r'^admin/', include(admin.site.urls)),
)
