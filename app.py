
import eventlet
eventlet.monkey_patch()

from flask import Flask, redirect,render_template,request,session
from flask_socketio import SocketIO, emit, send, join_room, leave_room
from functools import wraps
import threading
import re
import tools


app=Flask(__name__)
app.config['SECRET_KEY'] = 'this is five-in-a-row'
socketio = SocketIO(app)

rooms={
    # '1':{'id':'1','owner':'zzs1253','viewers':[],'mode':'5分','status':'等待中','white_player':'zzs1253','black_player':'','white_ready':False,'black_ready':False,'lock':'','white_time':300,'black_time':300,'chess_list':[]},
    # '2':{'id':'2','owner':'lsg5321','viewers':[],'mode':'5分','status':'等待中','white_player':'','black_player':'','white_ready':False,'black_ready':False,'lock':'','white_time':300,'black_time':300,'chess_list':[]}
}

users={
    # 'zzs1253':{'name':'zzs1253','all':0,'win':0,'tie':0,'fail':0,'which_room':'1'},
    # 'lsg5321':{'name':'lsg5321','all':5,'win':3,'tie':1,'fail':1,'which_room':'2'},
}


rooms_chess={
    # '1':{'id':'1','owner':'zzs1253','viewers':[],'mode':'5分','status':'等待中','white_player':'zzs1253','black_player':'','white_ready':False,'black_ready':False,'lock':'','white_time':300,'black_time':300,'chess_list':[]},
    # '2':{'id':'2','owner':'lsg5321','viewers':[],'mode':'5分','status':'等待中','white_player':'','black_player':'','white_ready':False,'black_ready':False,'lock':'','white_time':300,'black_time':300,'chess_list':[]}
}

users_chess={
    # 'zzs1253':{'name':'zzs1253','all':0,'win':0,'tie':0,'fail':0,'which_room':'1'},
    # 'lsg5321':{'name':'lsg5321','all':5,'win':3,'tie':1,'fail':1,'which_room':'2'},
}

def login_required(view_func):
    global users
    @wraps(view_func)
    def wrapped_view(**kwargs):
        current_user=session.get('current_user')
        if not current_user:
            return redirect('/login/')
        return view_func(**kwargs)
    return wrapped_view

def game_init(room_id):
    global rooms
    rooms[room_id]['status']="准备中"
    rooms[room_id]['white_player'],rooms[room_id]['black_player']=rooms[room_id]['black_player'],rooms[room_id]['white_player']
    rooms[room_id]['white_ready']=False
    rooms[room_id]['black_ready']=False
    rooms[room_id]['lock']=""
    rooms[room_id]['white_time']=300
    rooms[room_id]['black_time']=300
    rooms[room_id]['chess_list']=[]

def game_init_chess(room_id):
    global rooms_chess
    rooms_chess[room_id]['status']="准备中"
    rooms_chess[room_id]['white_player'],rooms_chess[room_id]['black_player']=rooms_chess[room_id]['black_player'],rooms_chess[room_id]['white_player']
    rooms_chess[room_id]['white_ready']=False
    rooms_chess[room_id]['black_ready']=False
    rooms_chess[room_id]['lock']=""
    rooms_chess[room_id]['white_time']=600
    rooms_chess[room_id]['black_time']=600
    rooms_chess[room_id]['chess_list']=tools.init_chessboard.copy()
    rooms_chess[room_id]['steps'].clear()

