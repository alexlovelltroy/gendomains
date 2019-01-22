#!/usr/bin/env python3

import argparse
import datetime
import hashlib
import ipaddress
import random
import sys
import yaml


def read_config_file(filename):
    configfile = open(filename, 'r', encoding='utf-8')
    config = yaml.load(configfile)
    configfile.close()
    return config

def write_config_file(filename):
    configfile = open(filename, 'w', encoding='utf-8')
    configfile.write(yaml.dump(config, default_flow_style=False))
    configfile.close()


def mix_wordlist_with_config(wordlist_file, config):
    # Use the config to generate a list of ip
    local_subnet = ipaddress.ip_network(config['subnet'])
    local_ips = list(local_subnet.hosts())

    # Pull the wordlist into a hostnames array
    wordfile = open(wordlist_file, 'r', encoding='utf-8')

    hostnames = []
    for line in wordfile.readlines():
        hostnames.append(line.replace(" ","").strip().lower().encode('utf-8'))
    wordfile.close()
    # Mix it up
    random.shuffle(hostnames)

    if not u'servers' in config.keys():
      config[u'servers'] = {}
    # iterate through the shuffled hostnames and ip addresses
    for idx, val in enumerate(hostnames):
      hostname = val.decode('utf-8')
      try:
        config[u'servers'][str(hashlib.md5(val).hexdigest())] = { 
          u'hwaddr' : "",
          u'instance-id' : str(hashlib.md5(val).hexdigest()),
          u'ipaddr' : str(local_ips[idx]),
          u'hostname' :  str(hostname)
        }
      except IndexError:
        pass
    return config 

def generate_random_config(domain):
    base_config = {}
    base_config['domain'] = domain
    base_config['subnet'] = "192.168." + str(random.randint(3,254)) + ".0/24"
    return base_config

  
def write_files(config):
    serial = datetime.datetime.now().strftime("%Y%m%d01")
    domain = config['domain']
    local_subnet = ipaddress.ip_network(config['subnet'])
    local_ips = list(local_subnet.hosts())
    reverse_pointer = str(local_subnet.network_address.reverse_pointer).strip("0.")
    
    #  Open the files
    zonefile = open(domain + ".zone", 'w', encoding='utf-8')
    revfile = open(domain + ".zone.rev4", 'w', encoding='utf-8')
    dhcpd_conf = open("dhcpd.conf", 'w', encoding='utf-8')



    #  Set up the frontmatter and write it to the zonefiles
    zone_frontmatter = "$ORIGIN " + domain + ".\n\n\n@\t\t\t\t3600 SOA ns1." + domain + ". (" + serial + " 1800 600 1209600 1800)\n\n"
    zonefile.write(zone_frontmatter)
    rev_frontmatter = "$ORIGIN " + domain + ".  ; default zone domain \n$TTL 86400\n\n\n" + reverse_pointer + "\tIN SOA ns1." + domain + ". admin." + domain +". (" + serial + " 1800 600 1209600 1800)\n\n"
    revfile.write(rev_frontmatter)
    
    #  Set up the DHCP frontmatter and write it to the conf file
    dhcpd_frontmatter = ("subnet " + str(local_subnet.network_address) + " netmask " + str(local_subnet.netmask) + " {\n" 
                             "\toption routers " + str(local_ips[0]) +  ";\n"
                         "\toption domain-name-servers " + str(local_ips[0]) + ";\n"
                         "\toption domain-name \"" + domain + "\";\n"
                         "\trange " + str(local_ips[0]) + " " + str(local_ips[-1]) + " ;\n"
                         "\tallow booting;\n"
                         "\tallow bootp;\n"
                         "\t\tnext-server" + str(local_ips[0]) + " ; \n"
                         "\t\tfilename \"/tftpboot/coreos_production_pxe.vmlinuz\";\n\n"
    )
    dhcpd_conf.write(dhcpd_frontmatter)

    for idx, val in config['servers'].items():
      zonefile.write(str(val['hostname']) + "\t\t\tA\t" + str(val['ipaddr']) + "\n")
      revfile.write(str(ipaddress.ip_address(val['ipaddr']).reverse_pointer) + "\tIN\tPTR\t" + str(val['hostname']) + "\n" )
      dhcpd_conf.write("host " + str(val['hostname']) + " {\n\toption host-name \"" + str(val['hostname']) + "." + domain + "\";\n\tfixed-address " + str(val['ipaddr']) + ";\n}\n")
    
    # Shut it down
    zonefile.close()
    revfile.close()
    dhcpd_conf.write("\n}")
    dhcpd_conf.close()




if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument("wordlist", help="file containing your wordlist - see bulgarian_cities.txt")
  parser.add_argument("--domain", help="domain name to use in dns and dhcp configurations")
  parser.add_argument("--subnet", help="subnet to use in dns and dhcp configurations")
  parser.add_argument("--config", help="yaml file to load as configuration")
  args = parser.parse_args()
  if args.config:
    try:
      config = read_config_file(args.config)
    except FileNotFoundError:
      print("File Not Found: " + args.config)
      sys.exit(1)
    except yaml.parser.ParserError:
      print("Unparseable config YAML")
      raise
  else:
    if args.domain:
      config = generate_random_config(args.domain)
    else:
      print("--domain is required if not passing a config file")
      sys.exit(1)

  config = mix_wordlist_with_config(args.wordlist,config)
  write_files(config)
  print(yaml.dump(config, default_flow_style=False))
  sys.exit(0)


