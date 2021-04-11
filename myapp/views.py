from flask import request, redirect, url_for, render_template, flash, session
from flask_paginate import Pagination, get_page_parameter
from myapp import app
from elasticsearch import Elasticsearch
import os
import re

@app.route('/')
def show_entries():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return redirect(url_for('show_results'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != app.config['USERNAME']:
            flash('ユーザ名が異なります')
        elif request.form['password'] != app.config['PASSWORD']:
            flash('パスワードが異なります')
        else:
            session['logged_in'] = True
            flash('ログインしました')
            return redirect(url_for('show_entries'))
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('ログアウトしました')
    return redirect(url_for('show_entries'))

@app.route('/result', methods=['GET', 'POST'])
def show_results():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    if 'request_form' not in session:
            session['request_form'] = {}
    if request.method == 'POST':
        session['request_form'] = request.form
    request.form = session['request_form']

    es = Elasticsearch()
    body = {
        "query" : {
            "bool": {
                "must": [
                ],
                "filter": [
                ],
            }
        },
        "sort":[
        ],
        "highlight": {
            "fields": {
                "content": {}
            }
        }
    }

    get_word = request.form.get('search_word')
    if get_word:
        if not re.match("^\".*\"$", get_word):
            body['query']['bool']['must'].append(
                {
                    "bool": {
                        "should": [
                            {
                                "match": {
                                    "content": {
                                        "query": get_word,
                                        "operator": "and"
                                    }
                                }
                            },
                            {
                                "match": {
                                    "title": {
                                        "query": get_word,
                                        "operator": "and"
                                    }
                                }
                            }
                        ]
                    }
                }
            )
        else:
            k_words = re.findall("\".*?\"", get_word)
            k_words = [i.strip("\"") for i in k_words]
            print(k_words)
            for k_word in k_words:
                k_word = "*" + k_word + "*" 
                body['query']['bool']['must'].append(
                    { 
                        "bool": {
                            "should": [
                                { "wildcard": { "title.keyword": k_word } },
                                { "wildcard": { "content.keyword": k_word } }
                            ]
                        }
                    }
                )

    kws = ["title", "country", "organization", "source"]
    for kw in kws:
        if request.form.get(kw):
            body['query']['bool']['must'].append(
                {"match": {kw: request.form.get(kw)}}
            )

    if request.form.get('number_min'):
        body['query']['bool']['filter'].append(
            { 
                "range": { 
                    "number": { "gte": request.form.get('number_min') } 
                } 
            }
        )

    if request.form.get('number_max'):
        body['query']['bool']['filter'].append(
            { 
                "range": { 
                    "number": { "lte": request.form.get('number_max') } 
                } 
            }
        )

    body['sort'].append(
        { 
            "number": { 
                "order":  "asc"
            } 
        }
    )

    print(body)

    result = es.search(index='fuel_research', body=body, size=1000)

    result_num = result['hits']['total']['value']
    fuel_researches = result['hits']['hits']

    page_disp_msg = '表示範囲 <b>{start}件 - {end}件 </b> 合計：<b>{total}</b>件'
    page = request.args.get(get_page_parameter(), type=int, default=1)
    per_page = 1
    res = fuel_researches[(page-per_page)*per_page: page*per_page]
    pagination = Pagination(page=page, total=len(fuel_researches), per_page=per_page, css_framework='bootstrap4')

    return render_template('index.html', result_num=result_num, books=res, request_form=request.form, pagination=pagination)
