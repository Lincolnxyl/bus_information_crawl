import scrapy
import re
import time

CookiesInfo = {
    'RCulture' : 'en-US',
    '_ga' : 'GA1.3.2068322039.1534362152',
    '_gid' : 'GA1.3.1020005923.1534362152',
    'CMSPreferredCulture' : 'en-US',
    'ASP.NET_SessionId' : 'qbskywfe4mwi00zdlefar0dn',
    'CMSCurrentTheme' : 'SAPTCO_En',
    '_gat' : '1'
}

headers = {
    'Accept' : 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'Accept-Encoding' : 'gzip, deflate, br',
    'Cache-Control' : 'max-age=0',
    'Connection' : 'keep-alive',
    'Content-Type' : 'application/x-www-form-urlencoded',
    'Host' : 'www.saptco.com.sa',
    'Upgrade-Insecure-Requests' : '1',
    'Accept-Language' : 'en-US,en;q=0.9',
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36'
}

html_script = r'var arrayResultTrips = \'(.*?)\''
CityList = ['Dammam','Al Qatif','Buraydah','Abha','Hail','Arar','Sakaka','Madinah','Tabuk','Al Ahsa','Riyadh (Azziziya)','Najran','Jazan','Baha','Taif','Makkah (Al Haram)','Jeddah']

def StoreResponse(name, response):
    print("=========================================== Generating {} ====================================".format(name))
    responseURL = response.url
    requestURL = response.request.url
    print('''Response's URL: ''', responseURL)
    print('''Request's  URL: ''', requestURL)
    print('response status',response.status)
    with open(name,'w') as f:
        f.write(response.body.decode("utf-8"))
        f.close()

def dateRange(bgn, end):
    fmt = '%d/%m/%Y'
    bgn = int(time.mktime(time.strptime(bgn,fmt)))
    end = int(time.mktime(time.strptime(end,fmt)))
    return [time.strftime(fmt,time.localtime(i)) for i in range(bgn,end+1,3600*24)]

def ParseResult(self,record_list):
    for one_record in record_list:
        DepartureDate = one_record['DepartureDate']
        DepartureTime = one_record['DepartureTime']
        IsTransitTrip = one_record['IsTransitTrip']
        DepartureStation = one_record['Trips'][0]['DepCityName']
        ArrivalStation = one_record['Trips'][-1]['ArrCityName']
        with open('Record.txt','a') as f:
            f.write('{},{},{},{},{}'.format(DepartureStation, ArrivalStation, DepartureDate, DepartureTime, IsTransitTrip))
            f.close()
        print('{},{},{},{},{}'.format(DepartureStation, ArrivalStation, DepartureDate, DepartureTime, IsTransitTrip))


