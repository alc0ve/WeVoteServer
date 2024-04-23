# apis_v1/documentation_source/issue_descriptions_retrieve_doc.py
# Brought to you by We Vote. Be good.
# -*- coding: UTF-8 -*-


def issue_descriptions_retrieve_doc_template_values(url_root):
    """
    Show documentation about issueDescriptionsRetrieve
    """
    optional_query_parameter_list = [
    ]

    potential_status_codes_list = [
    ]

    try_now_link_variables_dict = {
    }

    api_response = '[{\n' \
                   '  "success": boolean,\n' \
                   '  "status": string,\n' \
                   '  "issue_list": list\n' \
                   '   [\n' \
                   '     "considered_left": boolean,\n' \
                   '     "considered_right": boolean,\n' \
                   '     "issue_we_vote_id": string,\n' \
                   '     "issue_name": string,\n' \
                   '     "issue_description": string,\n' \
                   '     "issue_followers_count": number,\n' \
                   '     "issue_icon_local_path": string,\n' \
                   '     "linked_organization_count": number,\n' \
                   '     "linked_organization_preview_list": list' \
                   '      [{\n' \
                   '        "organization_name": string,\n' \
                   '        "organization_we_vote_id": string,\n' \
                   '        "twitter_description": string,\n' \
                   '        "twitter_followers_count": number,\n' \
                   '        "organization_twitter_handle": string,\n' \
                   '        "we_vote_hosted_profile_image_url_medium": string,\n' \
                   '        "we_vote_hosted_profile_image_url_tiny": string,\n' \
                   '      }],\n' \
                   '     "issue_photo_url_medium": string,\n' \
                   '     "issue_photo_url_tiny": string,\n' \
                   '   ],\n' \
                   '}]'

    template_values = {
        'api_name': 'issueDescriptionsRetrieve',
        'api_slug': 'issueDescriptionsRetrieve',
        'api_introduction':
            "",
        'try_now_link': 'apis_v1:issueDescriptionsRetrieveView',
        'try_now_link_variables_dict': try_now_link_variables_dict,
        'url_root': url_root,
        'get_or_post': 'GET',
        'optional_query_parameter_list': optional_query_parameter_list,
        'api_response': api_response,
        'api_response_notes':
            "",
        'potential_status_codes_list': potential_status_codes_list,
    }
    return template_values
