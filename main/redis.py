import redis, json, os, pandas as pd
from .decorators import get_candidates
from .app import app


redis_url = app.config['REDIS_URL']
redis_client = redis.StrictRedis.from_url(redis_url, ssl_cert_reqs=None)
# redis_client.delete('cached_candidates')

def sort_data(candidates):
    presidential_candidates = []
    party_members = []
    # Sort alphabetically
    df = pd.DataFrame(candidates)
    sorted_df = df.sort_values(by='party')
    candidates = sorted_df.to_dict(orient='records')

    for item in candidates:
        if item['orderno'] == '1':
            presidential_candidates.append(item)
        else:
            party_members.append(item)

    return presidential_candidates, party_members


def get_cached_data_or_fetch(form_id, db, candidate_type):
    cached_data = redis_client.get('cached_candidates')
    if cached_data:
        data = json.loads(cached_data)
        return data["candidates"]["presidential"], data["candidates"]["party_members"], data["code"]
    else:
        candidates, code = get_candidates(form_id, db, candidate_type)
        presidential_candidates, party_members = sort_data(candidates)
        # Cache the fetched data for future requests
        data_to_cache = {
            'candidates': {
                'presidential': presidential_candidates, 
                'party_members': party_members
                }, 
            'code': code
        }
        redis_client.set('cached_candidates', json.dumps(data_to_cache))
        redis_client.expire('cached_candidates', 86400)  # Cache for 24 hours
        return presidential_candidates, party_members, code