@socketio.on('connect')
def user_connect():
    global rooms,users,rooms_chess,users_chess
    user_name=session.get('current_user')
    referer=request.headers.get("Referer")
    if referer.find('chess')>-1:
        join_room('chess')
        
        # 处理中国象棋的连接
        current_user=users_chess.get(user_name)
        if not current_user:
            current_user={'name':user_name,'all':0,'win':0,'tie':0,'fail':0,'which_room':''}
            users_chess[user_name]=current_user
        if referer.find('lobby')>-1:
            emit('lobby_infos_chess',{'rooms':rooms_chess,'users':users_chess,'current_user':current_user},broadcast=False)
            emit('new_user_entered_lobby_chess',current_user,broadcast=True,room='chess')
        else:
            room_id=(re.compile("room_chess/(\d*?)/").findall(referer))[0]
            old_room=current_user['which_room']
            if old_room and room_id!=old_room:
                r=rooms_chess.get(old_room)
                if r.get("white_player")==user_name or r.get("black_player")==user_name:
                    emit('return_room_chess', old_room, broadcast=False)
                    return
                else:
                    user_leave_room_chess({'room':old_room,'user':current_user['name']})
            join_room("chess"+room_id)
            if current_user not in rooms_chess[room_id]['viewers']:
                rooms_chess[room_id]['viewers'].append(current_user)
                users_chess[user_name]["which_room"]=room_id
            user=current_user
            room=rooms_chess.get(room_id)
            emit('enter_room_chess',{"user":user,"room":room}, broadcast=True,room="chess"+room_id) # room页面进入
        pass
    else:
        join_room('five')
        # 处理五子棋的连接
        current_user=users.get(user_name)
        if not current_user:
            current_user={'name':user_name,'all':0,'win':0,'tie':0,'fail':0,'which_room':''}
            users[user_name]=current_user
        if referer.find('lobby')>-1:
            emit('lobby_infos',{'rooms':rooms,'users':users,'current_user':current_user},broadcast=False)
            emit('new_user_entered_lobby',current_user,broadcast=True)
        else:
            room_id=(re.compile("room/(\d*?)/").findall(referer))[0]
            old_room=current_user['which_room']
            if old_room and room_id!=old_room:
                r=rooms.get(old_room)
                if r.get("white_player")==user_name or r.get("black_player")==user_name:
                    emit('return_room', old_room, broadcast=False)
                    return
                else:
                    user_leave_room({'room':old_room,'user':current_user['name']})
            join_room(room_id)
            if current_user not in rooms[room_id]['viewers']:
                rooms[room_id]['viewers'].append(current_user)
                users[user_name]["which_room"]=room_id
            user=current_user
            room=rooms.get(room_id)
            emit('enter_room',{"user":user,"room":room}, broadcast=True,room=room_id) # room页面进入
        
@socketio.on('create_room')
def create_room(data):
    global rooms
    user=data.get('name')
    room_id=data.get('which_room')
    if room_id:
        exist_room=rooms.get(room_id)
        if exist_room.get('owner')==user:
            emit('enter_room', room_id, broadcast=False) # lobby页面进入
            return
    exist_flag=True
    room_id=(len(rooms))
    while exist_flag:
        room_id=(room_id+1)
        if not rooms.get(str(room_id)):
            exist_flag=False
    room_id=str(room_id)
    new_room={'id':room_id,'owner':user,'viewers':[],'mode':'5分','status':'等待中','white_player':'','black_player':'','white_ready':False,'black_ready':False,'lock':"",'white_time':300,'black_time':300,'chess_list':[],'not_score':False,'deny_undo_checkbox':False}
    rooms[room_id]=new_room
    users[user]['which_room']=room_id
    emit('room_has_been_created', new_room, broadcast=True)
    emit('enter_room', room_id, broadcast=False) # lobby页面进入

@socketio.on('create_room_chess')
def create_room_chess(data):
    global rooms_chess,users_chess
    user=data.get('name')
    room_id=data.get('which_room')
    if room_id:
        exist_room=rooms_chess.get(room_id)
        if exist_room.get('owner')==user:
            emit('enter_room_chess', room_id, broadcast=False) # lobby页面进入
            return
    exist_flag=True
    room_id=(len(rooms_chess))
    while exist_flag:
        room_id=(room_id+1)
        if not rooms_chess.get(str(room_id)):
            exist_flag=False
    room_id=str(room_id)
    new_room={'id':room_id,'owner':user,'viewers':[],'mode':'5分','status':'等待中','white_player':'','black_player':'','white_ready':False,'black_ready':False,'lock':"",'white_time':600,'black_time':600,'chess_list':tools.init_chessboard.copy(),'not_score':False,'deny_undo_checkbox':False,'steps':[]}
    rooms_chess[room_id]=new_room
    users_chess[user]['which_room']=room_id
    emit('room_has_been_created_chess', new_room, broadcast=True)
    emit('enter_room_chess', room_id, broadcast=False) # lobby页面进入

@socketio.on("change_room_setting")
def change_room_setting(data):
    global rooms
    room_id=data.get('room')
    not_score=data.get('not_score')
    deny_undo_checkbox=data.get('deny_undo_checkbox')
    time_select=data.get('time_select')
    rooms[room_id]['white_time']=time_select
    rooms[room_id]['black_time']=time_select
    rooms[room_id]['not_score']=not_score
    rooms[room_id]['deny_undo_checkbox']=deny_undo_checkbox
    emit('has_change_room_setting',{'not_score':not_score,'deny_undo_checkbox':deny_undo_checkbox,'time_select':time_select},broadcast=True,room=room_id)

