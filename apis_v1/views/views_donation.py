# apis_v1/views/views_donation.py
# Brought to you by We Vote. Be good.
# -*- coding: UTF-8 -*-

import json
import urllib
from urllib.parse import urlencode
from urllib.request import urlopen

import stripe
from django.http import HttpResponse, HttpResponseForbidden, HttpResponseNotFound
from django.views.decorators.csrf import csrf_exempt

import wevote_functions.admin
from config.base import get_environment_variable
from geoip.controllers import voter_location_retrieve_from_ip_for_api
from stripe_donations.controllers import donation_active_paid_plan_retrieve, donation_with_stripe_for_api, \
    donation_process_stripe_webhook_event, \
    donation_refund_for_api, donation_subscription_cancellation_for_api, donation_journal_history_for_a_voter
from stripe_donations.controllers import donation_lists_for_a_voter
from stripe_donations.models import StripeManager
from stripe_ip_history.controllers import check_for_excessive_stripe_access
from voter.models import fetch_voter_we_vote_id_from_voter_device_link, VoterManager
from wevote_functions.functions import get_ip_from_headers, positive_value_exists, get_voter_device_id
from wevote_settings.models import fetch_stripe_processing_enabled_state

logger = wevote_functions.admin.get_logger(__name__)

WE_VOTE_SERVER_ROOT_URL = get_environment_variable("WE_VOTE_SERVER_ROOT_URL")


