from django.shortcuts import render
from django.shortcuts import redirect
from django.http import HttpResponse
from django.http import JsonResponse
import base64
import pandas as pd
import MySQLdb as mysql
from math import ceil, isnan
from sklearn import linear_model
from sklearn import preprocessing
# Create your views here.

MYSQL_HOST = "localhost"
MYSQL_USER = "root"
MYSQL_PASS = "1234"
MYSQL_DB = "Recommender"

#--- Check Trip_type, Companion ---#
def check_input(trip_type, companion):
    check_type = ["business", "leisure", None]
    check_com = ["solo", "couple", "friend", "family", None]
    ok = True
    try:
        check_type.remove(trip_type)
    except:
        ok = False
        print("trip_type is not valid")
    try:
        check_com.remove(companion)
    except:
        ok = False
        print("companion is not valid")
    return ok

#---Part preprocessing ---#
def check_case(target_id, trip_type, companion, db):
    user_data = pd.read_sql("select * from ratings", con=db).drop('id', axis=1)
    group_user = user_data.drop('hotel_name', axis=1)
    target_user = group_user.loc[group_user['user_id'] == target_id]
    if len(target_user) == 0:
        print("target_user is not valid")
    else:
        other_user = group_user.loc[group_user['user_id'] != target_id]

        if (trip_type == None) & (companion == None):
            status = [0, "case_none"]
            data_out = get_main(target_id, target_user,
                                other_user, trip_type, companion, status[0])
            del data_out['others']
            return data_out, status[1]
        else:
            num_target = len(target_user.loc[(target_user['trip_type'] == trip_type) & (
                target_user['companion'] == companion)])
            if num_target >= 6:
                status = [1, "case_pass_regr"]
                data_out = get_main(target_id, target_user,
                                    other_user, trip_type, companion, status[0])
                del data_out['others']
                return data_out, status[1]
            else:
                # no data regression
                status = [-1, "case_not_regr"]
                data_out = get_main(target_id, target_user,
                                    other_user, trip_type, companion, status[0])
                data_out, buff_data = re_get_main(
                    data_out, target_id, user_data, trip_type, companion)
                del data_out['others']
                return data_out, status[1]

def get_main(target_id, target, other, trip_type, companion, status):
    if status == 1:
        target = target.loc[(target['trip_type'] == trip_type)
                            & (target['companion'] == companion)]
    elif (status == -1) | (status == 0):
        pass
    target_weight = get_weight(target)
    target_rank = get_rank_weight(target_weight)
    group_user = {}
    result = {}
    other_user = other['user_id'].drop_duplicates(keep='first')
    other_user = other_user.values.tolist()
    for data in other_user:
        user = other.loc[other['user_id'] == data]
        other_weight = get_weight(user)
        other_rank = get_rank_weight(other_weight)
        result.update({data: [other_weight, other_rank]})
    group_user.update({'target': {target_id: [target_weight, target_rank]}})
    group_user.update({'others': result})
    #--- Make Neighbors ---#
    group_user_rank = cal_corr(target_id, group_user)
    data_out = get_neighbor(group_user_rank)
    return data_out
    # {
    # 'target': {'user_id': [weight, rank_f]},
    # 'others': {'user_id': [weight, rank_f]},
    # 'neighbors': [[user_id], [corr]]
    # }

#--- Cal Regression ---#
def get_weight(df):
    # weight of ['price', 'near_station', 'restaurant', 'entertain',
    # 'shopping_mall', 'convenience_store']
    x = df[['price', 'near_station', 'restaurant', 'entertain',
            'shopping_mall', 'convenience_store']].values.tolist()
    y = df['rating'].values.tolist()
    # Create linear regression object
    regr = linear_model.LinearRegression(fit_intercept=False)
    # http://stackoverflow.com/questions/24393518/python-sklearn-linear-model-linearregression-working-weird
    regr.fit(x, y)
    return regr.coef_

