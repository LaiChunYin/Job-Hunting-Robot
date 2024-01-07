# **Job Hunting Robot**

### What is it:

A Python, Selenium-based tool designed to automates the job application process. This robot automates the search for job listings and crafts personalized cover letters by analyzing job descriptions using LLM. It's a time-saving solution for job seekers, streamlining the tedious task of tailoring applications for each job opening and increasing the chances of landing the perfect job.

### Features:

There are two modes:

1. Scan Job Mode:
   The program will go the specified job website (currently only Indeed is supported), scans through the job search results, then generates a cover letter for each of the job it finds.
2. Interactive Mode:
   Users can paste a job link from Indeed/Linkedin into the terminal, then a tailored cover letter will be generated.

### Prerequisite:

1. Make sure that LibreOffice is installed for PDF generation.
2. Currently the program only works on MacOS

### How to Use:

1. Prepare the following files (samples are given):

   1. resources/templates/cover_letter_template.docx
   2. .env
   3. config/personal_information.yaml
   4. config/search_and_filter.yaml
2. Usage:
   job_hunting_bot [options] website

   Positional Arguments:
   website             Should be either "Indeed" or "Linkedin"

   Options:
   -h, --help          Show this help message and exit.

   -a                  Apply the job automatically

   -s <number>         Scan <number> of jobs from the website. Number of jobs should be an integer value.

   -i                  Interactive mode
   -v                  Print debugging logs

   Note:
   Either -s or -i must be specified, but not both.

   Examples:
   job_hunting_bot -a -s 5 indeed
   This command will scan 5 jobs from Indeed

   job_hunting_bot -i linkedin
   This command will run the interactive mode on Linkedin

### Caution:

1. Do not click the any of the buttons on the webdriver. It may affect the program
2. Please check manually all the information and the cover letters before submitting a job application
3. Do not include any tab characters in the prompt file

### TODO:

1. ChatGPT API Integration
2. Support scanning Linkedin jobs
3. Improve prompts
4. Add more information/questions that can be filled automatically during job application
5. Auto generate a tailored resume according to the users experience and the job description
6. Support Windows version
7. Testing
8. Documentation
9. Add Typings
10. Support different login modes besides Google login

I warmly welcome contributions and feedback from the community.
