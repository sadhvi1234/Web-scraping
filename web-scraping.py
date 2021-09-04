#!/usr/bin/env python
# coding: utf-8

# # Top Repositories For Github Topics

# In[1]:


# Execute this to save new versions of the notebook
jovian.commit(project="web-scraping")


# ## Objective
# 
# - Browse through different sites and pick on to scrape. Check the "Project Ideas" section for inspiration.
# - Identify the information you'd like to scrape from the site. Decide the format of the output CSV file.
# - Summarize your project idea and outline your strategy in a Juptyer notebook. Use the "New" button above.
# 

# ### Project outline
# 
# - I am going to scrape https://github.com/topics
# - First get a list of topics. For each topic we will get a topic title, topic page URL, and topic description.
# - For each topic, we'll get top 25 repositories in the topic from the topic page.
# - For each repository, we'll grab the repo name, username, stars and repo URL.
# - For each topic, we'll create a CSV file.

# ## Use the requests library to download web pages

# In[2]:


get_ipython().system('pip install requests --upgrade --quiet')


# In[3]:


import requests


# In[4]:


topics_url = 'https://github.com/topics'


# In[5]:


response = requests.get(topics_url)


# In[6]:


response.status_code


# In[7]:


page_contents = response.text


# In[8]:


page_contents[:1000]


# In[9]:


with open('webpage.html', 'w') as f:
    f.write(page_contents)


# ## Here Beautiful Soup is uded to parse and extract information

# In[10]:


get_ipython().system('pip install beautifulsoup4 --upgrade --quiet')


# In[11]:


from bs4 import BeautifulSoup


# In[12]:


doc = BeautifulSoup(page_contents, 'html.parser')


# In[13]:


# finding all p tags
selection_class = 'f3 lh-condensed mb-0 mt-1 Link--primary'
topic_title_tags = doc.find_all('p', {'class' : selection_class})


# In[14]:


len(topic_title_tags) # total topic tags


# In[15]:


topic_title_tags[:5] # top 5 tags


# In[16]:


desc_selector = 'f5 color-text-secondary mb-0 mt-1'
topic_desc_tags = doc.find_all('p', {'class': desc_selector})


# In[17]:


topic_desc_tags[:5]


# In[ ]:


# 


# In[18]:


topic_title_tag0 = topic_title_tags[0]


# In[19]:


div_tag = topic_title_tag0.parent


# In[20]:


topic_link_tags = doc.find_all('a', {'class': 'd-flex no-underline'})


# In[21]:


len(topic_link_tags)


# In[22]:


topic0_url = "https://github.com"+topic_link_tags[0]['href']
print(topic0_url)


# In[23]:


#topic_title_tag0.parent.parent (didn't work)


# In[24]:


topic_titles=[]

for tag in topic_title_tags:
    topic_titles.append(tag.text)
    
print(topic_titles)


# In[25]:


topic_descs=[]

for tag in topic_desc_tags:
    topic_descs.append(tag.text.strip())
    
print(topic_descs[:5])


# In[26]:


topic_urls=[]
base_url = 'https://github.com'

for tag in topic_link_tags:
    topic_urls.append(base_url + tag['href'])
    
topic_urls   


# In[27]:


get_ipython().system('pip install pandas --quiet')


# In[28]:


import pandas as pd


# In[29]:


topics_dict={
    'title':topic_titles,
    'description':topic_descs,
    'url':topic_urls
}


# In[30]:


#topics_dict


# In[31]:


topics_df = pd.DataFrame(topics_dict)


# In[32]:


#topics_df


# ## Create CSV file(s) with the extracted information

# In[33]:


topics_df.to_csv('topics.csv', index = None)


# ## Getting information out of a topic page

# In[34]:


topic_page_url = topic_urls[0]


# In[35]:


topic_page_url


# In[36]:


response = requests.get(topic_page_url)


# In[37]:


response.status_code


# In[38]:


len(response.text)


# In[39]:


topic_doc = BeautifulSoup(response.text, 'html.parser')


# In[40]:


h1_selection_class = 'f3 color-text-secondary text-normal lh-condensed'
repo_tags = topic_doc.find_all('h1', {'class': h1_selection_class} )


# In[41]:


repo_tags


# In[42]:


len(repo_tags)


# In[43]:


a_tags = repo_tags[0].find_all('a')


# In[44]:


a_tags[0].text.strip()


# In[45]:


a_tags[1].text.strip()


# In[46]:


base_url = 'https://github.com'
repo_url = base_url + a_tags[1]['href']
print(repo_url)


# In[47]:


star_tags = topic_doc.find_all('a', { 'class': 'social-count float-none'})


# In[48]:


len(star_tags)


# In[49]:


star_tags[0].text.strip()


# In[50]:


def parse_star_count(stars_str):
    stars_str = stars_str.strip()
    if stars_str[-1] == 'k':
        return int(float(stars_str[:-1]) * 1000)
    return int(stars_str)


# In[51]:


parse_star_count(star_tags[0].text.strip())