class SpidyQuotesViewStateSpider(scrapy.Spider):
    name = 'buses'
    # start_urls = ['https://www.saptco.com.sa/TripReservation/Search.aspx']
    download_delay = 20
    # Count = 0
    def start_requests(self):
        self.Count = 0
        reqs = []
        url = 'https://www.saptco.com.sa/TripReservation/Search.aspx'
        req = scrapy.Request(url, headers=headers, cookies = CookiesInfo, meta={'url': url}, dont_filter=True)
        reqs.append(req)
        return reqs

    """
    change the mode into single ride and get response.
    here the response is from previous GET, which should be a page in 200 status
    """
    def parse(self, response):

        StoreResponse('afterGET.html', response)

        yield scrapy.FormRequest(
            'https://www.saptco.com.sa/TripReservation/Search.aspx',
            formdata = {
                'p$lt$ctl01$pageplaceholder1$p$lt$ctl02$pageplaceholder$p$lt$ctl00$logonminiform1$plcUp$loginElem$chkRememberMe' : 'on',
                'p$lt$ctl02$pageplaceholder$p$lt$ctl01$ResSearchUC$RBLType:' : '1',
                'p$lt$ctl02$pageplaceholder$p$lt$ctl01$ResSearchUC$DDAdults' : '1',
                'p$lt$ctl02$pageplaceholder$p$lt$ctl01$ResSearchUC$DDKids' : '0',
                'p$lt$ctl02$pageplaceholder$p$lt$ctl01$ResSearchUC$DDInfant' : '0',
                'p$lt$ctl02$pageplaceholder$p$lt$ctl01$ResSearchUC$IsVipSelected_hf' : '1',
                'manScript_HiddenField' : response.css('input#manScript_HiddenField::attr(value)').extract_first(),
                '__EVENTTARGET' : response.css('input#__EVENTTARGET::attr(value)').extract_first(),
                '__EVENTARGUMENT' : response.css('input#__EVENTARGUMENT::attr(value)').extract_first(),
                '__LASTFOCUS' : response.css('input#__LASTFOCUS::attr(value)').extract_first(),
                '__VIEWSTATE' : response.css('input#__VIEWSTATE::attr(value)').extract_first(),
                'lng' : response.css('input#lng::attr(value)').extract_first(),
                '__VIEWSTATEGENERATOR' : response.css('input#__VIEWSTATEGENERATOR::attr(value)').extract_first(),
                '__SCROLLPOSITIONX' : response.css('input#__SCROLLPOSITIONX::attr(value)').extract_first(),
                '__SCROLLPOSITIONY' : response.css('input#__SCROLLPOSITIONY::attr(value)').extract_first(),
                'VipStanderd_rb' : '1'
            },
            method = 'POST',
            headers = headers,
            cookies = CookiesInfo,
            callback = self.parse_address,
            dont_filter = True
        )

    """
    Input from and to information and get response
    here the response is from previous POST, which is a page with only single ride information
    """
    def parse_address(self, response):

        StoreResponse('afterPOSTSingleRide.html', response)
        FormData = {
            'p$lt$ctl01$pageplaceholder1$p$lt$ctl02$pageplaceholder$p$lt$ctl00$logonminiform1$plcUp$loginElem$chkRememberMe' : 'on',
            'p$lt$ctl02$pageplaceholder$p$lt$ctl01$ResSearchUC$RBLType:' : '1',
            'p$lt$ctl02$pageplaceholder$p$lt$ctl01$ResSearchUC$TxtFrom' : 'Dammam',
            'p$lt$ctl02$pageplaceholder$p$lt$ctl01$ResSearchUC$TxtTo' : 'Buraydah',
            'p$lt$ctl02$pageplaceholder$p$lt$ctl01$ResSearchUC$timePickerDeparture$txtDateTime' : '25/08/2018',
            'p$lt$ctl02$pageplaceholder$p$lt$ctl01$ResSearchUC$DDAdults' : '1',
            'p$lt$ctl02$pageplaceholder$p$lt$ctl01$ResSearchUC$DDKids' : '0',
            'p$lt$ctl02$pageplaceholder$p$lt$ctl01$ResSearchUC$DDInfant' : '0',
            'p$lt$ctl02$pageplaceholder$p$lt$ctl01$ResSearchUC$BtnSearch' : 'Search',
            'p$lt$ctl02$pageplaceholder$p$lt$ctl01$ResSearchUC$IsVipSelected_hf' : '1',
            'manScript_HiddenField' : response.css('input#manScript_HiddenField::attr(value)').extract_first(),
            '__EVENTTARGET' : response.css('input#__EVENTTARGET::attr(value)').extract_first(),
            '__EVENTARGUMENT' : response.css('input#__EVENTARGUMENT::attr(value)').extract_first(),
            '__LASTFOCUS' : response.css('input#__LASTFOCUS::attr(value)').extract_first(),
            '__VIEWSTATE' : response.css('input#__VIEWSTATE::attr(value)').extract_first(),
            'lng' : response.css('input#lng::attr(value)').extract_first(),
            '__VIEWSTATEGENERATOR' : response.css('input#__VIEWSTATEGENERATOR::attr(value)').extract_first(),
            '__SCROLLPOSITIONX' : response.css('input#__SCROLLPOSITIONX::attr(value)').extract_first(),
            '__SCROLLPOSITIONY' : response.css('input#__SCROLLPOSITIONY::attr(value)').extract_first(),
            'VipStanderd_rb' : '1'
        }

        DepartureDateList = dateRange('20/08/2018','30/08/2018')
        DepartureList = CityList
        ArrivalList = CityList

        for Departure in DepartureList:
            for Arrival in ArrivalList:
                if (Departure == Arrival):
                    continue

                FormData['p$lt$ctl02$pageplaceholder$p$lt$ctl01$ResSearchUC$TxtFrom'] = Departure
                FormData['p$lt$ctl02$pageplaceholder$p$lt$ctl01$ResSearchUC$TxtTo'] = Arrival

                for DepartureDate in DepartureDateList:

                    FormData['p$lt$ctl02$pageplaceholder$p$lt$ctl01$ResSearchUC$timePickerDeparture$txtDateTime'] = DepartureDate

                    print('Start crawlling buses from {} to {} at {}'.format(Departure,Arrival,DepartureDate))

                    yield scrapy.FormRequest(
                        'https://www.saptco.com.sa/TripReservation/Search.aspx',
                        formdata = FormData,
                        method = 'POST',
                        headers = headers,
                        cookies = CookiesInfo,
                        callback = self.parse_search,
                        dont_filter = True
                    )

    def parse_search(self, response):

        StoreResponse('Result.html', response)

        content = response.body.decode("utf-8")

        self.Count += 1
        FileName = './Store/' + str(self.Count) + '.html'
        with open(FileName, 'w') as f:
            f.write(content)

        pre_record = re.findall(html_script,content,re.S|re.M)

        if (len(pre_record) == 1):
            record = pre_record[0]
        else:
            with open('Log.txt','a') as f:
                f.write('Wrong: length of pre-record = {}'.format(len(pre_record)))
                f.close()

        new_record = record.replace('false','\'false\'')
        new_record = new_record.replace('true','\'true\'')
        new_record = new_record.replace('null','\'null\'')
        record_list = list(eval(new_record))
        if (len(record_list)>0):
            print("Added {} Records".format(len(record_list)))
            ParseResult(record_list)
        else:
            print("No record was added")
        # elif (response.status == 302):
        #     yield scrapy.Request(
        #         url = response.url,
        #         method = 'GET',
        #         headers = headers,
        #         cookies = CookiesInfo,
        #         callback = self.parse_search
        #     )
        """
        Mark Here
        """
