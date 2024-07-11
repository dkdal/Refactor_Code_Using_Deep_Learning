import requests
import csv
def download_data_file_from_seart(file_type, **kwargs)->bool:
    '''Download data file from SEART'''

    url = f'https://seart-ghs.si.usi.ch/api/r/download/{file_type}?'
    for k, v in kwargs.items():
        if url[-1] != '?':
            url += '&'
        url += str(k) + '=' + str(v)
    r = requests.get(url, verify=False, timeout=60)

    if r.status_code != 200:
        print(f'Error {r.status_code} when downloading data file from SEART')
        return False
    
    with open(f'./data/result.{file_type}', 'wb') as f:
        f.write(r.content)
    return True

def fetch_java_repositories(min_stars=50, min_commits=500):
    api_url = "https://api.github.com/search/repositories"
    params = {
        'q': f'language:java stars:>={min_stars} forks:>={min_commits}',
        'sort': 'stars',
        'order': 'desc',
        'per_page': 1000  # Maximum items per page
    }

    repositories = []

    while True:
        response = requests.get(api_url, params=params)

        if response.status_code == 200:
            data = response.json()
            items = data.get('items', [])
            print(items[0])
            for repo in items:
                repositories.append({
                    'Name': repo['name'],
                    'FullName': repo['full_name'],
                        'URL': repo['html_url'],
                        'Stars': repo['stargazers_count'],
                        'Commits': repo['size']
                })

            if 'Link' in response.headers:
                links = response.headers['Link'].split(', ')
                for link in links:
                    url, rel = link.split('; ')
                    if 'rel="next"' in rel or 'rel="last"' in rel:
                        api_url = url.strip('<>')
                        break
            else:
                break
        else:
            print(f"Error: {response.status_code}")
            break

    return repositories

def write_to_csv(repositories, filename='java_repositories.csv'):
    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        fieldnames = ['Name', 'FullName', 'URL', 'Stars', 'Commits']
        writer = csv.DictWriter(file, fieldnames=fieldnames)

        writer.writeheader()
        writer.writerows(repositories)

if __name__=='__main__':
    download_data_file_from_seart('json', nameEquals=False,language="Java",commitsMin=5000,contributorsMin=2,issuesMin=1,pullsMin=1,
                                  committedMin="2023-12-24",committedMax="2024-01-21",starsMin=2000,forksMin=10)