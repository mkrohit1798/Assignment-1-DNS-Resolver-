import sys
import datetime
import dns.resolver
import dns.query
import time

# root servers from https://www.iana.org/domains/root/servers
root_servers_IANA =  ['198.41.0.4', '199.9.14.201', '192.33.4.12', '199.7.91.13', '192.203.230.10', '192.5.5.241', '192.112.36.4', '198.97.190.53', '192.36.148.17', '192.58.128.30', '193.0.14.129', '199.7.83.42', '202.12.27.33']


def accessNextLevelServers(domain, server, category):
    reply = None
    # generate UDP query
    try:
            query = dns.message.make_query(domain, category)
            reply = dns.query.udp(query, server, timeout = 1)
    except:
            return None
    
    if not reply:
        return None
    
    # check if answer, authority sections are there and whether they incicate SOA(Start of Authority)
    if (len(reply.answer) > 0 or ((len(reply.authority) > 0) and (reply.authority[0].rdtype == dns.rdatatype.SOA))):
        return [server]
    
    res = []
    
    # checking for any additional fields
    if len(reply.additional) > 0:
        for x in reply.additional:
            res.append(x[0].to_text())
    
    if res:
        return res
    
    auth_name_server = None
    
    # check for the first authoritative server encountered
    if len(reply.authority) > 0:
        auth_name_server = reply.authority[0][0].to_text()
    
    if auth_name_server:
        return resolveDNS(auth_name_server, category)
    else:
        return None
    
    return []



# resolution process begins from the root server -> top level domain -> sub-level domains  
def resolveDNS(name, type):
    # splitting by domain name
    domain = dns.name.from_text(name)
    domainList = str(domain).split('.')
    domainList = domainList[:-1]
    
    input_domain = list(reversed(domainList))
    query = input_domain[0] + "."
    
    for server in root_servers_IANA:
        current_servers = accessNextLevelServers(query, server, type)
        
        if current_servers:
            break
    
    if current_servers == None:
        return []
    
    subset_domain = input_domain[1:]
    for dd in subset_domain:
        query = dd + '.' + query
        
        if current_servers == None:
            return []
        
        for server in current_servers:
            try:
                next_level_servers = accessNextLevelServers(query, server, type)
                if next_level_servers:
                    current_servers = next_level_servers
            except:
                pass
    
    return current_servers

# function for implementing Dig command functionlaity
def DigInit(domainName, domainType):
    servers = resolveDNS(domainName, domainType)
    
    if servers == None:
        return None
    
    for s in servers:
        try:
            query = dns.message.make_query(domainName, domainType)
            result = dns.query.udp(query, s, timeout = 1)
        except:
            return None
                
        if result is not None:
            return result
    
    return None
 
 # function for invoking the Dig implementation and producing output similar to the actual Dig Command       
def myDig(domainName, domainType):
    time_start = time.time()
    result = DigInit(domainName, domainType)
    total_time_taken = time.time() - time_start
    
    if result:
        if len(result.answer) > 0:
            r_section = result.answer[0]
            r_section1 = r_section[0]
        
            if(type == 'A' and r_section1 == dns.rdatatype.CNAME):
                cname_answer = DigInit(str(r_section1), "A")
                result.answer += cname_answer.answer
    
        output = ""
    
        output += "QUESTION SECTION:\n" + result.question[0].to_text() + "\n\n\n" + "ANSWER SECTION:\n"
    
        for a in result.answer:
            output += a.to_text() + "\n"
        
        output += "\n" + "Query Time: "
        output += str(total_time_taken) + "sec\n"
        
        currentDateTime = datetime.datetime.now()
        output += currentDateTime.strftime("%a %b %d %H:%M:%S %Y\n")
        output += "MSG SIZE rcvd: " + str(sys.getsizeof(result))
        return output
    else:
        print ("Cannot resolve DNS")

        
if __name__ == '__main__':
    domainName = sys.argv[1]
    domainType = sys.argv[2]

    print(myDig(domainName, domainType))