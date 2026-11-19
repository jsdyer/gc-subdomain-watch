"""Track the public federal directory, keeping past editions and validated CT summaries."""
import concurrent.futures
from datetime import datetime, timezone
import gzip
from html.parser import HTMLParser
import json
from pathlib import Path
import re
from urllib.parse import urljoin, urlsplit, urlencode
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
DIRECTORY = 'https://www.canada.ca/en/government/dept.html'
SEEDS = ['20231120204928', '20251119232708']
HOMES = ['www.canada.ca', 'www2.gov.bc.ca', 'www.novascotia.ca', 'www.halifax.ca']
DATA = ROOT / 'web/data.json'

def read(url):
    with urlopen(Request(url, headers={'User-Agent':'CoolCode public web directory history'}), timeout=35) as response:
        raw=response.read()
        return gzip.decompress(raw) if raw.startswith(b'\x1f\x8b') else raw

def now():
    return datetime.now(timezone.utc).date().isoformat()

class Directory(HTMLParser):
    def __init__(self):
        super().__init__()
        self.record = None
        self.anchor = False
        self.name = []
        self.rows = {}

    def handle_starttag(self, tag, attrs):
        if tag == 'tr':
            self.record = ''
        if tag == 'a' and self.record == '' and dict(attrs).get('href'):
            self.record = urljoin(DIRECTORY, dict(attrs)['href'])
            self.anchor = True
            self.name = []

    def handle_data(self, data):
        if self.anchor:
            self.name.append(data)

    def handle_endtag(self, tag):
        if tag == 'a':
            self.anchor = False
        if tag == 'tr' and self.record:
            name = ' '.join(''.join(self.name).split())
            if name and urlsplit(self.record).scheme in ('https','http'):
                if name in self.rows and self.rows[name] != self.record:
                    raise ValueError('Duplicate institution name with competing URLs')
                self.rows[name] = self.record
            self.record = None

def source_edition(url, day):
    parser = Directory()
    parser.feed(read(url).decode('utf-8-sig','replace'))
    if len(parser.rows) < 120 or 'Bank of Canada' not in parser.rows:
        raise ValueError('Directory unavailable or table changed')
    return {'date':day, 'source':url, 'rows':dict(sorted(parser.rows.items()))}

def ct(host):
    url = 'https://api.certspotter.com/v1/issuances?' + urlencode({'domain':host,'include_subdomains':'false','expand':'issuer'})
    cursor, observed = '', {}
    for _ in range(10):
        batch = json.loads(read(url + ('&after='+cursor if cursor else '')))
        if not isinstance(batch,list):
            raise ValueError('Unrecognized CT response')
        if not batch:
            break
        for row in batch:
            observed[row['id']] = row['issuer']['friendly_name']
        new_cursor = batch[-1]['id']
        if new_cursor == cursor:
            raise ValueError('CT pagination did not progress')
        cursor = new_cursor
        if len(batch)<100:
            break
    else:
        raise ValueError('CT response exceeds collector limit')
    issuers = {}
    for label in observed.values():
        issuers[label] = issuers.get(label,0)+1
    return {'date':now(),'count':len(observed),'issuers':issuers}

def main():
    previous = json.loads(DATA.read_text()) if DATA.exists() else {}
    editions = previous.get('editions',[])
    if not editions:
        def ingest(stamp):
            url='https://web.archive.org/web/'+stamp+'id_/'+DIRECTORY
            return source_edition(url,stamp[:4]+'-'+stamp[4:6]+'-'+stamp[6:8])
        with concurrent.futures.ThreadPoolExecutor(2) as pool:
            editions = list(pool.map(ingest, SEEDS))
    latest = source_edition(DIRECTORY,now())
    if editions[-1]['date']==latest['date']:
        editions[-1] = latest
    elif editions[-1]['rows'] != latest['rows']:
        editions.append(latest)
    certificates = previous.get('certificates',{})
    for host in HOMES:
        try:
            certificates[host] = ct(host)
        except (OSError, ValueError, KeyError) as exc:
            print('CT source unavailable for '+host+': '+str(exc))
    result = {'retrieved':now(),'first':editions[0]['date'],'latest_change':editions[-1]['date'],
              'count':len(latest['rows']),'editions':editions,'certificates':certificates}
    staging = DATA.with_suffix('.tmp')
    staging.write_text(json.dumps(result, ensure_ascii=False,separators=(',',':'))+'\n')
    staging.replace(DATA)
    from xml.etree.ElementTree import Element, SubElement, ElementTree
    channel = Element('rss',version='2.0')
    inner = SubElement(channel,'channel')
    for key,value in [('title','GC Subdomain Watch · public directory changes'),('link','https://coolcode.ca/gc-subdomain-watch/'),('description','Additions, removals and destination changes observed between published directory editions.')]:
        SubElement(inner,key).text=value
    for left,right in zip(reversed(editions[:-1]), reversed(editions[1:])):
        for name in sorted(left['rows'].keys() | right['rows'].keys()):
            a,b=left['rows'].get(name),right['rows'].get(name)
            if a==b:continue
            item=SubElement(inner,'item')
            SubElement(item,'title').text=name+' · '+('Added' if not a else 'Removed' if not b else 'Destination changed')
            link='https://coolcode.ca/gc-subdomain-watch/?'+urlencode({'from':left['date'],'to':right['date'],'q':name})
            SubElement(item,'link').text=link
            SubElement(item,'guid',isPermaLink='true').text=link
            SubElement(item,'description').text='Directory comparison '+left['date']+' to '+right['date']+'.'
    ElementTree(channel).write(ROOT/'web/changes.xml',encoding='utf-8',xml_declaration=True)
    print([(e['date'],len(e['rows'])) for e in editions], 'certificate summaries:', len(certificates))

if __name__ == '__main__':
    main()