def donation_with_stripe_view(request):  # donationWithStripe
    """
    Make a charge with a stripe token. This could either be:
    A) one-time or monthly donation
    B) payment for a subscription plan
    :type request: object
    :param request:
    :return:
    """

    voter_device_id = get_voter_device_id(request)  # We standardize how we take in the voter_device_id

    # Before anything else, screen for DOS or scammers
    # https://wevotedeveloper.com:8000/apis/v1/donationWithStripe
    voter_manager = VoterManager()
    results = voter_manager.retrieve_voter_from_voter_device_id(voter_device_id)
    ip_address = get_ip_from_headers(request)
    voter_found = positive_value_exists(results['voter_found'])
    if voter_found:
        voter = results['voter']
        we_vote_id = voter.we_vote_id
        name = voter.first_name
        name += (" " + voter.last_name) if voter else ' name'
        signed_in = voter.is_signed_in() if voter else False
        signed_in_twitter = voter.signed_in_twitter() if voter else False
        signed_in_facebook = voter.signed_in_facebook() if voter else False
        logger.error('(Ok) DONATION voter found (%s) %s - %s, signedIn %s, twitter %s, facebook %s, request %s' %
                     (ip_address, name, we_vote_id, signed_in, signed_in_twitter, signed_in_facebook,
                      dict(request.GET)))
    else:
        logger.error('(Ok) DONATION voter NOT found (%s) request %s' % (ip_address, dict(request.GET)))
        return HttpResponseForbidden("error")

    # 1/2/2023:  If disabled on the "Stripe Fraudulent and Suspect Charges" page, no stripe charges can go through
    if not fetch_stripe_processing_enabled_state():
        logger.error(
            'DONATION request arrived while API disabled (%s) %s - %s, signedIn %s, twitter %s, facebook %s, request %s'
            % (ip_address, name, we_vote_id, signed_in, signed_in_twitter, signed_in_facebook, dict(request.GET)))
        return HttpResponseNotFound("Stripe transactions disabled by WeVote")

    logger.error('(Ok) DONATION voter PASSED SCREEN (%s) %s - %s, signedIn %s, twitter %s, facebook %s' %
                 (ip_address, name, we_vote_id, signed_in, signed_in_twitter, signed_in_facebook))

    # Handle the hopefully valid API call
    token = request.GET.get('token', '')
    email = request.GET.get('email', '')
    donation_amount = request.GET.get('donation_amount', 0)
    is_chip_in = positive_value_exists(request.GET.get('is_chip_in', False))
    is_monthly_donation = positive_value_exists(request.GET.get('is_monthly_donation', False))
    is_premium_plan = positive_value_exists(request.GET.get('is_premium_plan', False))
    client_ip = request.GET.get('client_ip', '')
    campaignx_we_vote_id = request.GET.get('campaignx_we_vote_id', '')
    payment_method_id = request.GET.get('payment_method_id', '')
    coupon_code = request.GET.get('coupon_code', '')
    premium_plan_type_enum = request.GET.get('premium_plan_type_enum', '')

    voter_we_vote_id = ''

    if positive_value_exists(voter_device_id):
        voter_we_vote_id = fetch_voter_we_vote_id_from_voter_device_link(voter_device_id)
    else:
        logger.error('%s', 'DONATION donation_with_stripe_view voter_we_vote_id is missing')

    voter_manager = VoterManager()
    linked_organization_we_vote_id = \
        voter_manager.fetch_linked_organization_we_vote_id_by_voter_we_vote_id(voter_we_vote_id)

    if positive_value_exists(token):
        logger.error('(Ok) DONATION donation_with_stripe_for_app called '
                     '(%s) %s - %s, signedIn %s, twitter %s, facebook %s, request %s' %
                     (ip_address, name, we_vote_id, signed_in, signed_in_twitter, signed_in_facebook,
                      dict(request.GET)))

        results = donation_with_stripe_for_api(request, token, email, donation_amount,
                                               is_chip_in, is_monthly_donation, is_premium_plan,
                                               client_ip, campaignx_we_vote_id, payment_method_id, coupon_code,
                                               premium_plan_type_enum,
                                               voter_we_vote_id, linked_organization_we_vote_id )

        org_subs_already_exists = results['org_subs_already_exists'] if \
            'org_subs_already_exists' in results else False

        active_results = donation_active_paid_plan_retrieve(linked_organization_we_vote_id, voter_we_vote_id)
        active_paid_plan = active_results['active_paid_plan']
        # donation_plan_definition_list_json = active_results['donation_plan_definition_list_json']
        donation_subscription_list, donation_payments_list = donation_lists_for_a_voter(voter_we_vote_id)
        json_data = {
            'status': results['status'],
            'success': results['success'],
            'active_paid_plan': active_paid_plan,
            'amount_paid': results['amount_paid'],
            'charge_id': results['charge_id'],
            'stripe_customer_id': results['stripe_customer_id'],
            'donation_subscription_list': donation_subscription_list,
            'donation_payments_list': donation_payments_list,
            'error_message_for_voter': results['error_message_for_voter'],
            'stripe_failure_code': results['stripe_failure_code'],
            'is_monthly_donation': is_monthly_donation,
            'organization_saved': results['organization_saved'],
            'org_subs_already_exists': org_subs_already_exists,
            'premium_plan_type_enum': results['premium_plan_type_enum'],
            'saved_donation_in_log': results['donation_entry_saved'],
            'saved_stripe_donation': results['saved_stripe_donation'],
        }
        return HttpResponse(json.dumps(json_data), content_type='application/json')

    else:
        json_data = {
            'status': "TOKEN_IS_MISSING ",
            'success': False,
            'amount_paid': 0,
            'error_message_for_voter': 'Cannot connect to payment processor.',
            'organization_saved': False,
            'premium_plan_type_enum': '',
        }
        return HttpResponse(json.dumps(json_data), content_type='application/json')


def donation_refund_view(request):  # donationRefund
    """
    Refund a stripe charge
    :type request: object
    :param request:
    :return:
    """

    charge_id = request.GET.get('charge', '')
    voter_device_id = get_voter_device_id(request)  # We standardize how we take in the voter_device_id
    ip_address = get_ip_from_headers(request)

    # 1/3/2023:  If disabled on the "Stripe Fraudulent and Suspect Charges" page, no stripe refunds can go through
    if not fetch_stripe_processing_enabled_state():
        logger.error('DONATION refund request arrived while API disabled (%s) -- %s' % (ip_address, charge_id))
        return HttpResponseNotFound("Stripe refunds disabled by WeVote")

    if positive_value_exists(voter_device_id):
        voter_we_vote_id = fetch_voter_we_vote_id_from_voter_device_link(voter_device_id)
        if len(charge_id) > 1:
            results = donation_refund_for_api(request, charge_id, voter_we_vote_id)
            logger.error('(Ok) DONATION REFUNDED donation_refund_for_api (%s) charge_id %s, voter_we_vote_id %s' %
                         (ip_address, charge_id, voter_we_vote_id))
            json_data = {
                'success': str(results),
                'charge_id': charge_id,
                'donation_list': donation_journal_history_for_a_voter(voter_we_vote_id),
                'voter_we_vote_id': voter_we_vote_id,
            }
        else:
            logger.error('%s', 'DONATION donation_refund_view voter_we_vote_id is missing')
            json_data = {
                'status': "VOTER_WE_VOTE_ID_IS_MISSING",
                'success': False,
            }
    else:
        logger.error('%s', 'DONATION donation_refund_view stripe_charge_id is missing')
        json_data = {
            'status': "STRIPE_CHARGE_ID_IS_MISSING",
            'success': False,
        }

    return HttpResponse(json.dumps(json_data), content_type='application/json')


