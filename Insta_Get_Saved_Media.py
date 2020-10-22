from browser_cookie3 import chrome as bc3chrome
import requests
from json import dump

__author__ = "GuruPrasaath Manirajan"

class InstagramDL:
	def __init__(self, folderpath=".//Saved_From_Instagram//", savetojson=True, GraphImage=True, GraphVideo=True):
		self.folderpath = ".//Saved_From_Instagram//"
		self.JsonFileCond = savetojson
		self.ImageReq = GraphImage
		self.VideoReq = GraphVideo
		self.src_dataset = {"GraphImage":[],"GraphVideo":[]}
		self.headers = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36",
						"Accept-Encoding":"gzip, deflate",
						"Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
						"DNT":"1",
						"Connection":"close",
						"Upgrade-Insecure-Requests":"1"}
		self.cookies = bc3chrome(domain_name='.instagram.com')
		self.AbsoluteCount = 0

	def ObjectRequest(self, rgeturl):
		try:
			OBJREQ = requests.get(rgeturl, verify=True, headers=self.headers, cookies=self.cookies, timeout=16)
			ResponseObject = OBJREQ.json()
			return ResponseObject
		except (ConnectionError, ReadTimeoutError) as e:
			self.ObjectRequest(rgeturl)

	def MediaResponse(self, EdgeDataArray):
		if EdgeDataArray[0]=="GraphImage":
			self.AbsoluteCount+=1
			print(self.AbsoluteCount)
			self.src_dataset["GraphImage"].append(EdgeDataArray[1])
		else:
			postapi = "https://www.instagram.com/p/{}/?__a=1".format(EdgeDataArray[2])
			AltDict = (self.ObjectRequest(postapi))["graphql"]["shortcode_media"]
			if EdgeDataArray[0]=="GraphSidecar":
				for EdgeNode in AltDict["edge_sidecar_to_children"]["edges"]:
					self.AbsoluteCount+=1
					print(self.AbsoluteCount)
					self.src_dataset[EdgeNode["node"]["__typename"]].append(EdgeNode["node"]["display_url"])
			else:
				self.AbsoluteCount+=1
				print(self.AbsoluteCount)
				self.src_dataset["GraphVideo"].append(AltDict["video_url"])

	def APICallIteration(self, end_cursor=""):
		defapiurl ='https://www.instagram.com/graphql/query/?query_hash=2ce1d673055b99250e93b6f88f878fde&variables={"id":"","first":50, "after":"'+end_cursor+'"}'
		ThisDictOBJ = self.ObjectRequest(defapiurl)
		NextPage_Cond = ThisDictOBJ["data"]["user"]["edge_saved_media"]["page_info"]["has_next_page"]
		ThisEndCursor = ThisDictOBJ["data"]["user"]["edge_saved_media"]["page_info"]["end_cursor"]
		self.IndividualIteration(ThisDictOBJ, ThisEndCursor, NextPage_Cond)

	def IndividualIteration(self, DictObj, EndCursor, NextPageCond):
		EdgeArray = DictObj["data"]["user"]["edge_saved_media"]["edges"]
		for EdgeElement in EdgeArray:
			self.MediaResponse([EdgeElement["node"]["__typename"], EdgeElement["node"]["display_url"], EdgeElement["node"]["shortcode"]])
		if NextPageCond:
			self.APICallIteration(end_cursor=EndCursor)
		else:
			#self.DownloadSavedMedia()
			if self.JsonFileCond:
				self.JsonHandle()
			else:
				pass

	def JsonHandle(self):
		with open('InstagramSaved_JSON.json', 'w+') as ISJ:
			dump(self.src_dataset, ISJ, indent=2)

	def DownloadSavedMedia(self):
		for EdgeUrl in self.src_dataset["GraphImage"]:
			open(self.folderpath+"Images//img"+str(self.src_dataset["GraphImage"].index(EdgeUrl))+".jpg", 'wb+').write(requests.get(EdgeUrl, allow_redirects=True, timeout=16).content)
		for EdgeUrl in self.src_dataset["GraphVideo"]:
			open(self.folderpath+"Videos//vid"+str(self.src_dataset["GraphVideo"].index(EdgeUrl))+".mp4", 'wb+').write(requests.get(EdgeUrl, allow_redirects=True, timeout=16).content)

def InstaSave(folderpath=".//Saved_From_Instagram//", savetojson=True, GraphImage=True, GraphVideo=True):
	InstaSaveClsOBJ=InstagramDL(folderpath, savetojson, GraphImage, GraphVideo)
	InstaSaveClsOBJ.APICallIteration()

InstaSave()