@socketio.on("change_room_setting_chess")
def change_room_setting_chess(data):
    global rooms_chess
    room_id=data.get('room')
    not_score=data.get('not_score')
    deny_undo_checkbox=data.get('deny_undo_checkbox')
    time_select=data.get('time_select')
    rooms_chess[room_id]['white_time']=time_select
    rooms_chess[room_id]['black_time']=time_select
    rooms_chess[room_id]['not_score']=not_score
    rooms_chess[room_id]['deny_undo_checkbox']=deny_undo_checkbox
    emit('has_change_room_setting_chess',{'not_score':not_score,'deny_undo_checkbox':deny_undo_checkbox,'time_select':time_select},broadcast=True,room="chess"+room_id)

@socketio.on("chat")
def chat(data):
    room_id=data.get("room_id")
    msg=data.get("msg")
    emit('receive_chat_msg',msg,broadcast=True,room=room_id)

@socketio.on("chat_chess")
def chat_chess(data):
    room_id=data.get("room_id")
    msg=data.get("msg")
    emit('receive_chat_msg_chess',msg,broadcast=True,room="chess"+room_id)

@socketio.on("sit_down")
def sit_down(data):
    global rooms
    camp=data.get('camp')
    user=data.get('user')
    room_id=data.get('room')
    room=rooms.get(room_id)
    white_player=room.get("white_player")
    black_player=room.get("black_player")
    ready_symbol=False
    if camp=="white":
        if (white_player=="" or white_player==user) and black_player!=user:
            rooms[room_id]["white_player"]=user
            if black_player != "":
                ready_symbol=True
                rooms[room_id]["status"]="准备中"
            emit("select_camp",{"camp":"white","user":user,"ready_symbol":ready_symbol},broadcast=True,room=room_id)
    else:
        if (black_player=="" or black_player==user) and white_player!=user:
            rooms[room_id]["black_player"]=user
            if white_player != "":
                ready_symbol=True
                rooms[room_id]["status"]="准备中"
            emit("select_camp",{"camp":"black","user":user,"ready_symbol":ready_symbol},broadcast=True,room=room_id)

@socketio.on("sit_down_chess")
def sit_down_chess(data):
    global rooms_chess
    camp=data.get('camp')
    user=data.get('user')
    room_id=data.get('room')
    room=rooms_chess.get(room_id)
    white_player=room.get("white_player")
    black_player=room.get("black_player")
    ready_symbol=False
    if camp=="white":
        if (white_player=="" or white_player==user) and black_player!=user:
            rooms_chess[room_id]["white_player"]=user
            if black_player != "":
                ready_symbol=True
                rooms_chess[room_id]["status"]="准备中"
            emit("select_camp_chess",{"camp":"white","user":user,"ready_symbol":ready_symbol},broadcast=True,room="chess"+room_id)
    else:
        if (black_player=="" or black_player==user) and white_player!=user:
            rooms_chess[room_id]["black_player"]=user
            if white_player != "":
                ready_symbol=True
                rooms_chess[room_id]["status"]="准备中"
            emit("select_camp_chess",{"camp":"black","user":user,"ready_symbol":ready_symbol},broadcast=True,room="chess"+room_id)

@socketio.on("stand_up")
def stand_up(data):
    global rooms
    camp=data.get("camp")
    room_id=data.get("room")
    if camp=="white":
        rooms[room_id]["white_player"]=""
    else:
        rooms[room_id]["black_player"]=""
    emit("quit_camp",camp,broadcast=True,room=room_id)

@socketio.on("stand_up_chess")
def stand_up_chess(data):
    global rooms_chess
    camp=data.get("camp")
    room_id=data.get("room")
    if camp=="white":
        rooms_chess[room_id]["white_player"]=""
    else:
        rooms_chess[room_id]["black_player"]=""
    emit("quit_camp_chess",camp,broadcast=True,room="chess"+room_id)

@socketio.on("ready")
def ready(data):
    global rooms
    camp=data.get("camp")
    room_id=data.get("room")
    status="准备中"
    if camp=='white':
        rooms[room_id]['white_ready']=True
        if rooms[room_id]['black_ready']==True:
            status="游戏中"
            rooms[room_id]['status']=status
    else:
        rooms[room_id]['black_ready']=True
        if rooms[room_id]['white_ready']==True:
            status="游戏中"
            rooms[room_id]['status']=status
    if rooms[room_id]['status']=='游戏中':
        rooms[room_id]['lock']='black'
    emit('game_start',{"camp":camp,"status":status},broadcast=True,room=room_id)

