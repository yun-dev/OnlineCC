import random
s=list('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ')

def new_visitor(users):
    global s
    flag=True
    while flag:
        visitor=''
        for i in range(3):
            visitor+=random.choice(s)
        for j in range(4):
            visitor+=str(random.randint(0,9))
        if not users.get(visitor):
            flag=False
    return visitor

def can_move(chessboard,step):
    # step={"camp":"black","x":6,"y":5}
    xx=step.get('x')-1
    yy=step.get('y')-1
    view_board=[([None]*15) for i in range(15) ]
    for i in chessboard:
        camp=i.get('camp')
        x=i.get('x')
        y=i.get('y')
        if camp=="black":
            view_board[x-1][y-1]='black'
        else:
            view_board[x-1][y-1]='white'

    if view_board[xx][yy] is None:
        if step['camp']=="black":
            view_board[xx][yy]='black'
        else:
            view_board[xx][yy]='white'
        # 开始判断输赢
        # 横向判断

        for i in range(15):
            for j in range(11):
                if view_board[i][j]==view_board[i][j+1]==view_board[i][j+2]==view_board[i][j+3]==view_board[i][j+4]!=None:
                    return view_board[i][j]
        # 竖向判断
        for i in range(11):
            for j in range(15):
                if view_board[i][j]==view_board[i+1][j]==view_board[i+2][j]==view_board[i+3][j]==view_board[i+4][j]!=None:
                    return view_board[i][j]
        # 左斜向判断 /
        for i in range(11):
            for j in range(4,15):
                if view_board[i][j]==view_board[i+1][j-1]==view_board[i+2][j-2]==view_board[i+3][j-3]==view_board[i+4][j-4]!=None:
                    return view_board[i][j]
        # 右斜向判断 \
        for i in range(11):
            for j in range(11):
                if view_board[i][j]==view_board[i+1][j+1]==view_board[i+2][j+2]==view_board[i+3][j+3]==view_board[i+4][j+4]!=None:
                    return view_board[i][j]
        return True
    return False

# 象棋初始棋盘
initing_chessboard=[
        ['r1','h1','e1','m1','k','m2','e2','h2','r2'],
        [None,None,None,None,None,None,None,None,None],
        [None,'c1',None,None,None,None,None,'c2',None],
        ['p1',None,'p2',None,'p3',None,'p4',None,'p5'],
        [None,None,None,None,None,None,None,None,None],
        [None,None,None,None,None,None,None,None,None],
        ['P1',None,'P2',None,'P3',None,'P4',None,'P5'],
        [None,'C1',None,None,None,None,None,'C2',None],
        [None,None,None,None,None,None,None,None,None],
        ['R1','H1','E1','M1','K','M2','E2','H2','R2']
    ]

init_chessboard={'r1':{'name':'r1','x':1,'y':1},'h1':{'name':'h1','x':2,'y':1},'e1':{'name':'e1','x':3,'y':1},'m1':{'name':'m1','x':4,'y':1},'k':{'name':'k','x':5,'y':1},
        'm2':{'name':'m2','x':6,'y':1},'e2':{'name':'e2','x':7,'y':1},'h2':{'name':'h2','x':8,'y':1},'r2':{'name':'r2','x':9,'y':1},'c1':{'name':'c1','x':2,'y':3},
        'c2':{'name':'c2','x':8,'y':3},'p1':{'name':'p1','x':1,'y':4},'p2':{'name':'p2','x':3,'y':4},'p3':{'name':'p3','x':5,'y':4},'p4':{'name':'p4','x':7,'y':4},
        'p5':{'name':'p5','x':9,'y':4},
        'P1':{'name':'P1','x':1,'y':7},'P2':{'name':'P2','x':3,'y':7},'P3':{'name':'P3','x':5,'y':7},'P4':{'name':'P4','x':7,'y':7},'P5':{'name':'P5','x':9,'y':7},
        'C1':{'name':'C1','x':2,'y':8},'C2':{'name':'C2','x':8,'y':8},'R1':{'name':'R1','x':1,'y':10},'H1':{'name':'H1','x':2,'y':10},'E1':{'name':'E1','x':3,'y':10},
        'M1':{'name':'M1','x':4,'y':10},'K':{'name':'K','x':5,'y':10},'M2':{'name':'M2','x':6,'y':10},'E2':{'name':'E2','x':7,'y':10},'H2':{'name':'H2','x':8,'y':10},
        'R2':{'name':'R2','x':9,'y':10}
    }
    
