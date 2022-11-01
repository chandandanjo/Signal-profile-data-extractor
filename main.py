import requests
import json
import re
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor


class SignalExtractor:
    def __init__(self) -> None:
        self.allCategoryLinks = []
        self.allPersonIds = []
        self.allInfoOutputs = []

    def categoryLinkExtractor(self):
        # Step 1
        MAIN_URL = 'https://signal.nfx.com/'
        resp = requests.get(MAIN_URL)
        soup = BeautifulSoup(resp.content, 'lxml')
        seedLinks = [re.match("(top-)(?P<link>.*)(-investors)", i['href'].split('/')[-1])['link'] for i in soup.find('div', {'id':'stage-pre-seed'}).find('ul').find_all('a')]
        preSeedLinks = [re.match("(top-)(?P<link>.*)(-investors)", i['href'].split('/')[-1])['link'] for i in soup.find('div', {'id':'stage-seed'}).find('ul').find_all('a')]
        self.allCategoryLinks.extend(seedLinks)
        self.allCategoryLinks.extend(preSeedLinks)
        print(f'Extracted all category links, total {len(self.allCategoryLinks)} in number.')


    def personIdExtractor(self, link):
        # Step 2
        try:
            nextPage = True
            endCursor = ''
            personIds = []
            while nextPage:
                json_data = {
                    'operationName': 'vclInvestors',
                    'variables': {
                        'slug': f'{link}',
                        'order': [
                            {},
                        ],
                        'after': f'{endCursor}',
                    },
                    'query': 'query vclInvestors($slug: String!, $after: String) {\n  list(slug: $slug) {\n    id\n    slug\n    investor_count\n    vertical {\n      id\n      display_name\n      kind\n      __typename\n    }\n    location {\n      id\n      display_name\n      __typename\n    }\n    stage\n    firms {\n      id\n      name\n      slug\n      __typename\n    }\n    scored_investors(first: 8, after: $after) {\n      pageInfo {\n        hasNextPage\n        hasPreviousPage\n        endCursor\n        __typename\n      }\n      record_count\n      edges {\n        node {\n          ...investorListInvestorProfileFields\n          __typename\n        }\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n}\n\nfragment investorListInvestorProfileFields on InvestorProfile {\n  id\n  person {\n    id\n    first_name\n    last_name\n    name\n    slug\n    is_me\n    is_on_target_list\n    __typename\n  }\n  image_urls\n  position\n  min_investment\n  max_investment\n  target_investment\n  is_preferred_coinvestor\n  firm {\n    id\n    name\n    slug\n    __typename\n  }\n  investment_locations {\n    id\n    display_name\n    location_investor_list {\n      id\n      slug\n      __typename\n    }\n    __typename\n  }\n  investor_lists {\n    id\n    stage_name\n    slug\n    vertical {\n      id\n      display_name\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n',
                }

                response = requests.post('https://signal-api.nfx.com/graphql', json=json_data).json()
                if response["data"]["list"]:
                    nextPage = response["data"]["list"]["scored_investors"]["pageInfo"]["hasNextPage"]
                    if nextPage:
                        endCursor = response["data"]["list"]["scored_investors"]["pageInfo"]["endCursor"]
                    personId = [i["node"]["person"]["slug"] for i in response["data"]["list"]["scored_investors"]["edges"]]
                    personIds.extend(personId)
                else:
                    break
            self.allPersonIds.extend(personIds)
            print(f'Extracted IDs for category : {link}, Total Ids : {len(personIds)}')
        except Exception as e:
            print(f'personIdExtractor : {link}, Error : {e}')


    def personInfoExtractor(self, id):
        # Step 3
        try:
            json_data = {
                'operationName': 'InvestorProfileSignedOutLoad',
                'variables': {
                    'personId': f'{id}',
                    'firstInvestmentsOnRecord': 8,
                    'firstNetworkListInvestorProfiles': 5,
                    'firstInvestingConnections': 3,
                },
                'query': 'query InvestorProfileSignedOutLoad($personId: ID!, $firstInvestmentsOnRecord: Int, $firstNetworkListInvestorProfiles: Int, $firstInvestingConnections: Int) {\n  investor_profile(person_id: $personId) {\n    ...signedOutInvestorProfileFields\n    __typename\n  }\n}\n\nfragment signedOutInvestorProfileFields on InvestorProfile {\n  id\n  person {\n    id\n    slug\n    first_name\n    last_name\n    name\n    linkedin_url\n    facebook_url\n    twitter_url\n    crunchbase_url\n    angellist_url\n    roles\n    url\n    first_degree_count\n    __typename\n  }\n  investor_profile_funding_rounds {\n    record_count\n    __typename\n  }\n  position\n  min_investment\n  max_investment\n  target_investment\n  image_urls\n  areas_of_interest_freeform\n  no_current_interest_freeform\n  vote_count\n  headline\n  previous_position\n  previous_firm\n  location {\n    id\n    display_name\n    __typename\n  }\n  firm {\n    id\n    current_fund_size\n    name\n    slug\n    __typename\n  }\n  degrees {\n    id\n    name\n    field_of_study\n    school {\n      id\n      name\n      display_name\n      total_student_count\n      __typename\n    }\n    __typename\n  }\n  positions {\n    id\n    title\n    company {\n      id\n      name\n      display_name\n      total_employee_count\n      __typename\n    }\n    start_date {\n      month\n      year\n      __typename\n    }\n    end_date {\n      month\n      year\n      __typename\n    }\n    __typename\n  }\n  media_links {\n    id\n    url\n    title\n    image_url\n    __typename\n  }\n  investor_lists {\n    id\n    slug\n    stage_name\n    vertical {\n      id\n      kind\n      display_name\n      __typename\n    }\n    __typename\n  }\n  investments_on_record(first: $firstInvestmentsOnRecord) {\n    pageInfo {\n      hasNextPage\n      __typename\n    }\n    record_count\n    edges {\n      node {\n        id\n        company_display_name\n        total_raised\n        coinvestor_names\n        investor_profile_funding_rounds {\n          id\n          is_lead\n          board_role {\n            id\n            title\n            __typename\n          }\n          funding_round {\n            id\n            stage\n            date\n            amount\n            __typename\n          }\n          __typename\n        }\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n  network_list_investor_profiles(first: $firstNetworkListInvestorProfiles) {\n    list_type\n    edges {\n      node {\n        id\n        image_urls\n        position\n        person {\n          id\n          name\n          first_name\n          last_name\n          slug\n          __typename\n        }\n        firm {\n          id\n          name\n          slug\n          __typename\n        }\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n  network_list_scouts_and_angels_profiles(first: $firstNetworkListInvestorProfiles) {\n    list_type\n    edges {\n      node {\n        id\n        image_urls\n        position\n        person {\n          id\n          name\n          first_name\n          last_name\n          slug\n          __typename\n        }\n        firm {\n          id\n          name\n          slug\n          __typename\n        }\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n  investing_connections(first: $firstInvestingConnections) {\n    record_count\n    edges {\n      node {\n        id\n        target_person {\n          id\n          name\n          slug\n          first_name\n          last_name\n          investor_profile {\n            id\n            image_urls\n            firm {\n              id\n              name\n              slug\n              __typename\n            }\n            __typename\n          }\n          __typename\n        }\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n',
            }

            response = requests.post('https://signal-api.nfx.com/graphql', json=json_data).json()
            linkedin = response["data"]["investor_profile"]["person"]["linkedin_url"]
            facebook = response["data"]["investor_profile"]["person"]["facebook_url"]
            twitter = response["data"]["investor_profile"]["person"]["twitter_url"]
            crunchbase = response["data"]["investor_profile"]["person"]["crunchbase_url"]
            angelList = response["data"]["investor_profile"]["person"]["angellist_url"]
            investorName = response["data"]["investor_profile"]["person"]["name"]
            try:
                firmName = response["data"]["investor_profile"]["firm"]["name"]
            except:
                firmName = None
            firmWebsite = response["data"]["investor_profile"]["person"]["url"]
            title = response["data"]["investor_profile"]["position"].replace('_', ' ')
            sweetSpot = response["data"]["investor_profile"]["target_investment"] + ' $'
            range = f'{response["data"]["investor_profile"]["min_investment"]} - {response["data"]["investor_profile"]["max_investment"]} $'
            try:
                location = response["data"]["investor_profile"]["location"]["display_name"]
            except:
                location = None
            investmentCat = list(set([i["vertical"]["display_name"] for i in response["data"]["investor_profile"]["investor_lists"]]))

            outputDict = {
                'Name' : investorName,
                'Signal Profile' : f'https://signal.nfx.com/investors/{id}',
                'Firm Name' : firmName,
                'Title' : title.title(),
                'Location' : location,
                'Linkedin' : linkedin,
                'Facebook' : facebook,
                'Twitter' : twitter,
                'Crunchbase' : crunchbase,
                'Angel List' : angelList,
                'Firm Website' : firmWebsite,
                'Sweet spot' : sweetSpot,
                'Range' : range,
                'Investment Categories' : investmentCat
            }
            self.allInfoOutputs.append(outputDict)
            print('Extracted profile for : ', investorName)
        except Exception as e:
            print(f'personInfoExtractor : {id}, {str(e)}')

    def main(self):
        self.categoryLinkExtractor()

        with ThreadPoolExecutor(max_workers=5) as executor:
            executor.map(self.personIdExtractor, list(set(self.allCategoryLinks)))

        with open('ids.json', 'w+') as f:
            f.write(json.dumps(self.allPersonIds, indent = 1))

        with ThreadPoolExecutor(max_workers=10) as executor:
            print(f'Total IDs : {len(list(set(self.allPersonIds)))}')
            executor.map(self.personInfoExtractor, list(set(self.allPersonIds)))

        with open('output.json', 'w+') as f:
            f.write(json.dumps(self.allInfoOutputs, indent = 1))

        
if __name__ == '__main__':
    obj = SignalExtractor()
    obj.main()