@socketio.on("ready_chess")
def ready_chess(data):
    global rooms_chess
    camp=data.get("camp")
    room_id=data.get("room")
    status="准备中"
    if camp=='white':
        rooms_chess[room_id]['white_ready']=True
        if rooms_chess[room_id]['black_ready']==True:
            status="游戏中"
            rooms_chess[room_id]['status']=status
    else:
        rooms_chess[room_id]['black_ready']=True
        if rooms_chess[room_id]['white_ready']==True:
            status="游戏中"
            rooms_chess[room_id]['status']=status
    if rooms_chess[room_id]['status']=='游戏中':
        rooms_chess[room_id]['lock']='white'
    emit('game_start_chess',{"camp":camp,"status":status},broadcast=True,room="chess"+room_id)

@socketio.on('start_count_time')
def start_count_time(data):
    global rooms
    room_id=data.get('room')
    def count_timer():
        if rooms[room_id]['lock']=='white':
            rooms[room_id]['white_time']-=1
        else:
            rooms[room_id]['black_time']-=1
        timer=threading.Timer(1,count_timer)
        timer.start()
        if rooms[room_id]['white_time']==0 or rooms[room_id]['black_time']==0:
            game_init(room_id)
            if rooms[room_id]['white_time']==0:
                socketio.emit('game_over','black',broadcast=True,room=room_id)
            else:
                socketio.emit('game_over','white',broadcast=True,room=room_id)
            timer.cancel()
    count_timer()

@socketio.on('start_count_time_chess')
def start_count_time_chess(data):
    global rooms_chess
    room_id=data.get('room')
    def count_timer():
        if rooms_chess[room_id]['lock']=='white':
            rooms_chess[room_id]['white_time']-=1
        else:
            rooms_chess[room_id]['black_time']-=1
        timer=threading.Timer(1,count_timer)
        timer.start()
        if rooms_chess[room_id]['white_time']==0 or rooms_chess[room_id]['black_time']==0:
            game_init_chess(room_id)
            if rooms_chess[room_id]['white_time']==0:
                socketio.emit('game_over_chess','black',broadcast=True,room="chess"+room_id)
            else:
                socketio.emit('game_over_chess','white',broadcast=True,room="chess"+room_id)
            timer.cancel()
    count_timer()

@socketio.on('move')  
def move(data):
    global rooms
    room_id=data.get('room')
    chessboard=rooms[room_id]['chess_list']
    step=data.get('step')
    result=tools.can_move(chessboard,step)
    if result!=False:
        rooms[room_id]['chess_list'].append(step)
        emit('move',step,broadcast=True,room=room_id)
        eventlet.sleep(0.2)
        if result=='white' or result=='black':
            # 有玩家获胜，游戏初始化,双方交换阵营
            game_init(room_id)
            emit('game_over',result,broadcast=True,room=room_id)
        else:
            camp=step.get('camp')
            if camp=='white':
                rooms[room_id]['lock']='black'
            else:
                rooms[room_id]['lock']='white'


# 中国象棋算法更改
@socketio.on('move_chess')  
def move_chess(data):
    global rooms_chess
    room_id=data.get('room')
    chessboard=rooms_chess[room_id]['chess_list']
    camp=data.get('camp')
    step_from=data.get('from')
    step_to=data.get('to')
    result=tools.can_move_chess(chessboard,step_from,step_to)
    if result!=False:
        rooms_chess[room_id]['chess_list'][result['move_name']]={"name":result['move_name'],"x":step_to['x'],"y":step_to['y']}
        emit('move_chess',{'camp':camp,'move_name':result['move_name'],'from':step_from,'to':step_to,'died_chess':result['target']},broadcast=True,room="chess"+room_id)
        rooms_chess[room_id]['steps'].append({'move_name':result['move_name'],'from':step_from,'to':step_to,'died_chess':result['target']})
        eventlet.sleep(0.2)
        if result['target'] is not None:
            del rooms_chess[room_id]['chess_list'][result['target']]
        if result['target'] in ['k','K']:
            if result['target']=='k':
                emit('game_over_chess','white',broadcast=True,room="chess"+room_id)
            else:
                emit('game_over_chess','black',broadcast=True,room="chess"+room_id)
            game_init_chess(room_id)
        else:
            # 交换执行权
            if camp=='white':
                rooms_chess[room_id]['lock']='black'
            else:
                rooms_chess[room_id]['lock']='white'

