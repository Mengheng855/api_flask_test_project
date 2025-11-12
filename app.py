from flask import Flask,request,jsonify,session
from werkzeug.utils import secure_filename
import pymysql,os,jwt,time
from pymysql.cursors import DictCursor
from werkzeug.security import generate_password_hash,check_password_hash
app=Flask(__name__)
JWT_SECRET = 'asdfghjk234567890'
def generate_token(user_id,email,role):
    payload={
        'user_id':user_id,
        'email':email,
        'role':role,
        'exp': int(time.time()) + 86400
    }
    token=jwt.encode(payload,JWT_SECRET,algorithm='HS256')
    return token
def get_token_data():
    token = None
    
    if 'Authorization' in request.headers:
        auth_header = request.headers['Authorization']
        try:
            token = auth_header.split(" ")[1]
        except IndexError:
            return None
    
    if not token:
        return None
    
    try:
        data = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
        return data
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None
def get_db():
    return pymysql.connect(
        host='localhost',
        user='root',
        passwd='',
        db='db_flask_project_api'
    )
UPLOAD_FOLDER='static/images'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER']=UPLOAD_FOLDER
@app.route('/getUser')
def getUser():
    conn=get_db()
    cursor=conn.cursor(DictCursor)
    cursor.execute('SELECT * FROM tbl_user')
    data=cursor.fetchall()
    if data:
        return jsonify({
            'message':'getUser',
            'status':200,
            'data':data
        })
    else:
        return jsonify({
            'message':'do not have user',
            'status':200,
            'data':data
        })
