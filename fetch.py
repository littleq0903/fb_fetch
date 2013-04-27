import facebook
import urllib2
from pprint import PrettyPrinter
import json
import time
import thread
from accesstoken import *

""" initialize Pprint Printer """

pp = PrettyPrinter(indent=2, depth=2)
pprint = pp.pprint




ma19_page = '118250504903757'
tsaieng_page = '46251501064'
#PAGE_ID = tsaieng_page
PAGE_ID = ma19_page

## doesn't matter
COMMENT_GET_URL = 'https://graph.facebook.com/118250504903757_138587616203379/comments?access_token=306890979329593|Ynlw53_3jWp5RF9RbhLEzCz00ZA&limit=25&offset=25&__after_id=118250504903757_138587616203379_1049914'
some_post_id = '118250504903757_138587616203379'

## doesn't matter
def openurl(url):
    return_dict = lambda url: json.loads(urllib2.urlopen(url).read())
    try:
        rtn = return_dict(url)
    except urllib2.HTTPError:
        time.sleep(5)
        rtn = openurl(url)
    
    return rtn


def get_all_data(first_data, oid):
    """
    data:
        []
    paging:
        next
        previous
    """
    data = {
            'data': [],
            }
    while 1:
        data['data'] += first_data['data']

        no_paging = not first_data.has_key('paging')
        if no_paging: break
        no_next = not first_data['paging'].has_key('next')
        if no_next: break

        first_data = openurl(first_data['paging']['next'])

    print 'get totally %s data from %s' % (len(data['data']), oid)

    return data


def get_connections(oid, connection_type, limit=500, offset=0, access_token=None):
    url = 'https://graph.facebook.com/{0}/{1}?access_token={2}&limit={3}&offset={4}'.format(oid, connection_type, access_token, limit, offset)

    response = openurl(url)
    all_data = get_all_data(response, oid)

    return all_data

def get_comment_user_ids(data):
    return map(lambda x: x['from']['id'], data['data'])

def get_like_user_ids(data):
    return map(lambda x: x['id'], data['data'])
    

## get  
def get_attended_user(some_post_id, new_access_token):

    comments = get_connections(some_post_id, 'comments', 1000, 0, new_access_token)
    likes = get_connections(some_post_id, 'likes', 10000, 0, new_access_token)

    activeusers = get_comment_user_ids(comments) + get_like_user_ids(likes)
    activeusers = list(set(activeusers))
    return activeusers

def get_all_posts(page_id, new_access_token):
    take_post_id = lambda x: x['id']
    posts = get_connections(page_id, 'posts', 1000, 0, new_access_token)
    return posts['data']
    

def run_multithread_tasks(num_threaded, posts_ids, revoke_token_interval):

    token_interval_counter = 0

    def run_thread(thread_name):
        global result
        global new_access_token

        while posts_ids:
            target_post = posts_ids.pop()
            print "%s: deal with %s" % (thread_name, target_post)
            attended_users = get_attended_user(target_post, new_access_token)

            result += attended_users

    def check_thread():
        print "Remaining: {0}, Result: {1}".format(len(posts_ids), len(result))

    for n in range(num_threaded):
        thread.start_new_thread(run_thread, ("Thread-%s"%n, ))
    
    while posts_ids:
        time.sleep(5)
        check_thread()
        token_interval_counter += 1
        if token_interval_counter > revoke_token_interval:
            token_interval_counter = 0
            new_access_token = facebook.get_app_access_token(APP_ID, APP_SECRET)



if __name__ == '__main__':
    result = []
    new_access_token = facebook.get_app_access_token(APP_ID, APP_SECRET)
    posts = get_all_posts(PAGE_ID, new_access_token)

    def kill_useless_key(data):
        post_keys = [ u'from',  u'privacy', u'shares',  u'updated_time', u'likes',  u'created_time', u'message',  u'type', u'id',  u'status_type', u'comments']
        useful_keys = ['from', 'likes', 'id', 'comments', 'top10_comments', 'message', 'updated_time']

        try:
            del data['likes']['data']
        except:
            print 'deleting likes failed'

        try:
            del data['comments']['data']
        except:
            print 'deleting comments failed'


        for key in data.keys():
            if key not in useful_keys:
                del data[key]

    map(kill_useless_key, posts)

    pprint(posts)

    top10_likemost_posts = sorted(posts, key=lambda x: x['likes']['count'] if x.has_key('likes') else 0, reverse=True)[:10]
    top10_commentmost_posts = sorted(posts, key=lambda x:x['comments']['count'] if x.has_key('comments') else 0, reverse=True)[:10]


    def embed_top10_likemost_comments(data):
        post_id = data['id']
        its_comments = get_connections(post_id, 'comments', access_token=new_access_token)
        sorted_likemost_comments = sorted(its_comments['data'], key=lambda x: x if x.has_key('likes') else 0, reverse=True)
        top_10_sorted_likemost_comments = sorted_likemost_comments[0:10]
        map(kill_useless_key, top_10_sorted_likemost_comments)
        data['top10_comments'] = top_10_sorted_likemost_comments
        
    map(embed_top10_likemost_comments, top10_likemost_posts)
    map(embed_top10_likemost_comments, top10_commentmost_posts)

        
    pprint(embed_top10_likemost_comments)

    result = {
            'top10_likemost_posts': top10_likemost_posts,
            'top10_commentmost_posts': top10_commentmost_posts
            }




    import json
    json_string = json.dumps(result)


    with open('./data/top10_posts.json', 'w') as fp:
        fp.write(json_string)

    print 'done'



      
    



    #print 'Totally {0} posts'.format(len(post_ids))

    #print len(list(set(post_ids)))

    #run_multithread_tasks(20, post_ids, 1000)
"""
    result = list(set(result))

    with open('active_ids.txt', 'w') as new_fp:
        new_fp.write('\n'.join(result))
    print 'done'
"""
