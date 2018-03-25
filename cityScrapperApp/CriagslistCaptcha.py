__author__ = 'eMaM'

import requests
from time import sleep, time


class CriaglistCaptchResolver():
    def CriaglistCaptchResolver(self, site_key, page):
        start_time = time()
        self.KEY = '722255fb8fed3c74efd8a3f36063f6ea'
        self.GOOGLE_KEY = site_key
        self.PAGE = page
        # send credentials to the service to solve captcha
        # returns service's captcha_id of captcha to be solved
        url = "http://2captcha.com/in.php?key={SERVICE_KEY}&method=userrecaptcha&googlekey={googlekey}&pageurl={pageurl}".format(
            SERVICE_KEY=self.KEY, googlekey=self.GOOGLE_KEY, pageurl=self.PAGE)
        resp = requests.get(url)
        if resp.text[0:2] != 'OK':
            quit('Error. Captcha is not received')
        captcha_id = resp.text[3:]

        # fetch ready 'g-recaptcha-response' token for captcha_id
        fetch_url = "http://2captcha.com/res.php?key=" + self.KEY + "&action=get&id=" + captcha_id
        for i in range(1, 20):
            sleep(5)  # wait 5 sec.
            resp = requests.get(fetch_url)
            if resp.text[0:2] == 'OK':
                break

        print('Time to solve: ', time() - start_time)

        # final submitting of form (POST) with 'g-recaptcha-response' token
        submit_url = page
        # spoof user agent
        headers = {'user-agent': 'Mozilla/5.0 Chrome/52.0.2743.116 Safari/537.36'}
        # POST parameters, might be more, depending on form content
        payload = {'submit': 'submit', 'g-recaptcha-response': resp.text[3:]}
        resp = requests.post(submit_url, headers=headers, data=payload)
        if resp.status_code == 200:
            return resp.text
        return None
