Folder Contents:
1. Part A: MyDig resolver
2. Part B: DNS resolver with MyDNSsec functionality
3. Part C: MyDig resolver performance analysis(continued from Part A)
 
Instructions for running the program:
Python Interpreter version used: 3.10.6

-----------------------------****-----------------------------
1. Part A: Import libraries: dnspython, sys, datetime, time

run the file resolverForDNS.py as follows:
python MydigResolverPartA.py www.cloudflare.com A 
		   OR 
py MydigResolverPartA.py www.cloudflare.com A

use the same command when resolving records of type NS or MX or CNAME

----------------------------------------------------------------------------
2. Part B: Import libraries: sys, dnspython, dns.rdtypes.ANY.NSEC, dns.rdtypes.ANY.NSEC3

run the file MyDNSsecPartB.py as follows: 
python MyDNSsecPartB.py www.cloudflare.com A
		   OR
py MyDNSsecPartB.py www.cloudflare.com A

use the same command when resolving records of type NS or MX or CNAME

----------------------------------------------------------------------------
3. Part C: Import libraries: sys, dnspython, matplotlib, numpy
 
run the file MyDigPartC.py as follows:
python MyDigPartC.py
	OR
py MyDigPartC.py

use the same command when resolving records of type NS or MX or CNAME