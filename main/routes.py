from flask import request, render_template, redirect, url_for, session, flash
import pandas as pd
from .database.models import *
from .app import app
from sqlalchemy import asc
from .decorators import requires_auth, get_candidates
from .redis import get_cached_data_or_fetch
from flask_minify import decorators as minify_decorators



@app.route('/', methods=['GET', 'POST'])
@minify_decorators.minify(html=True, js=True, cssless=True)
def home():
    candidates = None
    candidate = None
    presidential_candidates = []
    party_members = []
    form_id = None
    form_url = "/"
    config_queryset = db.session.query(Config).first()
    config = config_queryset.json()
    data = get_data()
    candidate_type = data[0]['candidate_type']
    
    if candidate_type == 'national' and request.method == 'GET':
        form_id = 'National'
        presidential_candidates, party_members, code = get_cached_data_or_fetch(form_id, db, candidate_type)

        candidate_query = f"""
            SELECT * FROM candidates
            WHERE {code} = :form_id
            AND candidate_type = :candidate_type
            LIMIT 1
        """
        params = {'form_id': form_id, "candidate_type": candidate_type}
        candidate_result = db.session.execute(candidate_query, params)
        candidate = candidate_result.fetchone()

    if request.method == 'POST' and request.form['ds_id'] is not None:
        form_id = request.form['ds_id']
        candidate_type = request.form['candidate_type']
        candidates, code = get_candidates(form_id, db, candidate_type)

        party_orderno_count = {}
        for item in candidates:
            party = item['party']
            orderno = item['orderno']
            
            if orderno == '1':
                # Check if this is the first candidate with orderno = '1' for this party
                if party not in party_orderno_count:
                    party_orderno_count[party] = 1
                    presidential_candidates.append(item)
                else:
                    party_orderno_count[party] += 1
                    if party_orderno_count[party] == 2:
                        party_members.append(item)
                    else:
                        presidential_candidates.append(item)
            else:
                party_members.append(item)
        candidate_query = f"""
            SELECT * FROM candidates
            WHERE {code} = :form_id
            AND candidate_type = :candidate_type
            LIMIT 1
        """
        params = {'form_id': form_id, "candidate_type": candidate_type}
        candidate_result = db.session.execute(candidate_query, params)
        candidate = candidate_result.fetchone()
    
    party_members = sorted(party_members, key=lambda x: int(x['orderno']))
        
    return render_template(
            'home.html', 
            candidates=party_members,
            presidential_candidates=presidential_candidates,
            candidate = candidate,
            ward=form_id, 
            form_url=form_url,
            data = data,
            config=config,
            area_name = candidate_type,
            domain = request.url_root
        )

@app.route('/insights', methods=['GET', 'POST'])
def insights():
    config_queryset = db.session.query(Config).first()
    config = config_queryset.json()
    return render_template(
            'insights.html',
            config=config,
            domain = request.url_root)
