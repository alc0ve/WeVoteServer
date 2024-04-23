import os
import json
from locust import HttpUser, TaskSet, task


class WeVoteTasks(TaskSet):

    def on_start(self):
        """
        read voter_device_id from a property file (./loadtest/test_variables.json) if exists
        otherwise generate a new one via the API
        """
        try:
            # print("voter_device_id = %s" % self.voter_device_id)
            with open(os.path.join(os.path.dirname(__file__), "test_variables.json")) as f:
                self.voter_device_id = json.loads(f.read())["voter_device_id"]
        except Exception as e:
            print("Cant find test_variables.json, generating new voter_device_id")
            response = self.client.get("/apis/v1/deviceIdGenerate/")
            self.voter_device_id = response.json()["voter_device_id"]

        try:
            # print("voter_device_id = %s" % self.voter_device_id)
            with open(os.path.join(os.path.dirname(__file__), "test_variables.json")) as f:
                self.google_civic_election_id = json.loads(f.read())["google_civic_election_id"]
        except Exception as e:
            print("Cant find test_variables.json, setting google_civic_election_id to 0")
            self.google_civic_election_id = 0

    @task(1)
    def homepage(self):
        voter_device_id = self.voter_device_id
        google_civic_election_id = self.google_civic_election_id
        response = self.client.get("/apis/v1/voterAllBookmarksStatusRetrieve/?voter_device_id={voter_device_id}"
                                   "".format(voter_device_id=voter_device_id), name="voterAllBookmarksStatusRetrieve")
        response = self.client.get("/apis/v1/voterRetrieve/?voter_device_id={voter_device_id}"
                                   "".format(voter_device_id=voter_device_id), name="voterRetrieve")
        response = self.client.get("/apis/v1/voterAddressRetrieve/?voter_device_id={voter_device_id}"
                                   "".format(voter_device_id=voter_device_id), name="voterAddressRetrieve")
        response = self.client.get("/apis/v1/searchAll/?voter_device_id={voter_device_id}"
                                   "".format(voter_device_id=voter_device_id), name="searchAll")
        response = self.client.get("/apis/v1/voterAllPositionsRetrieve/?voter_device_id={voter_device_id}"
                                   "".format(voter_device_id=voter_device_id), name="voterAllPositionsRetrieve")
        response = self.client.get("/apis/v1/voterGuidesToFollowRetrieve/?voter_device_id={voter_device_id}"
                                   "&google_civic_election_id={google_civic_election_id}"
                                   "&maximum_number_to_retrieve=350&search_string="
                                   "".format(google_civic_election_id=google_civic_election_id,
                                             voter_device_id=voter_device_id), name="voterGuidesToFollowRetrieve")
        response = self.client.get("/apis/v1/voterGuidesFollowedRetrieve/?voter_device_id={voter_device_id}"
                                   "".format(voter_device_id=voter_device_id), name="voterGuidesFollowedRetrieve")
        response = self.client.get("/apis/v1/voterBallotItemsRetrieve/?voter_device_id={voter_device_id}"
                                   "&use_test_election=false"
                                   "".format(voter_device_id=voter_device_id), name="voterBallotItemsRetrieve")

    # @task(1)
    # def organizationCount(self):
    #     response = self.client.get("/apis/v1/organizationCount/")
    #     #print "organizationCount:", response.status_code, response.content
    #     pass
    #
    # @task(1)
    # def voterCount(self):
    #     response = self.client.get("/apis/v1/voterCount/")
    #     #print "voterCount:", response.status_code, response.content
    #     pass


class WeVoteLocust(HttpUser):
    tasks = {WeVoteTasks:5}
    min_wait = 500  # 0.5s
    max_wait = 1500
