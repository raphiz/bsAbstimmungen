Stage 1
x1. Implement relationships between councillor and fraction, votes, voting etc.
x2. Work existing councillors / fractions
x3. Improve test case - parse a lot of the docs

Stage 2
x1. Build a scraper that fetches the docs and takes from/to parameters
x2. Test the scraper
$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
$$$$$$$$$$$4 3. LOGGING $$$$$$$$$$$$$$$$$$$$
$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
3. Replae nose with pytest
3. Use pyp instead of cpython
4. Repalce sqlalchemy with peewee (peewe is stronger when it comes to querying)
5. Isolate long parsing tests into a separate tests suite to speed up development time


Stage 3
* Build scrapers that fetch additional information from the website
    * Councillor data
    * Fraction information

Stage 4
* Create a "task", that fetches the current session, scrapes all additional data and stores it in the db.
* Create a "task", that builds a HTML website

Stage 5
* Perform calculations
    * Best friend/ enemy
    * Percentage Yes/No/Away
    * Rebelling?

Stage 6
* Comparison view (takes the MP data from a generated JSON doc)

More:
* get inspiration from http://smartmonitor.ch/
* add indices
* Abstraction for the ENUM
* test mysql...
