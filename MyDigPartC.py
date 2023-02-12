import dns.resolver
import dns.query
import time
import numpy as np
import matplotlib.pyplot as plt
from MydigResolverPartA import DigInit  #importing the MyDig resolver routines from Part A

# 5 random websites out of top 25 websites selected from https://www.similarweb.com/top-websites/
top_5_sites = ['reddit.com', 'youtube.com', 'tiktok.com','instagram.com', 'google.com', 'netflix.com']

# root servers from https://www.iana.org/domains/root/servers
root_servers_IANA =  ['198.41.0.4', '199.9.14.201', '192.33.4.12', '199.7.91.13', '192.203.230.10', '192.5.5.241', '192.112.36.4', '198.97.190.53', '192.36.148.17', '192.58.128.30', '193.0.14.129', '199.7.83.42', '202.12.27.33']


        
def myDig(domainName, domainType): # This will act as resolver_0 for the performance calculation
    try:
        result = DigInit(domainName, domainType)
        
    except dns.exception.Timeout:
        print("DNS operation timed out")

    
time_myDig=[]
time_google=[]
time_localdns=[]
resolver_1=dns.resolver.Resolver(configure=False) #resolver_1 uses google dns
resolver_1.nameservers=['8.8.4.4']

resolver_2=dns.resolver.Resolver(configure=False) #resolver_2 uses local dns
resolver_2.nameservers=['8.8.8.8'] #Ip address for this resolver is retrieved by using the T-Mobile Hotspot, 
                                         #which gives details of the local DNS servers present in the area

for site in top_5_sites:
    sum0=0
    sum1 = 0
    sum2 = 0
    domain = site
    for j in range(10): # perform resolution for each website 10 times
        
        # performance of myDig resolver
        t1_Mydig = int(round(time.time() * 1000))
        myDig(site, 'A')
        t2_Mydig = int(round(time.time() * 1000))
        difference_Mydig = t2_Mydig - t1_Mydig
        sum0 = sum0 + difference_Mydig
        
        # performance of google dns
        t1_google = int(round(time.time() * 1000))
        resolver_1.resolve(site, 'A')
        t2_google = int(round(time.time() * 1000))
        difference_google = t2_google - t1_google
        sum1 = sum1 + difference_google
        
        # performance of local dns
        t1_local = int(round(time.time() * 1000))
        resolver_2.resolve(site, 'A')
        t2_local = int(round(time.time() * 1000))
        difference_local=t2_local - t1_local
        sum2 = sum2 + difference_local
        
    average_Mydig = sum0/10 # average time with Mydig resolver
    average_google = sum1/10 # average time with Google DNS
    average_local = sum2/10 # average time with Local DNS
    
    # printing the average time taken by the MyDig Resolver
    print ("Average resolving time for domain:",domain,"---->",average_Mydig," msec") 
    
    time_myDig.append(round(average_Mydig, 2))
    time_google.append(round(average_google, 2))
    time_localdns.append(round(average_local, 2))

time_myDig_sorted = np.sort(time_myDig)
p0 = 1. * np.arange(len(time_myDig))/(len(time_google) - 1)
print("Average time using MyDig resolver: ", time_myDig_sorted)

time_google_sorted = np.sort(time_google)
p1 = 1. * np.arange(len(time_google))/(len(time_google) - 1)
print("Average time using Google DNS: ", time_google_sorted)

time_localdns_sorted = np.sort(time_localdns)
p2 = 1. * np.arange(len(time_localdns))/(len(time_localdns) - 1)
print("Average time using Local DNS: ", time_localdns_sorted)

# t_arr = [time_myDig_sorted, time_localdns_sorted, time_google_sorted]
# plotting the performance of each resolver 

# plt.axis([0,1000, 0, 2])
# plt.plot(time_myDig_sorted, p0, color = "red", label = "myDig resolver")
# plt.plot(time_google_sorted, p1, color = "green", label = "google DNS")
# plt.plot(time_localdns_sorted, p2, color = "orange", label = "local DNS")
# plt.legend(loc = "upper right")

# plt.plot(time_google_sorted, p1, color = "green") 
# plt.plot(time_myDig_sorted, p0, color = "red") 
# plt.plot(time_localdns_sorted, p2, color = "orange")

# b1 = np.arange(len(time_myDig_sorted))
# b2 = np.arange(len(time_google_sorted))
# b3 = np.arange(len(time_localdns_sorted))   

# spacing = [1,2,3,4,5,6]
#**************** Default stacked  bar chart *****************
# plt.bar(spacing, time_myDig, color='green', align = "center", width = 0.25)
# plt.bar(spacing, time_google, color = 'orange', align="center", width = 0.25)
# plt.bar(spacing, time_localdns, color = 'cyan',align="center", width = 0.25)
# plt.xticks(spacing, top_5_sites)
# plt.margins(0.01)
#*************************************************************

time_array = [time_myDig, time_google, time_localdns]
spacing = np.arange(6)
plt.bar(spacing + 0.00, time_array[0], color = 'orange', width = 0.25, edgecolor = 'black')
plt.bar(spacing + 0.25, time_array[1], color = 'green', width = 0.25, edgecolor = 'black')
plt.bar(spacing + 0.50, time_array[2], color = 'red', width = 0.25, edgecolor = 'black')
plt.xticks(spacing, top_5_sites)

# plt.plot(color = 'orange', label = "MyDIG resolver")
# plt.plot(color = 'green', label = "Google DNS")
# plt.plot(color = 'red', label = "Local DNS")
plt.legend(labels = ['MyDIG Resolver', 'Google DNS', 'Local DNS'])

plt.xlabel('Sites')
plt.ylabel('Avg time')
plt.show()