def donation_cancel_subscription_view(request):  # donationCancelSubscription
    """
    Cancel a stripe subscription or subscription plan
    :type request: object
    :param request:
    :return:
    """

    premium_plan_type_enum = request.GET.get('premium_plan_type_enum', '')
    stripe_subscription_id = request.GET.get('stripe_subscription_id', '')
    voter_device_id = get_voter_device_id(request)  # We standardize how we take in the voter_device_id

    if positive_value_exists(voter_device_id):
        voter_we_vote_id = fetch_voter_we_vote_id_from_voter_device_link(voter_device_id)
        if len(voter_we_vote_id) > 0:
            json_data = donation_subscription_cancellation_for_api(
                voter_we_vote_id, premium_plan_type_enum=premium_plan_type_enum, stripe_subscription_id=stripe_subscription_id)
        else:
            logger.error('%s', 'DONATION donation_cancel_subscription_view voter_we_vote_id is missing')
            json_data = {
                'status': "VOTER_WE_VOTE_ID_IS_MISSING ",
                'success': False,
            }
    else:
        logger.error('%s', 'DONATION donation_cancel_subscription_view stripe_subscription_id is missing')
        json_data = {
            'status': "STRIPE_SUBSCRIPTION_ID_IS_MISSING ",
            'success': False,
        }

    return HttpResponse(json.dumps(json_data), content_type='application/json')


# Using ngrok to test Stripe Webhook
# Start ngrok (install it first!)
# (WeVoteServerPy3.7) Steves-MacBook-Pro-32GB-Oct-2018:PycharmProjects stevepodell$ ~/PythonProjects/ngrok http 8000 -host-header="localhost:8000"
# https://a9a761d9.ngrok.io/apis/v1/donationStripeWebhook/
# http://a9a761d9.ngrok.io -> localhost:8000
# Important!!!!!!!   django urls without a trailing slash do not redirect   !!!!!!
# The webhook in the stripe console HAS TO END WITH A '/' or you are doomed to waste a bunch of time!
@csrf_exempt
def donation_stripe_webhook_view(request):    # donationStripeWebhook
    # print('first line in donation_stripe_webhook')
    payload = request.body.decode('utf-8')

    try:
        stripe.api_key = get_environment_variable("STRIPE_SECRET_KEY")
        event = stripe.Event.construct_from(json.loads(payload), stripe.api_key)

    except ValueError as e:
        logger.error("DONATION donation_stripe_webhook_view, Stripe returned ValueError: " + str(e))
        return HttpResponse(status=400)

    except stripe.error.SignatureVerificationError as err:
        logger.error("DONATION donation_stripe_webhook_view, Stripe returned SignatureVerificationError: " + str(err))
        return HttpResponse(status=400)

    except Exception as err:
        logger.error("DONATION donation_stripe_webhook_view: " + str(err))
        return HttpResponse(status=400)

    ip_address = get_ip_from_headers(request)

    # 1/3/2023:  If disabled on the "Stripe Fraudulent and Suspect Charges" page, stripe WebHooks are alos disabled
    if not fetch_stripe_processing_enabled_state():
        ip_address = get_ip_from_headers(request)
        try:
            logger.error('DONATION WebHook arrived while API disabled (%s) -- %s Event: %s' %
                         (ip_address, event.type, json.dumps(event)))
        except:
            logger.error('DONATION WebHook arrived while API disabled (%s) -- %s Event: Unable to serialize event' %
                         (ip_address, event.type))
        return HttpResponseNotFound("Stripe WebHooks disabled by WeVote")

    logger.error("DONATION donation_stripe_webhook_view INVOKED: " + event.type + " --  " +  ip_address)
    donation_process_stripe_webhook_event(event)

    return HttpResponse(status=200)


