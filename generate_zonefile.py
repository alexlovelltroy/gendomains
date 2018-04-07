#!/usr/local/bin/python2.7

from sys import argv
import random

# You'll need to add a frontmatter here

#$ORIGIN bulgaria.lovelltroy.net.
#$TTL 86400
#
#@       3600    SOA     a.ns.bulgaria.lovelltroy.net. hostmaster.bulgaria.lovelltroy.net. (
#                        2017060701      ; serial
#                        1800            ; refresh
#                        7200            ; retry
#                        1209600         ; expire
#                        3600 )          ; negative
#
#                NS      a.ns.bulgaria.lovelltroy.net.
#                NS      b.ns.bulgaria.lovelltroy.net.
#
#                MX      0 mail.bulgaria.lovelltroy.net.

script, wordlist_file, domain = argv

ip = 1
wordfile = open(wordlist_file, 'r')
zonefile = open(domain + ".zone", 'w')
revfile = open(domain + ".zone.rev4", 'w')

random_octet = random.randint(3,254)

hostnames = []
for line in wordfile.readlines():
    hostnames.append(line.replace(" ","").strip().lower())

random.shuffle(hostnames)


for hostname in hostnames:
    if ip < 256:
        zonefile.write(hostname + "\t\t\tA\t192.168." + str(random_octet) + "." + str(ip) + "\n")
        revfile.write(str(ip) + "\tIN\tPTR\t" + hostname + "." + domain + ".\n" )
        ip = ip + 1
    else:
        break

wordfile.close()
zonefile.close()
revfile.close()
