#!/usr/bin/env python2.7

from sys import argv
import random
import datetime

#  Pull some simple arguments.  Argparser would help...  maybe
script, wordlist_file, domain = argv

#  Set some defaults 
ip = 1
random_octet = str(random.randint(3,254))
serial = datetime.datetime.now().strftime("%Y%m%d01")


#  Open the files
wordfile = open(wordlist_file, 'r')
zonefile = open(domain + ".zone", 'w')
revfile = open(domain + ".zone.rev4", 'w')
dhcpd_conf = open("dhcpd.conf", 'w')


#  Set up the frontmatter and write it to the zonefiles
zone_frontmatter = "$ORIGIN " + domain + ".\n\n\n@\t\t\t\t3600 SOA ns1." + domain + ". (" + serial + " 1800 600 1209600 1800)\n\n"
zonefile.write(zone_frontmatter)
rev_frontmatter = "$ORIGIN " + str(random_octet) + ".168.192.in-addr.arpa.\n\n\n@\t\t\t\t3600 SOA ns1." + domain + ". (" + serial + " 1800 600 1209600 1800)\n\n"
revfile.write(rev_frontmatter)

#  Set up the DHCP frontmatter and write it to the conf file
dhcpd_frontmatter = ("subnet 192.168." + random_octet + ".0 netmask 255.255.255.0 {\n" 
                     "\toption routers 192.168." + random_octet + ".1;\n"
                     "\toption domain-name-servers 192.168." + random_octet + ".1;\n"
                     "\toption domain-name \"" + domain + "\";\n"
                     "\trange 192.168." + random_octet + ".30 192.168." + random_octet + ".254;\n"
                     "\tallow booting;\n"
                     "\tallow bootp;\n"
                     "\t\tnext-server 192.168." + random_octet + ".1; \n"
                     "\t\tfilename \"/tftpboot/coreos_production_pxe.vmlinuz\";\n\n"
)
dhcpd_conf.write(dhcpd_frontmatter)



# Pull the wordlist into a hostnames array
hostnames = []
for line in wordfile.readlines():
    hostnames.append(line.replace(" ","").strip().lower())
# Mix it up
random.shuffle(hostnames)

#  Iterate through the hostnames and write symmetrical entries to all files
#  This will write a maximum of 255 lines, but less if there's not enough words
for hostname in hostnames:
    if ip < 256:
        zonefile.write(hostname + "\t\t\tA\t192.168." + str(random_octet) + "." + str(ip) + "\n")
        revfile.write(str(ip) + "\tIN\tPTR\t" + hostname + "." + domain + ".\n" )
        dhcpd_conf.write("host " + hostname + " {\n\toption host-name \"" + hostname + "." + domain + "\";\n\tfixed-address 192.168." + random_octet + "." + str(ip) + ";\n}\n")
        ip = ip + 1
    else:
        break

# Shut it down
wordfile.close()
zonefile.close()
revfile.close()
dhcpd_conf.write("\n}")
dhcpd_conf.close()

print("192.168." + str(random_octet) + ".0")