# In[52]:


def get_repo_info(h1_tag, star_tag):
    # returns all the required info about a repository
    a_tags = h1_tag.find_all('a')
    username = a_tags[0].text.strip()
    repo_name = a_tags[1].text.strip()
    repo_url =  base_url + a_tags[1]['href']
    stars = parse_star_count(star_tag.text.strip())
    return username, repo_name, stars, repo_url


# In[53]:


get_repo_info(repo_tags[0], star_tags[0])


# In[54]:


topic_repos_dict = {
    'username': [],
    'repo_name': [],
    'stars': [],
    'repo_url': []
}


for i in range(len(repo_tags)):
    repo_info = get_repo_info(repo_tags[i], star_tags[i])
    topic_repos_dict['username'].append(repo_info[0])
    topic_repos_dict['repo_name'].append(repo_info[1])
    topic_repos_dict['stars'].append(repo_info[2])
    topic_repos_dict['repo_url'].append(repo_info[3])


# ## FINAL CODE

# In[62]:


import os

def get_topic_page(topic_url):
    
    # download the page
    response = requests.get(topic_url)    
    # check successful response
    if response.status_code != 200:
        raise Exception('Failed to load page {}'.format(topic_url))
    # Parse using Beautiful soup
    topic_doc = BeautifulSoup(response.text, 'html.parser')
    return topic_doc

def get_repo_info(h1_tag, star_tag):
    # returns all the required info about a repository
    a_tags = h1_tag.find_all('a')
    username = a_tags[0].text.strip()
    repo_name = a_tags[1].text.strip()
    repo_url =  base_url + a_tags[1]['href']
    stars = parse_star_count(star_tag.text.strip())
    return username, repo_name, stars, repo_url

def get_topic_repos(topic_doc):
    # Get the h1 tags containing repo title, repo URL and username
    h1_selection_class = 'f3 color-text-secondary text-normal lh-condensed'
    repo_tags = topic_doc.find_all('h1', {'class': h1_selection_class} )
    # Get star tags
    star_tags = topic_doc.find_all('a', { 'class': 'social-count float-none'})
    
    topic_repos_dict = {
        'username': [], 
        'repo_name': [], 
        'stars': [],
        'repo_url': []
    }

    # Get repo info
    for i in range(len(repo_tags)):
        repo_info = get_repo_info(repo_tags[i], star_tags[i])
        topic_repos_dict['username'].append(repo_info[0])
        topic_repos_dict['repo_name'].append(repo_info[1])
        topic_repos_dict['stars'].append(repo_info[2])
        topic_repos_dict['repo_url'].append(repo_info[3])
        
    return pd.DataFrame(topic_repos_dict)


def scrape_topic(topic_url, path):
    if os.path.exists(path):
        print("The file {} already exists. Skipping...".format(path))
        return
    topic_df = get_topic_repos(get_topic_page(topic_url))
    topic_df.to_csv(path, index=None)


# Write a single function to :
# 1. Get the list of topics from the topics page
# 2. Get the list of top repos from the individual topic pages
# 3. For each topic, create a CSV of the top repos for the topic
# 
# 

# In[68]:


import os
help(os.makedirs)


# In[63]:


def get_topic_titles(doc):
    selection_class = 'f3 lh-condensed mb-0 mt-1 Link--primary'
    topic_title_tags = doc.find_all('p', {'class': selection_class})
    topic_titles = []
    for tag in topic_title_tags:
        topic_titles.append(tag.text)
    return topic_titles

def get_topic_descs(doc):
    desc_selector = 'f5 color-text-secondary mb-0 mt-1'
    topic_desc_tags = doc.find_all('p', {'class': desc_selector})
    topic_descs = []
    for tag in topic_desc_tags:
        topic_descs.append(tag.text.strip())
    return topic_descs

def get_topic_urls(doc):
    topic_link_tags = doc.find_all('a', {'class': 'd-flex no-underline'})
    topic_urls = []
    base_url = 'https://github.com'
    for tag in topic_link_tags:
        topic_urls.append(base_url + tag['href'])
    return topic_urls
    

def scrape_topics():
    topics_url = 'https://github.com/topics'
    response = requests.get(topics_url)
    if response.status_code != 200:
        raise Exception('Failed to load page {}'.format(topic_url))
    topics_dict = {
        'title': get_topic_titles(doc),
        'description': get_topic_descs(doc),
        'url': get_topic_urls(doc)
    }
    return pd.DataFrame(topics_dict)


# In[64]:


def scrape_topics_repos():
    print('Scraping list of topics')
    topics_df = scrape_topics()
    
    os.makedirs('data', exist_ok=True)
    for index, row in topics_df.iterrows():
        print('Scraping top repositories for "{}"'.format(row['title']))
        scrape_topic(row['url'], 'data/{}.csv'.format(row['title']))


# In[65]:


scrape_topics_repos()


# In[ ]:





# In[69]:


import jovian


# In[71]:


jovian.commit()


# ## Documentation 

# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:




