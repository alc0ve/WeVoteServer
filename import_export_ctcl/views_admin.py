# import_export_ctcl/views_admin.py
# Brought to you by We Vote. Be good.
# -*- coding: UTF-8 -*-

from .controllers import import_ctcl_from_xml
from django.contrib.messages import get_messages
from django.shortcuts import render
import wevote_functions.admin
from voter.models import voter_has_authority
from admin_tools.views import redirect_to_sign_in_page
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.urls import reverse
logger = wevote_functions.admin.get_logger(__name__)


def import_export_ctcl_index_view(request):
    """
    Provide an index of import/export actions (for We Vote data maintenance)
    """
    messages_on_stage = get_messages(request)

    template_values = {
        'messages_on_stage':    messages_on_stage,
    }
    return render(request, 'import_export_ctcl/index.html', template_values)


@login_required
def import_ctcl_from_xml_view(request):
    """
    Take data from CTCL API Endpoint, (an XML file, for now) and store in the local Voting Info Project database
    """
    # If person isn't signed in, we don't want to let them visit this page yet
    # admin, analytics_admin, partner_organization, political_data_manager, political_data_viewer, verified_volunteer
    authority_required = {'admin'}
    if not voter_has_authority(request, authority_required):
        return redirect_to_sign_in_page(request, authority_required)

    results = import_ctcl_from_xml(request)

    if not results['success']:
        messages.add_message(request, messages.ERROR, results['status'])
    else:
        messages.add_message(request, messages.INFO, 'CTCL sample data imported.')

    return HttpResponseRedirect(reverse('import_export_ctcl:import_export_ctcl_index', args=()))