def get_rank_weight(weight):
    rank = pd.Series(list(weight)).rank(ascending=False)
    rank_f = rank.values.tolist()
    return rank_f

#--- Cal Spearman's Rank ---#
def cal_corr(target_id, group_user_rank):
    target = pd.Series(group_user_rank['target'][target_id][1])
    others = sorted(list(group_user_rank['others'].keys()))
    list_user = []
    list_corr = []
    for user in others:
        other = pd.Series(group_user_rank['others'][user][1])
        corr = target.corr(other, method='spearman')
        list_user.append(user)
        list_corr.append(corr)
    result = [list_user, list_corr]
    group_user_rank.update({'neighbors': result})
    return group_user_rank

#--- Before recommendation ---#
def get_neighbor(group_user_rank):
    corr = pd.Series(group_user_rank['neighbors'][1]).rank(ascending=True)
    neighbor = corr.values.tolist()
    group_user_rank['neighbors'].append(neighbor)
    return group_user_rank

#--- Solve case not regression ---#
def re_get_main(data_main, target_id, user_data, trip_type, companion):
    target_data = user_data.loc[(user_data['user_id'] == target_id) & (
        user_data['trip_type'] == trip_type) & (user_data['companion'] == companion)]
    other_id = data_main['neighbors'][0]
    other_rank = data_main['neighbors'][2]
    neighbors = pd.DataFrame({'user_id': other_id, 'rank': other_rank})
    neighbors = neighbors.sort_values(by=('rank'), ascending=True)
    list_neighbors = neighbors['user_id'].values.tolist()

    buff_data = target_data
    rows_t = len(target_data)
    for other in list_neighbors:
        #--- Expect each user: 10 records ---#
        # pass regression
        if len(buff_data) >= 6:
            break

        # filter trip_type, companion each other user
        other_data = user_data.loc[(user_data['user_id'] == other) & (
            user_data['trip_type'] == trip_type) & (user_data['companion'] == companion)]
        rows_o = len(other_data)
        supply = 6 - rows_t
        if (rows_o == 0):
            continue
        else:
            if rows_o < supply:
                sup_data = other_data[:rows_o + 1]
            else:
                sup_data = other_data[:supply + 1]
        buff_data = buff_data.append(sup_data)

    # recalculate
    new_weight = get_weight(buff_data)
    new_rank = get_rank_weight(new_weight)
    data_main['target'][target_id] = [new_weight, new_rank]
    data_out = cal_corr(target_id, data_main)
    data_out = get_neighbor(data_out)
    return data_out, buff_data

#--- Part recommendation ---#
def prediction_rating(dataset, data_frame, **kwargs):
    data_frame = weight_neighbors(data_frame)
    data_rec = pd.DataFrame()
    neighbors = list(data_frame['user_id'])
    # print('Bug ties data: {}'.format(neighbors))

    if (kwargs['trip_type'] is None) & (kwargs['companion'] is None):
        for neighbor in neighbors:
            if len(data_rec) > 20:
                break

            result = dataset.ix[dataset['user_id'] == neighbor, [
                'user_id', 'hotel_name', 'rating', 'trip_type', 'companion']]
            data_rec = data_rec.append(result)
    else:
        for neighbor in neighbors:
            if len(data_rec) > 20:
                break
            try:
                result = dataset.ix[(dataset['user_id'] == neighbor) & (dataset['trip_type'] == kwargs['trip_type']) & (
                    dataset['companion'] == kwargs['companion']), ['user_id', 'hotel_name', 'rating', 'trip_type', 'companion']]
            except:
                pass
            data_rec = data_rec.append(result)

    data_rec = pd.merge(data_rec.drop(
        ['trip_type', 'companion'], axis=1), data_frame, how='inner', on='user_id')
    groups = data_rec.groupby('hotel_name')
    result1 = []
    result2 = []
    for hotel, group in groups:
        predict_rating = group.apply(lambda row: (
            row.loc['weight'] * row.loc['rating']) / group['weight'].sum(), axis=1).sum()
        result1.append(hotel)
        result2 .append(predict_rating)
    hotel_rec = pd.DataFrame(
        data={'hotel_name': result1, 'predict_rating': result2})
    return hotel_rec

