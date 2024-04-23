# organization/views.py
# Brought to you by We Vote. Be good.
# -*- coding: UTF-8 -*-

from django.http import JsonResponse
from follow.models import FollowOrganizationManager
from voter.models import fetch_voter_id_from_voter_device_link
import wevote_functions.admin
from wevote_functions.functions import get_voter_api_device_id


logger = wevote_functions.admin.get_logger(__name__)


# NOTE: We prefer organization_follow_api_view
def organization_follow_view(request, organization_id):
    logger.debug("organization_follow_view {organization_id}".format(
        organization_id=organization_id
    ))
    voter_api_device_id = get_voter_api_device_id(request)
    voter_id = fetch_voter_id_from_voter_device_link(voter_api_device_id)

    follow_organization_manager = FollowOrganizationManager()
    results = follow_organization_manager.toggle_on_voter_following_organization(voter_id, organization_id)
    if results['success']:
        return JsonResponse({0: "success"})
    else:
        return JsonResponse({0: "failure"})


# NOTE: We prefer organization_stop_following_api_view
def organization_stop_following_view(request, organization_id):
    logger.debug("organization_stop_following_view {organization_id}".format(
        organization_id=organization_id
    ))
    voter_api_device_id = get_voter_api_device_id(request)
    voter_id = fetch_voter_id_from_voter_device_link(voter_api_device_id)

    follow_organization_manager = FollowOrganizationManager()
    results = follow_organization_manager.toggle_off_voter_following_organization(voter_id, organization_id)
    if results['success']:
        return JsonResponse({0: "success"})
    else:
        return JsonResponse({0: "failure"})