@app.route('/getUser/<int:id>')
def gettUser(id):
    conn=get_db()
    cursor=conn.cursor(pymysql.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_user WHERE user_id=%s',(id))
    data=cursor.fetchall()
    if data:
        return jsonify({
            'message':'getUser',
            'status':200,
            'data':data
        })
    else:
        return jsonify({
            'message':'do not have this user',
            'status':200,
            'data':data
        })
@app.route('/register',methods=['POST'])
def register():
    username=request.form['username']
    email=request.form['email']
    password=generate_password_hash(request.form['password'])
    conn=get_db()
    cursor=conn.cursor()
    cursor.execute('INSERT INTO tbl_user (username,email,password) VALUES (%s,%s,%s)',(username,email,password))
    conn.commit()
    return jsonify({
        'message':'created',
        'status':200
    })  
@app.route('/login',methods=['POST'])
def login():
    email=request.form['email']
    password=request.form['password']
    if email and password:
        conn=get_db()
        cursor=conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute('SELECT user_id, email, password,role FROM tbl_user WHERE email=%s',(email))
        data=cursor.fetchone()
        if data:
            if check_password_hash(data['password'],password):
                token=generate_token(data['user_id'],data['email'],data['role'])
                if data['role']==1:
                    role_message='admin'
                else:
                    role_message='user'
                return jsonify({
                    'message':f'login successfuly, {role_message}',
                    'status':200,
                    'token':token,
                   
                })
            else:
                return jsonify({
                    'message':'Invalid password',
                    'status':401
                })
        else:
            return jsonify({
                'message':'Email not found',
                'status':404
            })
    else:
        return jsonify({
            'message':'Email and password required',
            'status':400
        })
@app.route('/addCategory',methods=['POST'])
def addCategory():
    token_data=get_token_data()
    if not token_data:
        return jsonify({
            'message':'Token is missing or invalid',
            'status':401,
        })
    if token_data['role']!=1:
        return jsonify({
            'message':'Only admin can add category',
            'status':401,
        })
    cate_name=request.form['cate_name']
    user_id=token_data['user_id']
    conn=get_db()
    cursor=conn.cursor()
    cursor.execute('INSERT INTO tbl_category (cate_name,user_id) VALUES (%s,%s)',(cate_name,user_id))
    conn.commit()
    return jsonify({
        'message':'added category',
        'status':201
    })
@app.route('/getCategory')
def getCategory():
    conn=get_db()
    cursor=conn.cursor(DictCursor)
    cursor.execute("""
        SELECT c.* , u.username FROM tbl_category c
        INNER JOIN tbl_user u
        ON c.user_id=u.user_id
        """)
    data=cursor.fetchall()
    return jsonify({
        'message':'success',
        'status':200,
        'data':data
    })
@app.route('/deleteCategory/<int:id>',methods=['DELETE'])
def deleteCategory(id):
    token_data=get_token_data()
    if not token_data:
        return jsonify({
            'message':'Token is missing or invalid',
            'status':401,
        })
    if token_data['role']!=1:
        return jsonify({
            'message':'Only admin can add category',
            'status':401,
        })
    conn=get_db()
    cursor=conn.cursor()
    cursor.execute('DELETE FROM tbl_category WHERE cate_id=%s',(id))
    conn.commit()
    return jsonify({
        'message':'deleted succesfully',
        'status':200
    })
@app.route('/editCategory/<int:id>',methods=['PATCH'])
def editCategory(id):
    token_data=get_token_data()
    if not token_data:
        return jsonify({
            'message':'Token is missing or invalid',
            'status':401,
        })
    if token_data['role']!=1:
        return jsonify({
            'message':'Only admin can add category',
            'status':401,
        })
    cate_name=request.form['cate_name']
    user_id=token_data['user_id']
    conn=get_db()
    cursor=conn.cursor()
    cursor.execute('UPDATE tbl_category SET cate_name=%s,user_id=%s',(cate_name,user_id))
    conn.commit()
    return jsonify({
        'message':'updated category',
        'status':200
    })
@app.route('/addRent',methods=['POST'])
def addRent():
    token_data=get_token_data()
    if not token_data:
        return jsonify({
            'message':'Token is missing or invalid',
            'status':401,
        })
    if token_data['role']!=1:
        return jsonify({
            'message':'Only admin can add category',
            'status':401,
        })
    user_id=token_data['user_id']
    cate_id=request.form['cate_id']
    price=request.form['price']
    des=request.form['description']
    image=request.files['image']
    if  image:
        filename=secure_filename(image.filename)
        filepath=os.path.join(app.config['UPLOAD_FOLDER'],filename)
        image.save(filepath)
        image_url=request.host_url.rstrip('/')+"/static/images/"+filename
    conn=get_db()
    cursor=conn.cursor()
    cursor.execute('INSERT INTO tbl_rent (price,description,image,cate_id,user_id) VALUES (%s,%s,%s,%s,%s)',(price,des,image_url,cate_id,user_id))
    conn.commit()
    return jsonify({
        'message':'rent added successfully',
        'status':201
    }) 

@app.route('/getRent')
def getRent():
    conn=get_db()
    cursor=conn.cursor(DictCursor)
    cursor.execute('''
        SELECT r.*, c.cate_name, u.username
        FROM tbl_rent r
        INNER JOIN tbl_user u ON r.user_id = u.user_id
        INNER JOIN tbl_category c ON r.cate_id = c.cate_id
        ''')
    data=cursor.fetchall()
    return jsonify({
        'message':'get rent',
        'status':200,
        'data':data
    })
@app.route('/deleteRent/<int:id>',methods=['DELETE'])
def deleteRent(id):
    token_data=get_token_data()
    if not token_data:
        return jsonify({
            'message':'Token is missing or invalid',
            'status':401,
        })
    if token_data['role']!=1:
        return jsonify({
            'message':'Only admin can add category',
            'status':401,
        })
    conn=get_db()
    cursor=conn.cursor()
    cursor.execute('DELETE FROM tbl_rent WHERE rent_id=%s',(id))
    conn.commit()
    return jsonify({
        'message':'deleted successfully',
        'status':200
    })
@app.route('/editRent/<int:id>',methods=['PATCH'])
def editRent(id):
    token_data=get_token_data()
    if not token_data:
        return jsonify({
            'message':'Token is missing or invalid',
            'status':401,
        })
    if token_data['role']!=1:
        return jsonify({
            'message':'Only admin can add category',
            'status':401,
        })
    user_id=token_data['user_id']
    cate_id=request.form.get('cate_id') 
    price=request.form.get('price') 
    des=request.form.get('description')
    image_url=None
    if 'image' in request.files:  
        image=request.files['image']
        if image.filename != '':  
            filename=secure_filename(image.filename)
            filepath=os.path.join(app.config['UPLOAD_FOLDER'],filename)
            image.save(filepath)
            image_url=request.host_url.rstrip('/')+"/static/images/"+filename
    conn=get_db()
    cursor=conn.cursor()
    if image_url:
            cursor.execute(
                'UPDATE tbl_rent SET price=%s, description=%s, image=%s, cate_id=%s, user_id=%s WHERE rent_id=%s',
                (price, des, image_url, cate_id, user_id, id) 
            )
    else:
        cursor.execute(
            'UPDATE tbl_rent SET price=%s, description=%s, cate_id=%s, user_id=%s WHERE rent_id=%s',
            (price, des, cate_id, user_id, id)  
        )    
    conn.commit()
    return jsonify({
        'message':'rent updated successfully',
        'status':201
    })
if (__name__)=="__main__":
    app.run(host='0.0.0.0', port=5000, debug=False)