@socketio.on('give_up')
def give_up(data):
    room_id=data.get('room')
    camp=data.get('camp')
    if camp=='white':
        result='black'
    else:
        result='white'
    emit('game_over',result,broadcast=True,room=room_id)
    game_init(room_id)

@socketio.on('give_up_chess')
def give_up_chess(data):
    room_id=data.get('room')
    camp=data.get('camp')
    if camp=='white':
        result='black'
    else:
        result='white'
    emit('game_over_chess',result,broadcast=True,room="chess"+room_id)
    game_init_chess(room_id)

@socketio.on('for_peace')
def for_peace(data):
    global room
    room_id=data.get('room')
    camp=data.get('camp')
    emit('ask_for_peace',camp,broadcast=True,room=room_id)

@socketio.on('for_peace_chess')
def for_peace_chess(data):
    room_id=data.get('room')
    camp=data.get('camp')
    emit('ask_for_peace_chess',camp,broadcast=True,room="chess"+room_id)

@socketio.on('peace_result')
def peace_result(data):
    room_id=data.get('room')
    emit('peace_result',data['result'],broadcast=True,room=room_id)
    if data['result']=='agree':
        game_init(room_id)
        emit('game_over','peace',broadcast=True,room=room_id)

@socketio.on('peace_result_chess')
def peace_result_chess(data):
    room_id=data.get('room')
    emit('peace_result_chess',data['result'],broadcast=True,room="chess"+room_id)
    if data['result']=='agree':
        game_init_chess(room_id)
        emit('game_over_chess','peace',broadcast=True,room="chess"+room_id)

@socketio.on('undo')
def undo(data):
    room_id=data.get('room')
    camp=data.get('camp')
    emit('ask_for_undo',camp,broadcast=True,room=room_id)

@socketio.on('undo_chess')
def undo_chess(data):
    room_id=data.get('room')
    camp=data.get('camp')
    emit('ask_for_undo_chess',camp,broadcast=True,room="chess"+room_id)

@socketio.on('undo_result')
def undo_result(data):
    global rooms
    room_id=data.get('room')
    if data['result']=='agree':
        del rooms[room_id]['chess_list'][-2:]
    emit('undo_result',data['result'],broadcast=True,room=room_id)

@socketio.on('undo_result_chess')
def undo_result_chess(data):
    global rooms_chess
    room_id=data.get('room')
    if data['result']=='agree':
        if len(rooms_chess[room_id]['steps'])>1:
            step1=rooms_chess[room_id]['steps'][-1]
            step2=rooms_chess[room_id]['steps'][-2]
            rooms_chess[room_id]['chess_list'][step1['move_name']]={'name':step1['move_name'],'x':step1['from']['x'],'y':step1['from']['y']}
            if step1.get('died_chess'):
                rooms_chess[room_id]['chess_list'][step1['died_chess']]={'name':step1['died_chess'],'x':step1['to']['x'],'y':step1['to']['y']}
            rooms_chess[room_id]['chess_list'][step2['move_name']]={'name':step2['move_name'],'x':step2['from']['x'],'y':step2['from']['y']}
            if step2.get('died_chess'):
                rooms_chess[room_id]['chess_list'][step2['died_chess']]={'name':step2['died_chess'],'x':step2['to']['x'],'y':step2['to']['y']}
            del rooms_chess[room_id]['steps'][-2:]
    emit('undo_result_chess',{'result':data['result'],'chess_list':rooms_chess[room_id]['chess_list']},broadcast=True,room="chess"+room_id)