def donation_history_list_view(request):   # donationHistory
    """
    Get the donor history list for a voter
    :type request: object
    :param request:
    :return:
    """

    stripe_subscription_id = request.GET.get('stripe_subscription_id', '')
    voter_device_id = get_voter_device_id(request)  # We standardize how we take in the voter_device_id
    status = ""
    active_paid_plan = {
        'last_amount_paid':         0,
        'premium_plan_type_enum':   '',
        'subscription_active':      False,
        'subscription_canceled_at': '',
        'subscription_ended_at':    '',
        'stripe_subscription_id':   stripe_subscription_id,
    }
    donation_subscription_list = []
    donation_payments_list = []

    if positive_value_exists(voter_device_id):
        voter_manager = VoterManager()
        results = voter_manager.retrieve_voter_from_voter_device_id(voter_device_id, read_only=True)
        if not results['voter_found']:
            logger.error("DONATION donation_history_list received invalid voter_device_id: " + voter_device_id)
            status += "DONATION_HISTORY_LIST-INVALID_VOTER_DEVICE_ID_PASSED "
            success = False
        else:
            success = True
            voter = results['voter']
            voter_we_vote_id = voter.we_vote_id
            linked_organization_we_vote_id = voter.linked_organization_we_vote_id

            donation_subscription_list, donation_payments_list = donation_lists_for_a_voter(voter_we_vote_id)
            # July 2021, active_results fails due to 'source' redefintion in api
            # active_results = donation_active_paid_plan_retrieve(linked_organization_we_vote_id, voter_we_vote_id)
            # active_paid_plan = active_results['active_paid_plan']

        json_data = {
            # 'active_paid_plan':                 active_paid_plan,
            'donation_subscription_list':       donation_subscription_list,
            'donation_payments_list':           donation_payments_list,
            'status':                           status,
            'success':                          success,
        }
    else:
        logger.error('%s', 'DONATION donation_history_list stripe_subscription_id is missing')
        json_data = {
            'active_paid_plan': active_paid_plan,
            'donation_list': [],
            'donation_plan_definition_list': [],
            'status': "DONATION_HISTORY_LIST-STRIPE_SUBSCRIPTION_ID_IS_MISSING",
            'success': False,
        }

    return HttpResponse(json.dumps(json_data), content_type='application/json')


