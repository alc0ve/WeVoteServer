# apis_v1/documentation_source/voter_all_bookmarks_status_retrieve_doc.py
# Brought to you by We Vote. Be good.
# -*- coding: UTF-8 -*-


def voter_all_bookmarks_status_retrieve_doc_template_values(url_root):
    """
    Show documentation about voterAllBookmarksStatusRetrieve
    """
    required_query_parameter_list = [
        {
            'name':         'voter_device_id',
            'value':        'string',  # boolean, integer, long, string
            'description':  'An 88 character unique identifier linked to a voter record on the server',
        },
        {
            'name':         'api_key',
            'value':        'string (from post, cookie, or get (in that order))',  # boolean, integer, long, string
            'description':  'The unique key provided to any organization using the WeVoteServer APIs',
        },
    ]
    optional_query_parameter_list = [
    ]

    potential_status_codes_list = [
        {
            'code':         'VALID_VOTER_DEVICE_ID_MISSING',
            'description':  'Cannot proceed. A valid voter_device_id parameter was not included.',
        },
        {
            'code':         'VALID_VOTER_ID_MISSING',
            'description':  'Cannot proceed. A valid voter_id was not found.',
        },
    ]

    try_now_link_variables_dict = {
    }

    api_response = '{\n' \
                   '  "success": boolean,\n' \
                   '  "status": string,\n' \
                   '  "bookmark_list": list\n' \
                   '   [\n' \
                   '     "ballot_item_we_vote_id": string,\n' \
                   '     "bookmark_on": boolean,\n' \
                   '   ],\n' \
                   '}'

    template_values = {
        'api_name': 'voterAllBookmarksStatusRetrieve',
        'api_slug': 'voterAllBookmarksStatusRetrieve',
        'api_introduction':
            "A list of the office, candidate, or measure bookmark status for this voter.",
        'try_now_link': 'apis_v1:voterAllBookmarksStatusRetrieveView',
        'try_now_link_variables_dict': try_now_link_variables_dict,
        'url_root': url_root,
        'get_or_post': 'GET',
        'required_query_parameter_list': required_query_parameter_list,
        'optional_query_parameter_list': optional_query_parameter_list,
        'api_response': api_response,
        'api_response_notes':
            "",
        'potential_status_codes_list': potential_status_codes_list,
    }
    return template_values
