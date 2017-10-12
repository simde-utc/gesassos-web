# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render

from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.urls import reverse
from django.template import loader
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from api import ginger

@login_required
def contributors(request):
    template = loader.get_template('ginger/index.html')
    
    context = {
        'app_name': "ginger",
        'view_name' : "contributors",
        'all': "all",
    }
    return HttpResponse(template.render(context, request))

@login_required
def api(request):
    if request.method == 'POST':
        # TODO: check data
        print(request.POST.items())
        response = ginger.addKey(request.POST.get("login", ""),
            request.POST.get("description", ""),
            request.POST.get("users_add", False) == "True",
            request.POST.get("users_delete", False) == "True",
            request.POST.get("users_edit", False) == "True",
            request.POST.get("users_badge", False) == "True",
            request.POST.get("contributions_add", False) == "True",
            request.POST.get("contributions_delete", False) == "True",
            request.POST.get("contributions_read", False) == "True",
            request.POST.get("stats", False) == "True",
            request.POST.get("settings_read", False) == "True",
            request.POST.get("keys_all", False) == "True")
        print(response)

    context = {
        'app_name': "ginger",
        'view_name' : "api",
        'keys': ginger.getKeys(),
        'ginger_rights': [
            "users_add",
            "users_delete",
            "users_edit",
            "users_badge",
            "contributions_add",
            "contributions_delete",
            "contributions_read",
            "stats_read",
            "settings_read",
            "keys_all"
        ],
        'assos': [
            {
                'login': "simde",
                'name': "SiMDE"
            },
            {
                'login': "etuville",
                'name': "Étuville"
            },
            {
                'login': "bde",
                'name': "BDE"
            }
        ]
    }
    context["ginger_rights"].sort()
    return render(request, 'ginger/api.html', context)

@login_required
def delete_key(request, key):
    response = ginger.deleteKey(key)
    return HttpResponseRedirect(reverse('ginger:api', args=()))


# @login_required
# def api_add(request):