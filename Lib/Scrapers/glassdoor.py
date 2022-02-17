# Bu araç @keyiflerolsun tarafından | @KekikAkademi için yazılmıştır.

from requests import Session
from urllib.parse import urlencode, unquote
from datetime import datetime, timedelta
from time import mktime
import hashlib, hmac, base64

from Lib.dosya_indir import dosya_indir
from KekikTaban import slugify

import json
with open("SETTINGS.json", "r+") as dosya:
    glassdoor_ulkeler = json.load(dosya)["GlassDoor_Countries"]

class VeriYok(Exception):
    """Şirket Bulunamadı"""

class GlassDoor:
    def __init__(self, sirket:str, proxi=None):
        self.sirket = sirket

        self.oturum = Session()
        self.oturum.headers.update({"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36"})

        if proxi:
            proxi_part = proxi.split(":")
            if len(proxi_part) == 4:
                p_ip, p_port, p_user, p_pass = proxi_part
                proxi = {
                    'http'  : f'http://{p_user}:{p_pass}@{p_ip}:{p_port}',
                    'https' : f'http://{p_user}:{p_pass}@{p_ip}:{p_port}',
                }
            elif len(proxi_part) == 2:
                p_ip, p_port = proxi_part
                proxi = {
                    'http'  : f'http://{p_ip}:{p_port}',
                    'https' : f'http://{p_ip}:{p_port}',
                }
            self.oturum.proxies.update(proxi)

        self.glassdoor_api = "https://api.glassdoor.com"

        while True:
            self.sign = self._gen_signature(self._20h_later_epox_time) # 1643903208000

            sirket_payload = {
                "action"            : "employers",
                "pageNumber"        : "1",
                "includeReviewText" : "true",
                "t.k"               : "fz6JLNgLgVs",
                "appVersion"        : "8.31.2",
                "responseType"      : "json",
                "s.expires"         : self.sign["epoch"],
                "signature"         : self.sign["signature"],
                "t.p"               : "16",
                "locale"            : "en_EN",
                "q"                 : self.sirket
            }
            sirket_istek = self.oturum.get(f"{self.glassdoor_api}/api-internal/api.htm?{self._payload(sirket_payload)}")
            sirket_json  = sirket_istek.json()
            if sirket_json["status"] == 'Access-Denied':
                continue
            elif sirket_json["status"] == 'Internal error':
                raise VeriYok("Şirket Bulunamadı")
            else:
                break

        self.sirket_veri = sirket_json["response"]["employers"][0]
        self.sirket_id   = self.sirket_veri["id"]

    @property
    def _20h_later_epox_time(self):
        after_20h = datetime.now() + timedelta(days=3)
        # return after_20h.strftime('%s')                   # ? python
        return int(mktime(after_20h.timetuple()) * 1000)    # ! javascript

    def _make_digest(self, message, key):
        key      = bytes(key, "UTF-8")
        message  = bytes(message, "UTF-8")
        digester = hmac.new(key, message, hashlib.sha1)
        # signature1 = digester.hexdigest()
        signature1 = digester.digest()
        # print(signature1)
        # signature2 = base64.urlsafe_b64encode(bytes(signature1, 'UTF-8'))
        signature2 = base64.urlsafe_b64encode(signature1)
        # print(signature2)

        return str(signature2, "UTF-8")

    def _gen_signature(self, epoch):
        data   = f"fz6JLNgLgVs|{epoch}"
        result = self._make_digest(data, "POkHINbj8hnKU87gjJNFDukljGKNkhvyopqaGkqC")
        return {"epoch": epoch, "signature": result}

    def _payload(self, data:dict):
        return unquote(urlencode(data))

    @property
    def _graph_payload(self):
        return self._payload({
            "action"       : "graph",
            "version"      : "1",
            "responseType" : "json",
            "appVersion"   : "8.31.2",
            "signature"    : self.sign["signature"],
            "s.expires"    : self.sign["epoch"],
            "t.p"          : "16",
            "t.k"          : "fz6JLNgLgVs",
            "locale"       : "en_US",
        })

    @property
    def graph_overview(self):
        overview_headers = {
            "x-apollo-operation-name"       : "EmployerOverviewNative",
            "x-apollo-cache-fetch-strategy" : "NETWORK_ONLY",
            "apollographql-client-name"     : "android",
            "apollographql-client-version"  : "8.31.2",
            "User-Agent"                    : "Mozilla/5.0 (Linux; Android 6.0; Google Nexus 4_1 Build/MRA58K; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/74.0.3729.186 Mobile Safari/537.36 GDDroid/8.31.2",
            "Content-Type"                  : "application/json",
        }

        overview_data = {
            "operationName" : "EmployerOverviewNative",
            "variables"     : {
                "employerId"        : self.sirket_id,
                "divisionProfileId" : 0,
                "sgocId"            : 1
            },
            "query" : "query EmployerOverviewNative($employerId: Int!, $divisionProfileId: Int!, $sgocId: Int) { employer(id: $employerId) { __typename id shortName website type revenue headquarters size squareLogoUrl(size: SMALL) coverPhoto { __typename hiResUrl } counts { __typename jobCount salaryCount reviewCount benefitCount interviewCount } subsidiaries { __typename employer { __typename id name headquarters squareLogoUrl ratings { __typename overallRating } counts { __typename jobCount salaryCount reviewCount } } } parent { __typename employer { __typename id name headquarters squareLogoUrl ratings { __typename overallRating } counts { __typename jobCount salaryCount reviewCount } subsidiaries { __typename employer { __typename id name headquarters squareLogoUrl ratings { __typename overallRating } counts { __typename jobCount salaryCount reviewCount } } } } } competitors { __typename shortName } primaryIndustry { __typename industryId industryName } yearFounded overview { __typename description mission } links { __typename manageoLinkData { __typename url urlText employerSpecificText } reviewsUrl interviewUrl } employerManagedContent(parameters: [{employerId: $employerId, divisionProfileId: $divisionProfileId}]) { __typename managedContent { __typename id body media { __typename caption source mediaType } type title } } awards(limit: 200, onlyFeatured: false) { __typename awardDetails name source year } divisions { __typename employer { __typename squareLogoUrl } profileId name isFeatured(sgocId: $sgocId) isVisible counts { __typename jobCount reviewCount } ratings { __typename overallRating } overview { __typename description mission } links { __typename overviewUrl } } } employerReviews(employer: {id: $employerId}, applyDefaultCriteria: true, division: {id: $divisionProfileId}, page: {num: 1, size: 1}) { __typename allReviewsCount ratings { __typename ceoRating ceoRatingsCount businessOutlookRating compensationAndBenefitsRating cultureAndValuesRating careerOpportunitiesRating overallRating recommendToFriendRating seniorManagementRating workLifeBalanceRating reviewCount diversityAndInclusionRating diversityAndInclusionRatingCount ratedCeo { __typename id name title regularPhoto: photoUrl(size: REGULAR) largePhoto: photoUrl(size: LARGE) currentBestCeoAward { __typename displayName timePeriod } } } reviews { __typename reviewId employer { __typename squareLogoUrl links { __typename reviewsUrl } } featured countHelpful countNotHelpful pros cons advice ratingBusinessOutlook ratingCeo ratingRecommendToFriend ratingOverall ratingCultureAndValues ratingDiversityAndInclusion ratingCareerOpportunities ratingCompensationAndBenefits ratingSeniorLeadership ratingWorkLifeBalance summary links { __typename reviewDetailUrl } jobTitle { __typename text } location { __typename name } reviewDateTime lengthOfEmployment isCurrentJob employmentStatus } } employerInterviews(employer: {id: $employerId}, page: {num: 1, size: 1}) { __typename totalInterviewCount interviewExperienceCounts { __typename type count } interviewObtainedChannelCounts { __typename type count } interviewExperienceSum difficultySubmissionCount difficultySum newestReviewDate interviewQuestionCount overallDurationDaysSum overallDurationDaysCount content: interviews { __typename id countHelpful featured countNotHelpful currentJobFlag difficulty durationDays experience interviewDateTime jobTitle { __typename text } location { __typename name } outcome processDescription reviewDateTime source userQuestions { __typename answers { __typename id answer countHelpful countNotHelpful userHandle contributionDate approvalStatus } answerCount id question url } declinedReason negotiationDescription otherSteps } } }",
        }
        overview_istek = self.oturum.post(f"{self.glassdoor_api}/api-internal/api-internal/api.htm?{self._graph_payload}", headers=overview_headers, json=overview_data)
        return overview_istek.json()

    def _get_rating_by_country(self, ulke_kodu):
        graph_headers = {
            "x-apollo-operation-name"       : "EmployerSalariesNative",
            "x-apollo-cache-fetch-strategy" : "NETWORK_ONLY",
            "apollographql-client-name"     : "android",
            "apollographql-client-version"  : "8.31.2",
            "User-Agent"                    : "Mozilla/5.0 (Linux; Android 6.0; Google Nexus 4_1 Build/MRA58K; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/74.0.3729.186 Mobile Safari/537.36 GDDroid/8.31.2",
            "Content-Type"                  : "application/json"
        }
        rating_data = {
            "operationName" : "EmployerReviewsNative",
            "variables"     : {
                "onlyCurrentEmployees"  : False,
                "employerId"            : self.sirket_id,
                "location"              : {"countryId": glassdoor_ulkeler[ulke_kodu]},
                "employmentStatuses"    : [],
                "pageNum"               : 2,
                "pageSize"              : 30,
                "sort"                  : "RELEVANCE",
                "fetchHighlights"       : True,
                "context"               : {
                    "domain"        : "glassdoor.com",
                    "userId"        : 0,
                    "intent"        : "EMPLOYER_SALARIES",
                    "viewType"      : "NATIVE",
                    "deviceType"    : "HANDHELD",
                    "platformType"  : "ANDROID",
                },
            },
            "query": 'query EmployerReviewsNative($onlyCurrentEmployees: Boolean, $employerId: Int, $jobTitle: JobTitleIdent, $location: LocationIdent, $employmentStatuses: [EmploymentStatusEnum], $goc: GOCIdent, $highlight: HighlightTerm, $pageNum: Int!, $pageSize: Int!, $sort: ReviewsSortOrderEnum, $fetchHighlights: Boolean!, $applyDefaultCriteria: Boolean, $worldwideFilter: Boolean, $language: String, $divisionId: DivisionIdent, $preferredTldId: Int, $isRowProfileEnabled: Boolean, $context: Context = {}) { employerReviews(onlyCurrentEmployees: $onlyCurrentEmployees, employer: {id: $employerId}, jobTitle: $jobTitle, location: $location, goc: $goc, employmentStatuses: $employmentStatuses, highlight: $highlight, sort: $sort, page: {num: $pageNum, size: $pageSize}, applyDefaultCriteria: $applyDefaultCriteria, worldwideFilter: $worldwideFilter, language: $language, division: $divisionId, preferredTldId: $preferredTldId, isRowProfileEnabled: $isRowProfileEnabled, multiLanguageEnabledOverride: "true", context: $context) { __typename filteredReviewsCountByLang { __typename count isoLanguage } employer { __typename id shortName squareLogoUrl(size: LARGE) links { __typename reviewsUrl } } queryLocation { __typename id type shortName longName } queryJobTitle { __typename id text } currentPage numberOfPages lastReviewDateTime allReviewsCount ratedReviewsCount filteredReviewsCount ratings { __typename overallRating reviewCount ceoRating recommendToFriendRating cultureAndValuesRating careerOpportunitiesRating workLifeBalanceRating seniorManagementRating compensationAndBenefitsRating businessOutlookRating diversityAndInclusionRating ceoRatingsCount ratedCeo { __typename id name title largePhoto: photoUrl(size: LARGE) currentBestCeoAward { __typename displayName timePeriod } } } reviews { __typename isLegal reviewId reviewDateTime ratingOverall ratingCeo ratingBusinessOutlook ratingWorkLifeBalance ratingCultureAndValues ratingSeniorLeadership ratingRecommendToFriend ratingCareerOpportunities ratingCompensationAndBenefits ratingDiversityAndInclusion isCurrentJob lengthOfEmployment employmentStatus jobEndingYear jobTitle { __typename id text } location { __typename id type name } originalLanguageId pros prosOriginal cons consOriginal summary summaryOriginal advice adviceOriginal isLanguageMismatch countHelpful countNotHelpful employerResponses { __typename id response userJobTitle responseDateTime(format: ISO) countHelpful countNotHelpful } featured divisionName topLevelDomainId languageId translationMethod } } reviewHighlights(employer: {id: $employerId}, context: $context, language: $language) @include(if: $fetchHighlights) { __typename pros { __typename id reviewCount topPhrase keyword links { __typename highlightPhraseUrl } } cons { __typename id reviewCount topPhrase keyword links { __typename highlightPhraseUrl } } } }',
        }

        rating_istek = self.oturum.post(f"{self.glassdoor_api}/api-internal/api-internal/api.htm?{self._graph_payload}", headers=graph_headers, json=rating_data)
        rating_json  = rating_istek.json()
        rating_veri  = rating_json["data"]["employerReviews"]

        return {
            # "country"                   : str(rating_veri["queryLocation"]["longName"]),
            "country"            : ulke_kodu,
            "overall_rating"     : str(rating_veri["ratings"]["overallRating"]),
            "rating_by_category" : {
                "work_life_balance"         : str(rating_veri["ratings"]["workLifeBalanceRating"]),
                "compensation_and_benefits" : str(rating_veri["ratings"]["compensationAndBenefitsRating"]),
                "career_opportunites"       : str(rating_veri["ratings"]["careerOpportunitiesRating"]),
                "senior_management"         : str(rating_veri["ratings"]["seniorManagementRating"]),
                "culture_and_values"        : str(rating_veri["ratings"]["cultureAndValuesRating"]),
                "diversity_and_inclusion"   : str(rating_veri["ratings"]["diversityAndInclusionRating"])
            }
        }

    @property
    def rating_by_countries_data(self):
        veri = {
            "overall_rating_by_countries"     : {},
            "rating_by_category_by_countries" : {}
        }

        for ulke in glassdoor_ulkeler:
            ulke_veri = self._get_rating_by_country(ulke)
            veri["overall_rating_by_countries"][ulke_veri["country"]]     = ulke_veri["overall_rating"]
            veri["rating_by_category_by_countries"][ulke_veri["country"]] = ulke_veri["rating_by_category"]

        return veri

    def _get_salary_by_country(self, ulke_kodu):
        graph_headers = {
            "x-apollo-operation-name"      : "EmployerSalariesNative",
            "x-apollo-cache-fetch-strategy": "NETWORK_ONLY",
            "apollographql-client-name"    : "android",
            "apollographql-client-version" : "8.31.2",
            "User-Agent"                   : "Mozilla/5.0 (Linux; Android 6.0; Google Nexus 4_1 Build/MRA58K; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/74.0.3729.186 Mobile Safari/537.36 GDDroid/8.31.2",
            "Content-Type"                 : "application/json",
        }
        salaries_data = {
            "operationName" : "EmployerSalariesNative",
            "query"         : "query EmployerSalariesNative($employerId: Int!, $location: LocationIdent, $jobTitle: String!, $pageNum: Int!, $pageSize: Int!, $sortType: SalariesSortOrderEnum, $employmentStatuses: [SalariesEmploymentStatusEnum], $context: Context = {}) { salariesByEmployer(employer: {id: $employerId}, location: $location, jobTitle: {text: $jobTitle}, page: {num: $pageNum, size: $pageSize}, sort: $sortType, employmentStatuses: $employmentStatuses, context: $context) { __typename salaryCount pages mostRecent jobTitleCount lashedJobTitle { __typename text id } queryLocation { __typename id type name } results { __typename currency { __typename code id symbol } employer { __typename id shortName squareLogoUrl } jobTitle { __typename id text } obscuring payPeriod count employerTotalCount salariesEmploymentStatus minBasePay meanBasePay maxBasePay medianBasePay links { __typename employerSalariesByCompanyLogoUrl } } } }",
            "variables"     : {
                "context" : {
                    "deviceType"   : "HANDHELD",
                    "domain"       : "glassdoor.com",
                    "intent"       : "EMPLOYER_SALARIES",
                    "platformType" : "ANDROID",
                    "userId"       : 0,
                    "viewType"     : "NATIVE"
                },
                "employerId"        : self.sirket_id,
                "employmentStatuses": [],
                "jobTitle"          : "",
                "location"          : {"countryId": glassdoor_ulkeler[ulke_kodu]},
                "pageNum"           : 1,
                "pageSize"          : 5000,
                "sortType"          : "COUNT",
            },
        }

        salaries_istek = self.oturum.post(f"{self.glassdoor_api}/api-internal/api-internal/api.htm?{self._graph_payload}", headers=graph_headers, json=salaries_data)
        salaries_json  = salaries_istek.json()
        salaries_veri  = salaries_json["data"]["salariesByEmployer"]["results"]

        return {
            "country"  : ulke_kodu,
            "salaries" : {
                veri["jobTitle"]["text"] : f"{veri['meanBasePay']} {veri['currency']['code']} {veri['payPeriod'].title()}"
                    # for veri in salaries_veri
                    for veri in salaries_veri if veri['payPeriod'].title() == 'Annual' and veri['currency']['code'] == 'USD'
            }
        }

    @property
    def salaries_by_countries_data(self):
        veri = {}
        for ulke in glassdoor_ulkeler:
            ulke_veri = self._get_salary_by_country(ulke)
            veri[ulke_veri['country']] = ulke_veri['salaries']

        return veri

    def data_ver(self):
        # resim_yolu = dosya_indir(self.sirket_veri["squareLogo"], slugify(self.sirket_veri['name']))
        veri = {
            "company_name"                 : self.sirket_veri["name"],
            # "logo"                         : f"/static/images/{resim_yolu}" if resim_yolu else None,
            "logo"                         : self.sirket_veri["squareLogo"],
            "founded"                      : str(self.graph_overview["data"]["employer"]["yearFounded"]),
            "industry"                     : self.sirket_veri["industry"],
            "website"                      : self.sirket_veri["website"],
            "overall_rating_worldwide"     : self.sirket_veri["overallRating"],
            "rating_by_category_worldwide" : {
                "work_life_balance"         : str(self.sirket_veri["workLifeBalanceRating"]),
                "compensation_and_benefits" : str(self.sirket_veri["compensationAndBenefitsRating"]),
                "career_opportunites"       : str(self.sirket_veri["careerOpportunitiesRating"]),
                "senior_management"         : str(self.sirket_veri["seniorLeadershipRating"]),
                "culture_and_values"        : str(self.sirket_veri["cultureAndValuesRating"]),
                "diversity_and_inclusion"   : str(self.sirket_veri["diversityAndInclusionRating"]),
            }
        }
        veri.update(self.rating_by_countries_data)
        veri["salary_by_countries"] = self.salaries_by_countries_data

        return veri

def glassdoor_ver(sirket, proxi=None):
    gl = GlassDoor(sirket, proxi)
    return gl.data_ver()