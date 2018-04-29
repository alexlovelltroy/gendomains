# Generate dhcp and dns configurations for OpenBSD

I run my home network behind an OpenBSD router for historical reasons.  I keep the initial configuration for it in [Packer and Ansible](http://github.com/alexlovelltroy/openbsd-router), and try to treat it as an appliance rather than a computer I play with.  Some time ago, I wrote a quick python script to generate a purely internal domain structure.  That means a dhcpd.conf file and a corresponding domain zonefile and reverse DNS zone file for nsd.  Both of those need to be intercepted by the unbound configuration file for internal resolution.