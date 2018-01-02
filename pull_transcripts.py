from time import sleep
import requests
from bs4 import BeautifulSoup

EPISODES_URL = 'http://paw-patrol.wikia.com/wiki/Episodes'
BASE_URL = 'http://paw-patrol.wikia.com'
TRANSCRIPT_URL = '/Transcript'

def grab_episodes():
    resp = requests.get(EPISODES_URL)
    soup = BeautifulSoup(resp.text, 'html.parser')
    links = soup.find_all('a')
    links = [link for link in links if set(link.attrs.keys()) == set(['href', 'title'])]
    episodes = [(link['title'], link['href']) for link in links]
    return list(set(episodes))

def pull_transcript(episode):
    url = BASE_URL + episode[1] + TRANSCRIPT_URL
    resp = requests.get(url)
    soup = BeautifulSoup(resp.text, 'html.parser')
    transcript = soup.find('table', {'id': 'transcript_table'})
    if transcript is not None:
        with open('transcripts/{}.csv'.format(episode[0].replace(' ', '_')), 'w') as file_open:
            for tr in transcript.find_all('tr'):
                transcript_time = tr.find('td').text.split()[0]
                speaker = ' '.join(tr.find('td').text.split()[1:])
                speaker = speaker.split(':')[0]
                line = tr.find_all('td')[-1].text.strip()
                file_open.write(transcript_time + '|' + speaker + '|' + line + '\n')

    else:
        print('No transcript for {}'.format(episode[0]))


def pull_transcripts():
    episodes = grab_episodes()
    for episode in episodes:
        pull_transcript(episode)
        sleep(1)
        
if __name__ == '__main__':
    pull_transcripts()
    #episode = ('Mission Paw: Quest for the Crown', '/wiki/Mission_PAW:_Quest_for_the_Crown')
    #pull_transcript(episode)