def recommendation(target_id, data_rec, top_k):
    topk_hotels = data_rec.sort_values(
        by=('predict_rating'), ascending=False).head(top_k)
    return topk_hotels['hotel_name']

def weight_neighbors(data_frame):
    scale = preprocessing.MinMaxScaler(feature_range=(0.1, 1))
    data_frame['weight'] = scale.fit_transform(data_frame[['weight']])
    return data_frame

# err 0 => no error
# err 1 => not login
def index(request, err=0):
    return render(request, 'index.html', {
        'err': err,
    })

def search(request):
    #--- Read data ---#
    user = request.session.get('user')
    if user == None:
        return index(request, 1)

    # --- Get parameters ---#
    db = mysql.connect(MYSQL_HOST, MYSQL_USER, MYSQL_PASS, MYSQL_DB)
    cursor = db.cursor()
    des = request.GET.get('des')
    trip_type = request.GET.get('triptype')
    companion = request.GET.get('companion')
    page = request.GET.get('page')
    sort = request.GET.get('sort')
    fprice = request.GET.get('fprice')
    frate = request.GET.get('frate')
    stars = request.GET.get('stars')
    district = request.GET.get('district')

    order = 'rating'
    filter_price = ""
    filter_rate = ""
    filter_stars = ""
    filter_district = ""

    if sort == 'l2hr':
        order = 'rating'
    elif sort == 'h2lr':
        order = 'rating desc'
    elif sort == 'l2hp':
        order = 'price'
    elif sort == 'h2lp':
        order = 'price desc'

    if fprice != None:
        filter_price = " and price<=" + fprice
    if frate != None:
        filter_rate = " and rating<=" + frate
    if stars != None:
        filter_stars = " and stars<=" + stars
    if district != None:
        filter_district = " and district=\"" + district + "\""
    if des == None:
        des = 'Tokyo'

    if page == None:
        page = 1
    else:
        page = int(page)
    if sort == None:
        sort = 'h2lr'
    target_id = user
    print target_id
    context = {'trip_type': trip_type, 'companion': companion}
    top_k = 9
    ok = check_input(trip_type, companion)
    list_rec = []
    if ok:
        print target_id, trip_type, companion
        data_in = pd.read_sql("select * from ratings where province = '"+des+"'", con=db).drop('id', axis=1)
        data_out, status = check_case(target_id, trip_type, companion, db)
        data_out = {'user_id': data_out['neighbors'][
            0], 'weight': data_out['neighbors'][2]}
        data_out = pd.DataFrame(data=data_out).sort_values(
            by=('weight'), ascending=False)
        #--- Recommendation ---#
        data_rec = prediction_rating(data_in, data_out, **context)
        list_rec = recommendation(target_id, data_rec, top_k)

    cursor.execute('select count(*) from hotels where destination="'+des+"\""+filter_price+filter_rate+filter_stars+filter_district)
    items = float(cursor.fetchone()[0])
    pages = ceil(items/6)
    count = 0
    hotels_all = []
    hotels_rec = []

    # Select filtered hotels to show in corresponds page
    try:
        if page < 3:
            if pages > 4:
                showpages = [i for i in range(1, 6)]
            else:
                showpages = [i for i in range(1, int(pages)+1)]
        elif page > pages-2:
            if pages > 4:
                showpages = [i for i in range(int(pages)-4, int(pages)+1)]
            else:
                showpages = [i for i in range(1, int(pages)+1)]
        else:
            showpages = [i for i in range(page-2, page+3)]

        hotels = pd.read_sql("select * from hotels where destination=\""+des+"\""+filter_price+filter_rate+filter_stars+filter_district+" order by " + order, con=db)
        if page == pages:
            last = int(items)
        else:
            last = (page-1) * 6 + 6
        for i in range((page-1)*6, last):
            this = hotels.values[i]
            cursor.execute("select image from hotel_images where hotel_name=\""+this[1]+"\"")
            img = cursor.fetchone()
            if img == None:
                img = ['']
            img = img[0]
            for j in range(len(this)):
                if str(this[j]) == 'nan':
                    this[j] = 0.0
            # count += 1
            hotels_all.append({
                'name': this[1],
                'rating': this[12],
                'price': this[13],
                'stars': this[9],
                'image': base64.b64encode(img),
            })
    except:
        showpages = [1]
        page = 1

    # Get hotels from recommender and calculate 3 adventages of hotels
    for k in list_rec:
        try:
            this = pd.read_sql("select * from hotels where destination=\""+des+"\" and name=\""+k+"\"", con=db)
            this = this.values[0].tolist()
            adv = pd.read_sql("select price_comp, near_station, restaurant, entertain, shopping_mall, convenience_store from hotels where destination=\""+des+"\" and name=\""+k+"\"", con=db)
            adv = adv.append({'price_comp':0, 'near_station':1, 'restaurant':2, 'entertain':3, 'shopping_mall':4, 'convenience_store':5}, ignore_index=True)
            adv = adv.transpose().sort_values(0, axis=0, ascending=False).transpose().values[1].tolist()
            adv = [adv[0], adv[1], adv[2]]
            cursor.execute("select image from hotel_images where hotel_name=\""+k+"\"")
            img = cursor.fetchone()
            if len(img) == 0:
                img = ''
            else:
                img = img[0]
            for j in range(len(this)):
                if str(this[j]) == 'nan':
                    this[j] = 0.0
            hotels_rec.append({
                'name': this[1],
                'rating': this[12],
                'price': this[13],
                'stars': this[9],
                'image': base64.b64encode(img),
                'adventages': adv,
            })
        except Exception as e:
            print k
            print e
            hotels_rec.append({
                'name': k + '(no data)',
                'rating': 0.0,
                'price': 0.0,
                'stars': -1.0,
                'image': '',
                'adventages': [-1, -1, -1],
            })
    cursor.execute("select distinct district from hotels where destination=\""+des+"\"")
    district = [x[0] for x in cursor.fetchall()]
    db.close()

    return render(request, 'search.html', {
        'showpages': showpages,
        'pages': pages,
        'page': page,
        'hotels_all': hotels_all,
        'hotels_rec': hotels_rec,
        'district': district,
        'price': fprice,
        'stars': stars,
        'district': district,
        'rating': frate,
        'next_page': page+1,
        'prev_page': page-1,
    })

def signin(request):
    user = request.GET.get('uname')
    pwd= request.GET.get('password')

    db = mysql.connect(MYSQL_HOST, MYSQL_USER, MYSQL_PASS, MYSQL_DB)
    uname = pd.read_sql('select * from users where username="'+str(user)+'" and password ="'+str(pwd)+'";', con=db)
    db.close()
    if len(uname.values) == 0:
       return HttpResponse('incorrect')
    request.session['user'] = uname.values[0][0]
    return HttpResponse('correct')

def signup(request):
    username = request.POST.get('uname')
    password = request.POST.get('password')
    print username, password

    db = mysql.connect(MYSQL_HOST, MYSQL_USER, MYSQL_PASS, MYSQL_DB)
    cursor = db.cursor()
    cursor.execute('select * from users where username="'+username+'"')
    if cursor.fetchone() != None:
        return HttpResponse('exists')
    cursor.execute('insert into users (username, password) values ("'+str(username)+'","'+str(password)+'");')
    db.commit()
    db.close()

    return HttpResponse('success')

def signout(request):
   try:
      del request.session['user']
   except:
      pass
   return redirect(request.META.get('HTTP_REFERER', '/'))
