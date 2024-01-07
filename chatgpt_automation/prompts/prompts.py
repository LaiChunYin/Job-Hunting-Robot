from config.config import Config
# Do not include any tab characters in the prompts

WRITE_COVER_LETTER = """Acting as professional hiring manager that is hiring the position of {position}.
Tailor make a cover letter according to the given resume and job description provided below.
Guidelines for writing:
1. Make sure that there are not any grammatical errors and typos
2. It is allowed to slightly exaggerate, modify experiences stated in the resume or make up/imagine some working experience/situation that I may have had/faced based on my working experience stated in the resume in the answers.
3. The job description given is in HTML format.
4. Should match keywords in the job description and should give related examples/experience to elaborate on the keywords
5. No more than 500 words
6. Only give the main body. DO NOT give any other things like the greeting, closing etc

Resume:
'
{resume}
'

job description:
'
{job_desc}
'
 """

FIND_KEY_WORDS = """
Act as an Applicant Tracking System (ATS), find keywords in the job description below that a resume has to match to get an interview.
Requirements:
1. Only give the answer in comma-separated values. 
2. Do not output other irrelevant sentences.
For example:
Python, Object Oriented Design, Javascript

job description:
'
{job_desc}
'
"""

WRITE_RESUME = """
Act as a Applicant Tracking System (ATS), modify the given resume so that it matches the given job description. Below are some guidelines:
1. Make sure that there are not any grammatical errors and typos
2. It is allowed to slightly exaggerate, modify experiences stated in the resume or make up/imagine some working experience/situation that I may have had/faced based on my working experience stated in the resume in the answers.
3. The job description given is in HTML format.
4. Should match keywords in the job description and should give related examples/experience to elaborate on the keywords
5. No more than 500 words

Resume:
'
{resume}
'

Job Desription:
'
{job_desc}
'
"""

GET_COMPANY_ADDRESS = """
Find the address of the company {company}
You may use your existing knowlege, search on Google.com, search on Google Map or search directly on the company's website
Display the address as a JSON string having the following keys:
1. street
2. city
3. province
4. country
5. postalCode
If the field does not exist, just ignore the key.

For example:
{{"street": "123 Main Steet","city": "Toronto","province": "ON""country": "Canada", "postalCode": "M2J 123"}}
"""

RESUME = Config.PERSONAL_INFO["resume"]