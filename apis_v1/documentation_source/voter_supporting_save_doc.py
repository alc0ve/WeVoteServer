# apis_v1/documentation_source/voter_supporting_save_doc.py
# Brought to you by We Vote. Be good.
# -*- coding: UTF-8 -*-


def voter_supporting_save_doc_template_values(url_root):
    """
    Show documentation about voterSupportingSave
    """
    required_query_parameter_list = [
        {
            'name':         'api_key',
            'value':        'string (from post, cookie, or get (in that order))',  # boolean, integer, long, string
            'description':  'The unique key provided to any organization using the WeVoteServer APIs',
        },
        {
            'name':         'voter_device_id',
            'value':        'string',  # boolean, integer, long, string
            'description':  'An 88 character unique identifier linked to a voter record on the server',
        },
        {
            'name':         'kind_of_ballot_item',
            'value':        'string',  # boolean, integer, long, string
            'description':  'The kind of ballot item the voter is supporting. '
                            '(kind_of_ballot_item is either "CANDIDATE", "POLITICIAN" or "MEASURE")',
        },
        {
            'name':         'ballot_item_id',
            'value':        'integer',  # boolean, integer, long, string
            'description':  'The unique internal identifier of the ballot item the voter is supporting. '
                            '(either ballot_item_id OR ballot_item_we_vote_id required -- not both. '
                            'If it exists, ballot_item_id is used instead of ballot_item_we_vote_id)',
        },
        {
            'name':         'ballot_item_we_vote_id',
            'value':        'string',  # boolean, integer, long, string
            'description':  'The unique identifier for this ballot_item across all networks '
                            '(either ballot_item_id OR ballot_item_we_vote_id required -- not both. '
                            'NOTE: In the future we might support other identifiers used in the industry.',
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
            'description':  'Cannot proceed. Missing voter_id while trying to save.',
        },
        {
            'code':         'UNABLE_TO_SAVE-CANDIDATE_ID_AND_MEASURE_ID_MISSING',
            'description':  'Cannot proceed. Neither candidate_id nor measure_id were included.',
        },
        {
            'code':         'SUPPORTING_CANDIDATE STANCE_UPDATED',
            'description':  'Success. Existing entry updated.',
        },
        {
            'code':         'SUPPORTING_CANDIDATE NEW_STANCE_SAVED',
            'description':  'Success. New entry created.',
        },
        {
            'code':         'SUPPORTING_CANDIDATE STANCE_COULD_NOT_BE_UPDATED',
            'description':  'Cannot proceed. Existing entry could not be updated.',
        },
        {
            'code':         'SUPPORTING_CANDIDATE NEW_STANCE_COULD_NOT_BE_SAVED',
            'description':  'Cannot proceed. New entry could not be created.',
        },
        {
            'code':         'SUPPORTING_MEASURE STANCE_UPDATED',
            'description':  'Success. Existing entry updated.',
        },
        {
            'code':         'SUPPORTING_MEASURE NEW_STANCE_SAVED',
            'description':  'Success. New entry created.',
        },
        {
            'code':         'SUPPORTING_MEASURE STANCE_COULD_NOT_BE_UPDATED',
            'description':  'Cannot proceed. Existing entry could not be updated.',
        },
        {
            'code':         'SUPPORTING_MEASURE NEW_STANCE_COULD_NOT_BE_SAVED',
            'description':  'Cannot proceed. New entry could not be created.',
        },
    ]

    try_now_link_variables_dict = {
        'kind_of_ballot_item': 'CANDIDATE',
        'ballot_item_id': '5655',
    }

    api_response = '{\n' \
                   '  "status": string (description of what happened),\n' \
                   '  "success": boolean (did the save happen?),\n' \
                   '  "ballot_item_id": integer,\n' \
                   '  "ballot_item_we_vote_id": string,\n' \
                   '  "kind_of_ballot_item": string (CANDIDATE, MEASURE),\n' \
                   '}'

    template_values = {
        'api_name': 'voterSupportingSave',
        'api_slug': 'voterSupportingSave',
        'api_introduction':
            "Save or create support stance for the current voter for either a measure or candidate.",
        'try_now_link': 'apis_v1:voterSupportingSaveView',
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