# def coupon_summary_retrieve_for_api_view(request):  # couponSummaryRetrieve
#     coupon_code = request.GET.get('coupon_code', '')
#     voter_device_id = get_voter_device_id(request)  # We standardize how we take in the voter_device_id
#
#     if positive_value_exists(voter_device_id):
#         voter_we_vote_id = fetch_voter_we_vote_id_from_voter_device_link(voter_device_id)
#         json_data = DonationManager.retrieve_coupon_summary(coupon_code)
#     else:
#         json_data = {
#             'success': False,
#             'status': "coupon_summary_retrieve_for_api_view received bad voter_device_id",
#         }
#
#     return HttpResponse(json.dumps(json_data), content_type='application/json')
#
#
# def default_pricing_for_api_view(request):  # defaultPricing
#     json_data = DonationManager.retrieve_default_pricing()
#
#     return HttpResponse(json.dumps(json_data), content_type='application/json')
#
#
# def validate_coupon_for_api_view(request):  # validateCoupon
#     premium_plan_type_enum = request.GET.get('premium_plan_type_enum', '')
#     coupon_code = request.GET.get('coupon_code', '')
#     voter_device_id = get_voter_device_id(request)  # We standardize how we take in the voter_device_id
#     print("validate_coupon_for_api_view, premium_plan_type_enum: " + premium_plan_type_enum + ", coupon_code: " + coupon_code)
#
#     if positive_value_exists(voter_device_id):
#         voter_we_vote_id = fetch_voter_we_vote_id_from_voter_device_link(voter_device_id)
#         json_data = DonationManager.validate_coupon(premium_plan_type_enum, coupon_code)
#     else:
#         json_data = {
#             'success': False,
#             'status': "validate_coupon_for_api_view received bad voter_device_id",
#         }
#
#     return HttpResponse(json.dumps(json_data), content_type='application/json')
#
#
# def create_new_plan_for_api_view(request):
#     authority_required = {'admin'}
#     if not voter_has_authority(request, authority_required):
#         return redirect_to_sign_in_page(request, authority_required)
#
#     coupon_code = request.GET.get('couponCode')
#     premium_plan_type_enum = request.GET.get('planTypeEnum')
#     hidden_plan_comment = request.GET.get('hiddenPlanComment')
#     coupon_applied_message = request.GET.get('couponAppliedMessage')
#     monthly_price_stripe = request.GET.get('monthlyPriceStripe')
#     monthly_price_stripe = monthly_price_stripe if monthly_price_stripe != '' else 0
#     annual_price_stripe = request.GET.get('annualPriceStripe')
#     annual_price_stripe = annual_price_stripe if annual_price_stripe != '' else 0
#     master_feature_package = request.GET.get('masterFeatureType')
#     features_provided_bitmap = request.GET.get('featuresProvidedBitmap')
#     coupon_expires_date = request.GET.get('couponExpiresDate', None)
#     if len(coupon_expires_date) == 0:
#         coupon_expires_date = None
#     print("create_new_plan_for_api_view, premium_plan_type_enum: " + premium_plan_type_enum + ", coupon_code: " + coupon_code)
#     plan_on_stage = 0
#
#     voter_device_id = get_voter_device_id(request)  # We standardize how we take in the voter_device_id
#     if positive_value_exists(voter_device_id):
#         voter_we_vote_id = fetch_voter_we_vote_id_from_voter_device_link(voter_device_id)
#         plan_on_stage = OrganizationSubscriptionPlans.objects.create(
#             coupon_code=coupon_code,
#             premium_plan_type_enum=premium_plan_type_enum,
#             hidden_plan_comment=hidden_plan_comment,
#             coupon_applied_message=coupon_applied_message,
#             monthly_price_stripe=monthly_price_stripe,
#             annual_price_stripe=annual_price_stripe,
#             master_feature_package=master_feature_package,
#             features_provided_bitmap=features_provided_bitmap,
#             coupon_expires_date=coupon_expires_date)
#         status = "create_new_plan_for_api_view succeeded"
#     else:
#         status = "create_new_plan_for_api_view received bad voter_device_id",
#
#     json_data = {
#         'success': positive_value_exists(plan_on_stage.id),
#         'status': status,
#         'id': plan_on_stage.id if positive_value_exists(plan_on_stage.id) else 0.
#         }
#
#     return HttpResponse(json.dumps(json_data), content_type='application/json')
#
#
# def delete_plan_for_api_view(request):
#     authority_required = {'admin'}
#     if not voter_has_authority(request, authority_required):
#         return redirect_to_sign_in_page(request, authority_required)
#
#     id = request.GET.get('id')
#     print("delete_coupon_for_api_view, sql id: " + id)
#
#     try:
#         if positive_value_exists(id):
#             OrganizationSubscriptionPlans.objects.filter(id=id).delete()
#             status = "DELETE_PLAN_SUCCESSFUL"
#             success = True
#         else:
#             status = "DELETE_PLAN-MISSING_ID"
#             success = False
#     except Exception as e:
#         status = "DELETE_PLAN-DATABASE_DELETE_EXCEPTION"
#         success = False
#
#     json_data = {
#         'success': success,
#         'status': status,
#         'id': id,
#         }
#
#     return HttpResponse(json.dumps(json_data), content_type='application/json')


def does_paid_subscription_exist_for_api(request):  # doesOrgHavePaidPlan
    voter_device_id = get_voter_device_id(request)  # We standardize how we take in the voter_device_id
    voter_we_vote_id = ''

    if positive_value_exists(voter_device_id):
        voter_we_vote_id = fetch_voter_we_vote_id_from_voter_device_link(voter_device_id)
    else:
        logger.error('%s', 'DONATION donation_with_stripe_view voter_we_vote_id is missing')
    voter_manager = VoterManager()
    organization_we_vote_id = voter_manager.fetch_linked_organization_we_vote_id_by_voter_we_vote_id(voter_we_vote_id)
    found_live_paid_subscription_for_the_org = StripeManager.does_paid_subscription_exist(organization_we_vote_id)

    json_data = {
        'org_has_active_paid_plan': found_live_paid_subscription_for_the_org,
        'success': True,
    }

    return HttpResponse(json.dumps(json_data), content_type='application/json')


