#!/usr/bin/env python
import geoip2.database
import socket
import sys
import urllib2
import requests 
from urlparse import urlparse

# Some lists
embargoed_countries = [ 'IR', 'CU' , 'KP' , 'SD' , 'SY' ]
location_major_index = {
 '1': { 'idx_number': '2', 'region': 'Africa' },
 '2': { 'idx_number': '2', 'region': 'Asia' },
 '3': { 'idx_number': '0', 'region': 'Canada' },
 '4': { 'idx_number': '1', 'region': 'EU' },
 '5': { 'idx_number': '6', 'region': 'Middle-East' },
 '6': { 'idx_number': '0', 'region': 'North America' },
 '7': { 'idx_number': '3', 'region': 'Oceania' },
 '8': { 'idx_number': '5', 'region': 'South America' },
 '9': { 'idx_number': '0', 'region': 'US' },
}

http_url = raw_input("Mirror URL ? : ")
fqdn = urlparse(http_url).hostname
ipv4 = socket.gethostbyname(fqdn)
try:
  ipv6 = socket.getaddrinfo(fqdn, None, socket.AF_INET6)[0][4][0]
  type(ipv6)
except:
  ipv6 = ''
  print("No IPv6/AAAA for %s") % (fqdn)
  pass
print("Checking url %s ...") % (http_url)
geodb = geoip2.database.Reader('/usr/share/GeoIP/GeoLite2-City.mmdb')

country = 'Unknown'
continent = 'Unknown'
state = 'Unknown'

try:
  country = geodb.city(ipv4).country.iso_code
  try: 
    continent = geodb.city(ipv4).continent.code
  except:
    continent = 'Unknown'
  if country == 'US' or country == 'CA':
    try:
      print("Country is %s so trying state") % (country)
      state = geodb.city(ipv4).subdivisions.most_specific.iso_code
    except:
      pass
  else:
    if state is not None and len(state) == 2:          
      country = country + '-' + region
except:
  pass

if country in embargoed_countries:
  print("country %s in embargoed countries list") % (country)
  sys.exit(1)

country_name = geodb.city(ipv4).country.names['en']

print("Country: %s - %s") % (country_name,country)
if state is None:      
  state = raw_input("Unable to find state for country %s so please enter manually : " % (country) )

try:
  #current_ts = urllib2.urlopen(http_url+'timestamp.txt').read()
  current_ts = requests.get(http_url+'timestamp.txt')
  print current_ts.text
except:
  print('Unable to gather timestamp.txt - unavailable mirror ?')
  sys.exit(1)

print("Mirror URL: %s") % (http_url)
print("IPv4 Address: %s") % (ipv4)
print("IPv6 Address: %s") % (ipv6)
print("Country: %s - %s") % (country_name,country)
print("State: %s") % (state)
print("Continent: %s") % (continent)
print("Mirror Age/Status: %s") % (current_ts.text.strip('\n'))

for i in location_major_index:
  print("%s -> %s") % (i,location_major_index[i]['region'])
loc_maj_query= raw_input("Select location area from list [0-9]: ")
loc_maj = location_major_index[loc_maj_query]['region']
loc_maj_idx = location_major_index[loc_maj_query]['idx_number']

https_url = raw_input("HTTPS URL ? : ")
rsync_url = raw_input("rsync URL ? : ")
bandwidth = raw_input("Available bandwidth  [1000] ? : ") or "1000"
sponsor_name = raw_input("Sponsor Name ? : ")
sponsor_url= raw_input("Sponsor URL? : ")
ip_1 = raw_input("First IP to authorize [%s] :" % (ipv4) ) or ipv4
ip_2 = raw_input("Second IP to authorize [%s] :" % (ipv6) ) or ipv6
contact_name = raw_input("Contact Name ? : ")
contact_email = raw_input("Contact email ? : ")

is_altarch = 'no'
altarch_http_url = ''
altarch_https_url = ''
altarch_rsync_url = ''

altarch = raw_input("Altarch Content ? [N] : ") or "N"
if altarch.lower() == 'y':
 is_altarch = 'yes'
 altarch_http_url = raw_input("Altarch HTTP URL ? : ")
 altarch_https_url = raw_input("Altarch HTTPS URL ? : ")
 altarch_rsync_url = raw_input("Altarch rsync URL ? : ")


if country == 'US' or country == 'CA':
  cc = country.lower()
  cc_continent = country.lower()
  country_name = state
  loc_maj = country
else:
  cc = country.lower()
  cc_continent = continent.lower()


print("====================================================================================================")
print("Here are the following SQL queries to do to add mirror :")
print("====================================================================================================")

print("insert into mirrors (name,url,`contact-email`,`location-major`,locmajidx,`location-minor`,http,https,rsync,bandwidth,cc,continent,centostext,`dvd-iso-host`,altarch, altarch_http, altarch_https, altarch_rsync) values('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','','yes','%s','%s','%s','%s');") % (sponsor_name, sponsor_url, contact_email, loc_maj, loc_maj_idx, country_name, http_url, https_url, rsync_url, bandwidth, cc, cc_continent, is_altarch, altarch_http_url, altarch_https_url, altarch_rsync_url)
print("insert into ipaddresses (mirror_id, ip) select max(mirror_id), '%s' from mirrors;") % (ip_1)

if len(ip_2) > 1:
  print("insert into ipaddresses (mirror_id, ip) select max(mirror_id), '%s' from mirrors;") % (ip_2)

print("====================================================================================================")
print("You can now reply this in infra ticket:")
mail_body = 'Thanks !\n'
mail_body += '\n'
mail_body += 'Your mirror %s has been added to the mirrors DB \n' % (http_url)
mail_body += '\n'
mail_body += 'It will be listed as a public mirror (and on https://mirror-status.centos.org / https://www.centos.org/download/mirrors/ ) in the following minutes/hours. \n'
mail_body += 'Your IP address[es] (%s %s) has/have been added in the ACL and so you should be able to rsync from msync.centos.org in the next ~10min \n' % (ip_1,ip_2)
mail_body += '\n'
mail_body += 'Important : it only concerns CentOS Linux 7 and Stream 8. For Stream 9 and above, read (again) https://wiki.centos.org/HowTos/CreatePublicMirrors \n'
mail_body += '\n'
mail_body += 'Kind Regards,'
print(mail_body)