def can_move_chess(chessboard,step_from,step_to):
    # from {'x': 5, 'y': 4}      to: {'x': 5, 'y': 5}
    #  return false 不符合规则 ，  return None 符合，无死亡   ，return target (棋子名字) 符合，有死亡 
    view_board=[([None]*9) for i in range(10) ]
    for i in chessboard:
        item=chessboard[i]
        view_board[item['y']-1][item['x']-1]=item['name']
    x_from=step_from['x']-1
    y_from=step_from['y']-1
    x_to=step_to['x']-1
    y_to=step_to['y']-1
    name=view_board[y_from][x_from]
    print('要移动的棋子：',name)
    print('x_from:%d,y_from:%d,x_to:%d,y_to:%d'%(x_from,y_from,x_to,y_to))
    if name in ['r1','r2','R1','R2']:
        if rook_move(view_board,x_from,y_from,x_to,y_to)!=False:
            target=view_board[y_to][x_to]
            return {'target':target,'move_name':name}
    elif name in ['h1','h2','H1','H2']:
        if horse_move(view_board,x_from,y_from,x_to,y_to):
            target=view_board[y_to][x_to]
            return {'target':target,'move_name':name}
    elif name in ['e1','e2','E1','E2']:
        if elephant_move(view_board,name,x_from,y_from,x_to,y_to):
            target=view_board[y_to][x_to]
            return {'target':target,'move_name':name}
    elif name in ['m1','m2','M1','M2']:
        if mandarin_move(view_board,name,x_from,y_from,x_to,y_to):
            target=view_board[y_to][x_to]
            return {'target':target,'move_name':name}
    elif name in ['k','K']:
        if king_move(view_board,name,x_from,y_from,x_to,y_to):
            target=view_board[y_to][x_to]
            return {'target':target,'move_name':name}
    elif name in ['c1','c2','C1','C2']:
        if cannon_move(view_board,x_from,y_from,x_to,y_to):
            target=view_board[y_to][x_to]
            return {'target':target,'move_name':name}
    elif name in ['p1','p2','p3','p4','p5','P1','P2','P3','P4','P5']:
        if pawn_move(view_board,name,x_from,y_from,x_to,y_to):
            target=view_board[y_to][x_to]
            return {'target':target,'move_name':name}
    print('不能这样走')
    return False

def rook_move(view_board,x_from,y_from,x_to,y_to):
    if x_from!=x_to and y_from!=y_to:
        return False
    if x_from==x_to:
        x=x_from
        if  abs(x_from-x_to)!=1:
            for y in range(min(y_from,y_to)+1,max(y_from,y_to)):
                if view_board[y][x]:
                    return False
    if y_from==y_to:
        y=y_from
        if  abs(x_from-x_to)!=1:
            for x in range(min(x_from,x_to)+1,max(x_from,x_to)):
                if view_board[y][x]:
                    return False

def horse_move(view_board,x_from,y_from,x_to,y_to):
    if abs(x_from-x_to)==1:
        # e f g h
        if y_from-y_to==2:
            if view_board[y_from-1][x_from] is None:
                return True
        if y_to-y_from==2:
            if view_board[y_from+1][x_from] is None:
                return True
    if abs(y_from-y_to)==1:
        # a b c d
        if x_from-x_to==2:
            if view_board[y_from][x_from-1] is None:
                return True
        if x_to-x_from==2:
            if view_board[y_from][x_from+1] is None:
                return True

def elephant_move(view_board,name,x_from,y_from,x_to,y_to):
    if abs(x_from-x_to)==2 and abs(y_from-y_to)==2:
        if name in ['e1','e2']:
            if (x_to,y_to) in [(0,2),(2,0),(2,4),(4,2),(6,0),(6,4),(8,2)]:
                if view_board[int((y_from+y_to)*0.5)][int((x_from+x_to)*0.5)] is None:
                    return True
        else:
            if (x_to,y_to) in [(0,7),(2,5),(2,9),(4,7),(6,5),(6,9),(8,7)]:
                if view_board[int((y_from+y_to)*0.5)][int((x_from+x_to)*0.5)] is None:
                    return True

def mandarin_move(view_board,name,x_from,y_from,x_to,y_to):
    if abs(x_from-x_to)==1 and abs(y_from-y_to)==1:
        if name in ['m1','m2']:
            if (x_to,y_to) in [(3,0),(5,0),(4,1),(3,2),(5,2)]:
                return True
        else:
            if (x_to,y_to) in [(3,7),(5,7),(4,8),(3,9),(5,9)]:
                return True

def king_move(view_board,name,x_from,y_from,x_to,y_to):
    if (abs(x_from-x_to)==1 and y_from-y_to==0) or (x_from-x_to==0 and abs(y_from-y_to)==1):
        if name=='k':
            if (x_to,y_to) in [(3,0),(3,1),(3,2),(4,0),(4,1),(4,2),(5,0),(5,1),(5,2)]:
                return True
        else:
            if (x_to,y_to) in [(3,7),(3,8),(3,9),(4,7),(4,8),(4,9),(5,7),(5,8),(5,9)]:
                return True
    if view_board[y_from][x_from] in ['k','K'] and view_board[y_to][x_to] in ['k','K']:
        if x_from==x_to:
            count=0
            for y in range(min(y_from,y_to)+1,max(y_from,y_to)):
                if view_board[y][x_from]:
                    count+=1
            if count==0:
                return True

def cannon_move(view_board,x_from,y_from,x_to,y_to):
    if x_from==x_to:
        x=x_from
        count=0
        for y in range(min(y_from,y_to)+1,max(y_from,y_to)):
            if view_board[y][x]:
                count+=1
        if count==0:
            if not view_board[y_to][x_to]:
                return True
        if count==1:
            if view_board[y_to][x_to]:
                return True
    if y_from==y_to:
        y=y_from
        count=0
        for x in range(min(x_from,x_to)+1,max(x_from,x_to)):
            if view_board[y][x]:
                count+=1
        if count==0:
            if not view_board[y_to][x_to]:
                return True
        if count==1:
            if view_board[y_to][x_to]:
                return True

def pawn_move(view_board,name,x_from,y_from,x_to,y_to):
    if name in ['p1','p2','p3','p4','p5']:
        # 黑方小兵
        if y_from<5:
            if x_from==x_to and y_to-y_from==1:
                return True
        else:
            if (x_from-x_to in [1,-1] and y_from==y_to) or (x_from==x_to and y_to-y_from==1):
                return True
    else:
        # 红方小兵
        if y_from>4:
            if x_from==x_to and y_from-y_to==1:
                return True
        else:
            if (x_from-x_to in [1,-1] and y_from==y_to) or (x_from==x_to and y_from-y_to==1):
                return True
