from requests import get, post
from requests.structures import CaseInsensitiveDict
from requests.utils import dict_from_cookiejar
from browser_cookie3 import chrome as bc3chrome

#indie_script
#could use something faster than requests, but i am too lazy and there is not much of a difference from previous analysis.
#limited to liking a max of 200 posts/hour due to api limitation

__author__ = "GuruPrasaath Manirajan"

class InstaLikerObject:
	def __init__(self, IG_Username):
		
		self.IGU = str(IG_Username)
		self.IDArr = []
		self.cookies = bc3chrome(domain_name='.instagram.com')

		headers = CaseInsensitiveDict()
		headers["user-agent"] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"

		openedcookies = dict_from_cookiejar(self.cookies)
		headers["x-csrftoken"] = openedcookies['csrftoken']

		self.headers = headers

	def InstaGet(self, url, cookies=True, returntype=0):	
		if cookies:
			cookies = self.cookies
		else:
			cookies = None
		ReqObj = get(url, headers=self.headers, cookies=cookies)
		if returntype==2:
			return ReqObj.status_code
		elif returntype==1:
			return ReqObj.json()
		else:
			return ReqObj.content

	def InstaPost(self, url, cookies=True, returntype=0):
		if cookies:
			cookies = self.cookies
		else:
			cookies = None
		ReqObj = post(url, headers=self.headers, cookies=cookies)
		if returntype==2:
			return ReqObj.status_code
		elif returntype==1:
			return ReqObj.json()
		else:
			return ReqObj.content

	def GetID(self, id):
		defapiurl = f'https://www.instagram.com/{id}/?__a=1'
		print((self.InstaGet(defapiurl, returntype=1))["graphql"]["user"]["id"])
		return str((self.InstaGet(defapiurl, returntype=1))["graphql"]["user"]["id"])

	def LikeIterate(self):
		for post in self.IDArr:
			print(post)
			apiurl = f'https://www.instagram.com/web/likes/{post}/like/'
			print(self.InstaPost(apiurl, returntype=2))

	def APICallIteration(self, end_cursor=""):
		defapiurl ='https://www.instagram.com/graphql/query/?query_hash=ea4baf885b60cbf664b34ee760397549&variables={"id":"' + self.GetID(self.IGU) + '","first":50, "after":"' + end_cursor + '"}'
		ThisDictOBJ = self.InstaGet(defapiurl, returntype=1)
		NextPage_Cond = ThisDictOBJ["data"]["user"]["edge_owner_to_timeline_media"]["page_info"]["has_next_page"]
		ThisEndCursor = ThisDictOBJ["data"]["user"]["edge_owner_to_timeline_media"]["page_info"]["end_cursor"]
		self.IndividualIteration(ThisDictOBJ, ThisEndCursor, NextPage_Cond)

	def IndividualIteration(self, DictObj, EndCursor, NextPageCond):
		EdgeArray = DictObj["data"]["user"]["edge_owner_to_timeline_media"]["edges"]
		for EdgeElement in EdgeArray:
			(self.IDArr).append(EdgeElement["node"]["id"])
		else:
			if NextPageCond:
				self.APICallIteration(end_cursor=EndCursor)
			else:
				self.LikeIterate()

ILO = InstaLikerObject('oorga.iruka')
ILO.APICallIteration()