def log_to_cloudwatch_view(request):            # logToCloudWatch
    # This was created for Stripe Captchas, but could be used for any situation where we want to log WebApp errors to
    # CloudWatch WeVoteServer Python logs

    error_level = request.GET.get('error_level', 'ERROR')
    message = urllib.parse.unquote(request.GET.get('message', 'No message supplied'))
    voter_device_id = get_voter_device_id(request)  # We standardize how we take in the voter_device_id
    ip_address = get_ip_from_headers(request)
    we_vote_id = 'failed'
    success = True
    try:
        voter_manager = VoterManager()
        results = voter_manager.retrieve_voter_from_voter_device_id(voter_device_id)
        voter = results['voter']
        we_vote_id = voter.we_vote_id
    except Exception as e:
        success = False
        logger.error('log_to_cloudwatch_view failed to retrieve a voter for device_id: ', voter_device_id, e)

    line = "WebApp (%s -- %s): %s" % (ip_address, we_vote_id, message)

    if error_level == "ERROR":
        logger.error(line)
    elif error_level == "INFO":
        logger.info(line)
    elif error_level == "DEBUG":
        logger.debug(line)

    results = {
        'success': success,
    }

    return HttpResponse(json.dumps(results), content_type='application/json')


def google_recaptcha_verify_view(request):            # googleRecaptchaVerifyView
    recaptcha_uri = 'https://www.google.com/recaptcha/api/siteverify'
    token = request.GET.get('token', None)
    secret_key = get_environment_variable("GOOGLE_RECAPTCHA_SECRET_KEY")
    remote_ip = get_ip_from_headers(request)
    params = urlencode({
        'secret': secret_key,
        'response': token,
        'remote_ip': remote_ip,
    })
    success = False
    captcha_score = 0

    geoip_results = voter_location_retrieve_from_ip_for_api(request)
    country_code = geoip_results['country_code']
    blocked_by_country = False
    blocked_by_frequency_hourly = False
    blocked_by_frequency_weekly = False
    captcha_score = 0.0
    captcha_success = False

    if country_code == 'US':
        data = urlopen(recaptcha_uri, params.encode('utf-8')).read()
        result = json.loads(data)
        captcha_success = result.get('success', None)
        captcha_score = result.get('score', None)
    else:
        blocked_by_country = True

    blocked_by_captcha = captcha_score < 0.5
    blocked_by_frequency_hours = False
    blocked_by_frequency_days = False

    voter_device_id = get_voter_device_id(request)  # We standardize how we take in the voter_device_id
    we_vote_id = 'failed'
    email = ''

    try:
        voter_manager = VoterManager()
        results = voter_manager.retrieve_voter_from_voter_device_id(voter_device_id)
        voter = results['voter']
        we_vote_id = voter.we_vote_id
        email = voter.email

        access_results = check_for_excessive_stripe_access(
            remote_ip, country_code, we_vote_id, email, captcha_score, captcha_success, blocked_by_captcha,
            blocked_by_country)
        success = access_results['success']
        blocked_by_frequency_hours = access_results['blocked_by_frequency_hours']
        blocked_by_frequency_days = access_results['blocked_by_frequency_days']

    except Exception as e:
        success = False
        logger.error('google_recaptcha_verify failed to retrieve a voter for device_id: ', voter_device_id, e)

    # We don't want to supply the potential "card tester" with the reason they are blocked via a JavaScript debugger
    blocked_by_other = blocked_by_country or blocked_by_frequency_hours or blocked_by_frequency_days
    was_blocked = blocked_by_captcha or blocked_by_other
    block = "BLOCKED" if was_blocked else "PASSED"
    log_template = "(Ok) reCAPTCHA %s ip: %s, country %s, we_vote_id: %s, verified: %s, score: %.2f, " \
                   "blockedByCaptcha: %s, blockedByCountry: %s, blockedByHours: %s, blockedByDays: %s"
    logger.error(log_template % (block, remote_ip, country_code, we_vote_id, success, captcha_score, blocked_by_captcha,
                 blocked_by_country, blocked_by_frequency_hours, blocked_by_frequency_days))

    results = {
        'allowedToDonate': not was_blocked,
        'captchaScore': captcha_score,
        'blockedByCaptcha': blocked_by_captcha,
        'blockedByOther': blocked_by_other,
    }

    return HttpResponse(json.dumps(results), content_type='application/json')
