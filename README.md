# SI507_FinalProject

README
Claire Marshall


Project Summary:

This project scrapes the top headlines from two news sources: the Conservative blog/site RedState and the Liberal blog/site InTheseTimes. On GitHub, I had initially intended my project to scrape The HuffingtonPost and The Federalist. However, The Federalist blocks web scraping, and I could not find another Conservative source that I felt was comparable in depth to The HuffingtonPost. Thus, I chose two smaller sources, which were more comparable in terms of content and content amount.

After scraping the HTML and pulling out the headlines, these are entered into a database (using CSV files), which also collects article author, URL, and source (either RS or ITT).

The ultimate result -- the visualization component -- is a webpage that compares a random headline from RS and ITT (if one exists) depending on a search term the user appends to the localhost URL.

The cache is deleted every 24 hours, so that new headlines can be scraped daily.


Steps:

1. Fork and clone the repository SI507_FinalProject
2. Run requirements.txt to install all necessary libraries and modules to run the project (do this in a virtual environment if you so choose)
3. Enter database credentials into the appropriate places in config.py
4. Run code from the command line (don't forget to add runserver); this project requires no user input apart from the visualization component
5. If installed successfully, the user should then go to localhost:5000/headline/<word> and enter a search term in place of <word>
6. The resulting page should look something like Fin_Project_Ex.png
7. To check the correctness of the program, run fin_project_tests.py

Note:

The caching system has been lightly adapted from the nytimes.py (from discussion section) caching setup.
