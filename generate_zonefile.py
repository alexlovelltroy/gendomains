#!/usr/bin/env python2.7

from sys import argv
import random
import datetime

#  Pull some simple arguments.  Argparser would help...  maybe
script, wordlist_file, domain = argv

#  Set some defaults 
ip = 1
random_octet = random.randint(3,254)
serial = datetime.datetime.now().strftime("%Y%m%d01")


#  Open the files
wordfile = open(wordlist_file, 'r')
zonefile = open(domain + ".zone", 'w')
revfile = open(domain + ".zone.rev4", 'w')


#  Set up the frontmatter and write it to the zonefiles
zone_frontmatter = "$ORIGIN " + domain + ".\n\n\n@\t\t\t\t3600 SOA ns1." + domain + ". (" + serial + " 1800 600 1209600 1800)\n\n"
zonefile.write(zone_frontmatter)
rev_frontmatter = "$ORIGIN " + str(random_octet) + ".168.192.in-addr.arpa.\n\n\n@\t\t\t\t3600 SOA ns1." + domain + ". (" + serial + " 1800 600 1209600 1800)\n\n"
revfile.write(rev_frontmatter)

# Pull the wordlist into a hostnames array
hostnames = []
for line in wordfile.readlines():
    hostnames.append(line.replace(" ","").strip().lower())
# Mix it up
random.shuffle(hostnames)

#  Iterate through the hostnames and write symmetrical entries to both files
#  This will write a maximum of 255 lines, but less if there's not enough words
for hostname in hostnames:
    if ip < 256:
        zonefile.write(hostname + "\t\t\tA\t192.168." + str(random_octet) + "." + str(ip) + "\n")
        revfile.write(str(ip) + "\tIN\tPTR\t" + hostname + "." + domain + ".\n" )
        ip = ip + 1
    else:
        break

# Shut it down
wordfile.close()
zonefile.close()
revfile.close()
