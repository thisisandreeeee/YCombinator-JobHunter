from bs4 import BeautifulSoup
import requests, csv, time, urllib.parse, pandas as pd, numpy as np
import config

class JobHunter:
	def __init__(self, auth):
		self.auth = auth
		self.YC_URL = "http://yclist.com/"
		self.CRUNCHBASE_URL = "https://api.crunchbase.com/v/3/organizations/"

	def get_yclist(self):
		page = requests.get(self.YC_URL)
		soup = BeautifulSoup(page.text, "html.parser")
		page.close()
		with open('1_yclist.csv','w') as f:
			w = csv.writer(f)
			w.writerow(['company_name','url','description','permalink'])

			list_of_companies = soup.find_all(class_="operating")
			for company in list_of_companies:
				details = company.find_all("td")
				company_name = details[1].get_text()
				url = details[2].find("a").get("href")
				description = details[5].get_text()

				if company_name and url and description:
					w.writerow([company_name,url,description,"null"])
		return pd.read_csv('1_yclist.csv')

	def get_permalinks(self, yclist = None):
		if yclist is None:
			yclist = pd.read_csv('1_yclist.csv')
		with open('2_withpermalink.csv','w') as f:
			w = csv.writer(f)
			w.writerow(['company_name','url','description','permalink','is_done'])
			within_limit = True
			for i in yclist.index:
				company_name, url, description, permalink = yclist['company_name'][i], yclist['url'][i],yclist['description'][i], yclist['permalink'][i]
				if permalink == "null" and within_limit:
					try:
						resp = requests.get(self.CRUNCHBASE_URL + self.auth + "&name=" + urllib.parse.quote_plus(company_name)).json()
						print("Querying " + company_name)
					except:
						within_limit = False
						print("EXIT: RATE LIMIT EXCEEDED")

					try:
						permalink = resp['data']['items'][0]['properties']['permalink']
					except:
						pass
				w.writerow([company_name, url, description, permalink, "no"])
		return pd.read_csv('2_withpermalink.csv')

	def get_company_info(self, companies = None):
		if companies is None:
			companies = pd.read_csv('2_withpermalink.csv')
		with open('3_allinfo.csv','w') as f:
			w = csv.writer(f)
			w.writerow(['company_name','url','description','permalink','since','min_emp','max_emp','funding','founders','num_investors','headquarters','news','is_done'])
			within_limit = True

			for i in companies.index:
				company_name, url, description, permalink, is_done = companies['company_name'][i], companies['url'][i], companies['description'][i], companies['permalink'][i], companies['is_done'][i]
				since,min_emp,max_emp,funding = companies['since'][i],companies['min_emp'][i],companies['max_emp'][i],companies['funding'][i]
				founders,num_investors,headquarters,news = companies['founders'][i], companies['num_investors'][i],companies['headquarters'][i],companies['news'][i]
				if is_done == "no" and within_limit:
					try:
						org_resp = requests.get(CRUNCHBASE + permalink + auth).json()
						print("Querying " + permalink)
					except:
						within_limit = False
						print("EXIT: RATE LIMIT EXCEEDED")

					try:
						data = org_resp['data']
						since,min_emp,max_emp,funding = "",0,0,0
						try:
							since = data['properties']['founded_on']
						except:
							pass
						try:
							min_emp = data['properties']['num_employees_min']
						except:
							pass
						try:
							max_emp = data['properties']['num_employees_max']
						except:
							pass
						try:
							funding = data['properties']['total_funding_usd']
						except:
							pass

						founders,num_investors,headquarters,news = [],0,"",0
						try:
							for founder in data['relationships']['founders']['items']:
								founders.append((founder['properties']['first_name'],founder['properties']['last_name']))
						except:
							pass
						try:
							num_investors = data['relationships']['investors']['paging']['total_items']
						except:
							pass
						try:
							headquarters = data['relationships']['headquarters']['item']['properties']['city']
						except:
							pass
						try:
							news = data['relationships']['news']['paging']['total_items']
						except:
							pass
						is_done = "yes"
					except:
						pass
				w.writerow([company_name,url,description,permalink,since,min_emp,max_emp,funding,founders,num_investors,headquarters,news,is_done])
		return pd.read_csv('3_allinfo.csv')

	def guess_emails(self, companies = None):
		if companies is None:
			companies = pd.read_csv('3_allinfo.csv')
		with open('4_final.csv','w') as f:
			w = csv.writer(f)
			w.writerow(['company_name','url','description','since','minimum_employees','maximum_employees','funding','founders','number_of_investors','headquarters','amount_of_publicity','email1','email2','email3','email4','email5','email6','email7','email8'])

			for i in companies.index:
				res = []
				email_domain = tldextract.extract(companies['url'][i])
				domain_name = email_domain.domain + "." + email_domain.suffix
				res.append(companies['company_name'][i])
				res.append(companies['url'][i])
				res.append(companies['description'][i])
				res.append(companies['since'][i])
				res.append(companies['min_emp'][i])
				res.append(companies['max_emp'][i])
				res.append(companies['funding'][i])
				res.append(companies['founders'][i])
				res.append(companies['num_investors'][i])
				res.append(companies['headquarters'][i])
				res.append(companies['news'][i])
				founders = ast.literal_eval(companies['founders'][i])
				for founder in founders:
					email = founder[0].lower() + "@" + domain_name
					if validate_email(email) and email not in res:
						res.append(email)
				w.writerow(res)
		return pd.read_csv('4_final.csv')

	def send_to(self, recipients, resume_path):
		sender = config.sender
		gmail_password = config.emailpass
		# Create the enclosing (outer) message
		outer = MIMEMultipart()
		outer['Subject'] = 'Hello world'
		outer['To'] = ', '.join(recipients)
		outer['From'] = sender
		# Email body: use html tags to style
		html_content = """
		<p>Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.</p>
		"""
		email_body = MIMEText(html_content,'html')
		outer.attach(email_body)
		# List of attachments
		attachments = [resume_path]
		# Add the attachments to the message
		for file in attachments:
			try:
				with open(file, 'rb') as fp:
					msg = MIMEBase('application', "octet-stream")
					msg.set_payload(fp.read())
				encoders.encode_base64(msg)
				msg.add_header('Content-Disposition', 'attachment', filename=os.path.basename(file))
				outer.attach(msg)
			except:
				print("Unable to open one of the attachments. Error: ", sys.exc_info()[0])
				raise
		composed = outer.as_string()
		# Send the email
		try:
			with smtplib.SMTP('smtp.gmail.com', 587) as s:
				s.ehlo()
				s.starttls()
				s.ehlo()
				s.login(sender, gmail_password)
				s.sendmail(sender, recipients, composed)
				s.close()
			print("Email sent!")
		except:
			print("Unable to send the email. Error: ", sys.exc_info()[0])
			raise

	def send_emails(self, final = None):
		resume_path = "resume.pdf"
		if final is None:
			final = pd.read_csv('4_final.csv')
		for i in final.index:
			recipients = []
			num_recipients = 1
			email_exists = True if final['email1'][i] else False
			while email_exists:
				recipients.add(final['email1'][i])
				num_recipients += 1
				email_exists = True if final['email' + str(num_recipients)][i] else False
			self.send_to(recipients, resume_path)

if __name__ == "__main__":
	jobs = JobHunter(config.auth1)
	yclist = jobs.get_yclist()
	yclist_with_permalinks = jobs.get_permalinks(yclist)
	companies = jobs.get_company_info(yclist_with_permalinks)
	final = jobs.guess_emails(companies)
	jobs.send_emails(final)
