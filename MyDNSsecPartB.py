import sys
import dns.query
import dns.rdtypes.ANY.NSEC
import dns.rdtypes.ANY.NSEC3


# root servers from https://www.iana.org/domains/root/servers
root_servers_IANA = ['198.41.0.4','199.9.14.201','192.33.4.12', '199.7.91.13','192.203.230.10','192.5.5.241','192.112.36.4', '198.97.190.53', '192.36.148.17', '192.58.128.30','193.0.14.129','199.7.83.42','202.12.27.33']

# recursive function to resolve and validate domain at each level starting from the root
def resolveDNS(domain, rtype, rootservers,zone,ds_parent):
    name = dns.name.from_text(domain)
    
    for root in rootservers:
        zone = str(zone)
        zone = dns.name.from_text(zone)
        query1 = dns.message.make_query(zone, dns.rdatatype.DNSKEY, want_dnssec=True)
        reply1 = dns.query.tcp(query1, root, timeout=1)
        query2 = dns.message.make_query(name, 'A', want_dnssec=True)
        reply2 = dns.query.tcp(query2, root, timeout=1)

        #perform validation of RRSig, DS and RRset from the root domain onwards,
        # followed by recursively validating the top-level domain ans so on 
        dnskey = reply1.answer[0]
        signed_ds_record = reply1.answer[1]
        ns=''
        if len(reply1.answer) > 0:
            try:
                dns.dnssec.validate(dnskey, signed_ds_record, {zone: dnskey})
            except Exception as e:
                print (e)
                print("DNSsec configured but failed to verify digital signature...")
                exit()

        # validate the current level domain and verifying chain of trust using delegation signer
        if len(reply2.answer) > 0:
            delegation_signer = reply2.answer[0]
            rrsig = reply2.answer[1]
            if (isinstance(delegation_signer[0], dns.rdtypes.ANY.NSEC.NSEC) or isinstance(delegation_signer[0], dns.rdtypes.ANY.NSEC3.NSEC3)):
                print("DNSsec is not supported...")
                exit()
            else:
                try:
                    dns.dnssec.validate(delegation_signer, rrsig, {zone: dnskey}) 
                except Exception as e:
                    print(e)
                    print("DNSsec configured but failed to verify digital signature...")
                    exit()
        else:
            ns = reply2.authority[0]
            delegation_signer = reply2.authority[1]
            rrsig = reply2.authority[2]
            if (isinstance(delegation_signer[0], dns.rdtypes.ANY.NSEC.NSEC) or isinstance(delegation_signer[0], dns.rdtypes.ANY.NSEC3.NSEC3)):
                print("DNSsec not supported....")
                exit()
            else:
                try:
                    dns.dnssec.validate(delegation_signer, rrsig, {zone: dnskey})
                except Exception as e:
                    print(e)
                    print("DNSsec configured but failed to verify digital signature...")
                    exit()
        
        
        if ds_parent is not None:
            for i in reply1.answer[0]:
                if str(i).split(" ")[0] == '257':
                    if dns.dnssec.make_ds(zone, i, "SHA256") == ds_parent[0]:
                        print("Validating chain of trust")
                        break
                    else:
                        print("Validation Failed")
                        exit()

       # perform preprocessing of the query 
        query = dns.message.make_query(name, rtype,use_edns=True)
        reply = dns.query.udp(query, root, timeout=1)
        flag = dns.flags.to_text(reply.flags)
        flag = flag.split(" ")[1]
        
        while len(reply.answer) == 0:
            
            if len(reply.additional) > 0:
                for i in reply.additional:
                    for j in i:
                        if dns.rdatatype.to_text(j.rdtype) == 'A' or dns.rdatatype.to_text(j.rdtype) == 'MX' or dns.rdatatype.to_text(j.rdtype) == 'NS':
                            for i in reply2.authority:
                                i = str(i)
                                k = i.split(" ")
                            zone_singing_key = k[0]
                            answer1 = resolveDNS(domain, rtype, [j.address], zone_singing_key, delegation_signer)
                            if answer1 is not None:
                                return answer1
            
            elif (len(reply.authority)) > 0:
                
                if (dns.rdatatype.to_text(reply.authority[0].rdtype) == 'SOA'):
                    return reply, 1, 1
                
                for i in reply.authority:
                    for j in i:
                        for i in reply2.authority:
                            i = str(i)
                            k = i.split(" ")
                        zone_singing_key = k[0]
                        r = resolveDNS(str(j), "A", root_servers_IANA, zone_singing_key, delegation_signer)
                        if r is not None:
                            for i in r[0].answer:
                                for j in i:
                                    for i in reply2.authority:
                                        i = str(i)
                                        k = i.split(" ")
                                    zone_singing_key = k[0]
                                    r = resolveDNS(domain, rtype, [str(j)], zone_singing_key, delegation_signer)
                                if r != None:
                                    return r

        print("Reply.answer is of this type: ",type(reply.answer))
        if (flag == 'AA') and len(reply.answer) > 0:
            for i in reply.answer:
                
                if (dns.rdatatype.to_text(i.rdtype) == 'A' or dns.rdatatype.to_text(i.rdtype) == 'MX' or dns.rdatatype.to_text(i.rdtype) == 'NS'):
                    return reply, 1, 1
                
                elif (dns.rdatatype.to_text(i.rdtype) == 'CNAME'):
                    canonical_name = str(i.items[0])
                    
                    for i in reply2.authority:
                        print(i)
                        i = str(i)
                        k = i.split(" ")
                    zone_singing_key = k[0]
                    reply1 = resolveDNS(canonical_name, rtype, root_servers_IANA, zone_singing_key, delegation_signer)
                    if reply1 is not None:
                        return reply1, i, canonical_name
            break
        

if __name__ == '__main__':
    domain=sys.argv[1]
    rtype=sys.argv[2]
    
answer,i,canonical_name= resolveDNS(domain, rtype, root_servers_IANA,'.',None)
print(answer)