@socketio.on('leave_room')
def user_leave_room(data):
    global rooms,users
    room_id=data.get('room')
    user=data.get('user')
    if rooms[room_id]['status']=='游戏中':
        if user==rooms[room_id]['white_player']:
            game_init(room_id)
            emit('game_over','black',broadcast=True,room=room_id)
            rooms[room_id]['white_player']=""
        elif user==rooms[room_id]['black_player']:
            game_init(room_id)
            emit('game_over','white',broadcast=True,room=room_id)
            rooms[room_id]['black_player']=""
    # 如何减少服务器压力
    for viewer in rooms[room_id]['viewers']:
        if viewer['name']==user:
            rooms[room_id]['viewers'].remove(viewer)
    leave_room(room_id)
    users[user]['which_room']=""
    if len(rooms[room_id]['viewers'])>0:
        if user==rooms[room_id]['owner']:
            new_owner=rooms[room_id]['viewers'][0]['name']
            rooms[room_id]['owner']=new_owner # 房主退出之后，把列表第一个观众设为房主
            emit('receive_chat_msg',user+"离开了房间",broadcast=True,room=room_id)
            emit('receive_chat_msg',new_owner+"成为了房主",broadcast=True,room=room_id)
        else:
            emit('receive_chat_msg',user+"离开了房间",broadcast=True,room=room_id)
        if user == rooms[room_id]['white_player']:
            rooms[room_id]['white_player']=""
        if user == rooms[room_id]['black_player']:
            rooms[room_id]['black_player']=""
        emit('has_been_leave_room',{'user':user,'owner':rooms[room_id]['owner']},broadcast=True,room=room_id)
    else:
        del rooms[room_id]
        emit('delete_room',room_id,broadcast=True,room='five')

@socketio.on('leave_room_chess')
def user_leave_room_chess(data):
    global rooms_chess,users_chess
    room_id=data.get('room')
    user=data.get('user')
    if rooms_chess[room_id]['status']=='游戏中':
        if user==rooms_chess[room_id]['white_player']:
            game_init_chess(room_id)
            emit('game_over_chess','black',broadcast=True,room="chess"+room_id)
            rooms_chess[room_id]['white_player']=""
        elif user==rooms_chess[room_id]['black_player']:
            game_init_chess(room_id)
            emit('game_over_chess','white',broadcast=True,room="chess"+room_id)
            rooms_chess[room_id]['black_player']=""
    # 如何减少服务器压力
    for viewer in rooms_chess[room_id]['viewers']:
        if viewer['name']==user:
            rooms_chess[room_id]['viewers'].remove(viewer)
    leave_room('chess'+room_id)
    users_chess[user]['which_room']=""
    if len(rooms_chess[room_id]['viewers'])>0:
        if user==rooms_chess[room_id]['owner']:
            new_owner=rooms_chess[room_id]['viewers'][0]['name']
            rooms_chess[room_id]['owner']=new_owner # 房主退出之后，把列表第一个观众设为房主
            emit('receive_chat_msg_chess',user+"离开了房间",broadcast=True,room="chess"+room_id)
            emit('receive_chat_msg_chess',new_owner+"成为了房主",broadcast=True,room="chess"+room_id)
        else:
            emit('receive_chat_msg_chess',user+"离开了房间",broadcast=True,room="chess"+room_id)
        if user == rooms_chess[room_id]['white_player']:
            rooms_chess[room_id]['white_player']=""
        if user == rooms_chess[room_id]['black_player']:
            rooms_chess[room_id]['black_player']=""
        emit('has_been_leave_room_chess',{'user':user,'owner':rooms_chess[room_id]['owner']},broadcast=True,room="chess"+room_id)
    else:
        del rooms_chess[room_id]
        emit('delete_room_chess',room_id,broadcast=True,room='chess')


@app.route('/')
def index():
    # return redirect('/login/')
    return render_template('index.html')

@app.route('/login/')
def login():
    return render_template('login.html')

@app.route('/register/')
def register():
    return render_template('register.html')

@app.route('/passwd/')
def passwd():
    return render_template('passwd.html')

@app.route('/lobby/')
@login_required
def lobby():
    return render_template('lobby.html')

@app.route('/lobby_chess/')
@login_required
def lobby_chess():
    return render_template('lobby_chess.html')


@app.route('/visitor_check/')
def visitor_check():
    global users
    referer=request.headers.get("Referer")
    visitor=session.get('current_user')
    if not visitor:
        visitor=tools.new_visitor(users)
        session['current_user']=visitor
    if not users.get(visitor):
        users[visitor]={'name':visitor,'all':0,'win':0,'tie':0,'fail':0,'which_room':''}
    if referer.find('lobby')>-1:
        return redirect(referer)
    return redirect('/')

@app.route('/room/<int:room_id>/')
@login_required
def room(room_id):
    return render_template('room.html')

@app.route('/room_chess/<int:room_id>/')
@login_required
def room_chess(room_id):
    return render_template('room_chess.html')

if __name__ == '__main__':
    socketio.run(app,debug=True,host="0.0.0.0")