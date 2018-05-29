# Table of Contents
1. [Description of EDGAR Analytics Challenge](#description-of-edgar-analytics-challenge)
2. [Data Format](#data-format)
3. [Implementation Details](#implementation-details)

# Description of EDGAR Analytics Challenge
The Securities and Exchange Commission's Electronic Data Gathering, Analysis and
Retrieval (EDGAR) system contains financial documents and logs of users who
request documents from their system.

The task at hand is to determine (for each user) how many documents were
accessed and how long the length of their document request session was for a
given "stream" of data.

A **single user session*** is defined to have started when the IP address first
requests a document from the EDGAR system and continues as long as the same user
continues to make requests. The session is over after a certain period of time
has elapsed and the user makes no requests for documents.

# Data Format
## Input
Data is input as a CSV file containing at least the following fields:

- `ip`: identifies the IP address of the device requesting the data. While the
  SEC anonymizes the last three digits, it uses a consistent formula that allows
  you to assume that any two ip fields with the duplicate values are referring
  to the same IP address
- `date`: date of the request (yyyy-mm-dd)
- `time`: time of the request (hh:mm:ss)
- `cik`: SEC Central Index Key
- `accession`: SEC document accession number
- `extention`: Value that helps determine the document being requested

## Output
The output file with the information about each of the users' sessions should be
a header-less csv file, with each line formatted as:  
`[ip],[session start date time],[session end date time],[session length],[doc count]`  

e.g.  
`101.81.133.jja,2017-06-30 00:00:00,2017-06-30 00:00:00,1,1`

## Emulating streaming
Since large-scale data streaming requires considerable resources, this problem
has been simplified down to simply reading in a CSV file. Here, in the interest
of simplicity, the entire CSV document is read into memory. This is acceptable
for small proof-of-concept implementations but is is not tractable for files on
the order of gigabytes.

Streaming could be emulated by taking in a single line, processing it (and all
necessary steps) before moving on. This would likely be slower and more complex.
In order to make it scalable a larger data infrastructure such as a
Lambda-architecture would be a preferable choice.

### Real time vs. event time
Normally, in a streaming environment, a real-time clock is used to determine the
life of sessions. This can be easily implemented using a time-to-live counter
on, e.g. Redis.In our case, since there is no real-time streaming, events are
triggered the reading of a new line in the log. This acts as the 'clock'.

# Implementation Details
The first step is to read (into memory) and process the CSV file, retaining
only the relevant pieces of information (stored on `raw_data`). This is then 
processed. 

For each piece of processed data (a row in the CSV file), a User and a Session
are assigned. A User consists of a unique IP address and the accompanying
Session, which is determined based on (potentially) the User's previous sessions
and the current one. The User's session is created or updated, followed by a
checking of all other open Sessions to see if any should be closed.

Once the end of the file is reached, all open Sessions are updated and closed.

## Program Performance
Running the log processing program on an 0.5M line CSV file (~56Mb) takes
approximately 40 seconds, with a majority of the time spent on []. The timings
were performed on a Mid 2015 MacBook Pro with a 2.8GHz Intel Core i7 and 16gb
DDR3 memory.

Left and right pop/append from a python deque is _O_(1) and is preferable to
internal list searches which scale as _O_(_N_), where _N_ is the size of the
list. Additionally, since the deque is start-time-ordered, once a User's session
with session time less than the inactivity period time, all of the remaining
open sessions can be skipped using a deque.rotate() to reset the order of the
deque. This scales as _O_(_k_), where _k_ is the number of items rotated, which
will be in the worst case _O_(_N_).

The program is not memory bound, so in order to improve the overall performance
of the program, creating a blocks over which to perform the sessionization would
be advantageous. Threading using shared memory would also be an additional route
to improving the overall performance.

## Unit tests py.test
Included in this repository are two different testing frameworks.

### Insight testsuite
In `./insight_testsuite` are included a variety of tests to check the behavior
of the end result of running the log processing program. The test suite can be
run by running the following command:  
`cd insight_testsuite && ./run_tests.sh`

A report will be created that shows the pass/fail for each of the tests in the
`./insight_testsuite/tests` directory, as well as a side-by-side diff of the
output files. The test report (e.g. 5 of 6 tests passed) is generated using
`diff`, while the comparison of output files is done using `sdiff`.

### Py.tests
Additional finer-level tests are available and written in Python. These tests
can be found in `./tests_py`. These are broken down into files for testing the
main different classes and functionalities. These tests can be run using the 
following command:  
`py.test` 


