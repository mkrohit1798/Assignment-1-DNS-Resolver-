from re import I
from ssl import SSL_ERROR_SSL
import matplotlib.pyplot as plt
import time
import dns.query
import dns.resolver as dnsres
import numpy as np

#Top 25 sites from https://www.similarweb.com/top-websites/
top_25_sites = ['google.com', 'youtube.com', 'facebook.com', 'twitter.com','instgram.com', 'baidu.com', 'wikipedia.org', 'yandex.ru',
                'yahoo.com', 'whatsapp.com', 'amazon.com', 'live.com', 'netfilx.com', 'reddit.com', 'tiktok.com', 'linkedin.com', 'office.com',
                'samsung.com', 'vk.com', 'xhamster.com', 'weather.com', 'twitch.tv', 'mail.ru', 'naver.com', 'discord.com']

root_server_list = ['198.41.0.4','199.9.14.201','192.33.4.12', '199.7.91.13','192.203.230.10','192.5.5.241',
                 '192.112.36.4', '198.97.190.53', '192.36.148.17', '192.58.128.30','193.0.14.129','199.7.83.42','202.12.27.33']

def resolveRecords(domainName, domainType, rootServers):
    try:
        
        if domainType == "MX" or domainType == "NS":
            domain1 = domainName.replace("www.", "")
            name = dns.name.from_text(domain1)
        else:
            name = dns.name.from_text(domainName)
            
        for root in rootServers:
            query = dns.message.make_query(name, domainType, root)
            reply = dns.query.udp(query, root, timeout = 1)
            flag = dns.flags.to_text(reply.flags)
            flag = flag.split(" ")[1]
            
            while len(reply.answer) == 0:
                if len(reply.additional) > 0:
                    for resp in reply.additional:
                        for j in resp:
                            if dns.rdatatype.to_text(j.rdtype) == 'A' or dns.rdatatype.to_text(j.rdtype) == 'NS' or dns.rdatatype.to_text(j.rdtype) == 'MX':
                                reply1 = resolveRecords(domainName, domainType, [j.address])
                                if reply1 is not None:
                                    return reply1
                elif len(reply.authority) > 0:
                    if dns.rdatatype.to_text(reply.authority[0].rdtype) == 'SOA':
                        return reply, 1, 1
                    
                    for rep in reply.authority:
                        for rr in rep:
                            r = resolveRecords(str(rr), "A", root_server_list)
                            
                            if r is not None:
                                for i in r[0].answer:
                                    for ii in i:
                                        r = resolveRecords(domainName, domainType, [str(ii)])
                                    
                                    if r is not None:
                                        return r
            if flag == 'AA' and len(reply.answer) > 0:
                for resp in reply.answer:
                    if dns.rdatatype.to_text(resp.rdtype) == 'A' or dns.rdatatype.to_text(resp.rdtype) == 'MX' or dns.rdatatype.to_text(resp.rdtype) == 'NS':
                        return reply, 1, 1
                    elif dns.rdatatype.to_text(resp.rdtype) == 'CNAME':
                        canonical_name = str(resp.items[0])
                        
                        reply1 = resolveRecords(canonical_name, domainType, root_server_list)
                        if reply1 is not None:
                            return reply1, resp, canonical_name
                break
    except dns.exception.Timeout:
        pass


time_array0 = []

for site in top_25_sites:
    sum = 0
    for x in range(5):
        t1 = int(round(time.time() * 1000))
        resolveRecords(site, 'A', root_server_list)
        t2 = int(round(time.time() * 1000))
        difference = t2 - t1
        sum = sum + difference
        
    avg = sum/5
    
    time_array0.append(round(avg,1))

time0 = np.sort(time_array0)
    
res = dnsres.Resolver(configure = False)
res.nameservers = ['8.8.8.8', '8.8.4.4']

time_array1 = []

for site in top_25_sites:
    t1 = time.time()
    domain = site
    sum = 0
    
    for x in range(5):
        t1 = int(round(time.time() * 1000))
        res.resolve(x, 'A')
        t2 = int(round(time.time() * 1000))
        difference = t2 - t1
        sum = sum + difference
        
    avg = sum/5
    time_array1.append(round(avg, 1))
time1 = np.sort(time_array1)
    
res2 = dnsres.Resolver(configure = False)
res2.nameservers = ['185.199.108.154']

time_array2 = []

for site in top_25_sites:
    t1 = time.time()
    domain = site
    sum = 0
    
    for x in range(5):
        t1 = int(round(time.time() * 1000))
        res2.resolve(x, 'A')
        t2 = int(round(time.time() * 1000))
        difference = t2 - t1
        sum = sum + difference
        
    avg = sum/5
    time_array2.append(round(avg,2))

time2 = np.sort(time_array2)

p0 = 1. * np.arange(len(time_array0))/(len(time_array0) - 1)
p1 = 1. * np.arange(len(time_array1))/(len(time_array1) - 1)
p2 = 1. * np.arange(len(time_array2))/(len(time_array2) - 1)

plt.axis([0, 1000, 0, 1])
plt.plot(time1, p1, time0, p0, time2, p2)
plt.margins(0.03)
plt.xlabel('Time (in milliseconds)')
plt.ylabel('CDF')
plt.show()
    

