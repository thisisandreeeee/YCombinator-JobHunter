#Job Hunter#
In the spring of 2016, I was looking for a one-year internship in Silicon Valley as a data science intern. The job search was not only long and arduous, but very time-consuming as well. So, I decided to spend even more time writing a script to automate most of the process.

###Setup###
For the script to work you will need a [crunchbase API key](), as well as a gmail account. Then, create a file called `config.py` with the following format:
```python
auth1 = "your crunchbase API key"
sender = "your gmail address"
emailpass = "your gmail password"
```

###Pseudocode###
1. I scraped [yclist.com](http://yclist.com/) using Python's beautiful soup, which gives me a list of ycombinator companies as well as their websites.
2. Then, using the crunchbase API service, I obtained additional information on each company including funding amount, number of employees, company address etc. This proved invaluable in helping me to filter and narrow down the long list of prospective companies to those relevant to my search.
3. I then tried guessing the email addresses of the founders using the following format: `<firstname>@<domain>`. Some of the email address were manually verified using LinkedIn's [rapportive](https://rapportive.com/) API, but do note that there will be a large number of invalid email addresses in the eventual list. One way this can be improved is to try different permutations of common email formats as well, and to automate the verification process.
4. After obtaining the email addresses, emails can be sent out programmatically to each company. I never got round to this step, as I had already got a company by then, but the plan would have been to send out Mailchimp like emails where I input the company / founder name into a template - so as to make the email seem more personal. 
