function start_login(){
    var login_logo=document.getElementById('login_logo')
    var login_input=document.getElementById('login_input')
    if(login_input.className.indexOf('undisplay')>-1){
        document.getElementById('login_input').classList.remove('undisplay')
        document.getElementById('login_logo').classList.add('undisplay')
    }else{
        document.getElementById('login_input').classList.add('undisplay')
        document.getElementById('login_logo').classList.remove('undisplay')
    }
}

function switch_module(name){
    var chat_block=document.getElementById('chat_block');
    var chess_manual_block=document.getElementById('chess_manual_block');
    var users_block=document.getElementById('users_block');
    var setting_block=document.getElementById('setting_block');
    var chat_block_btn=document.getElementById('chat_block_btn');
    var chess_manual_block_btn=document.getElementById('chess_manual_block_btn');
    var users_block_btn=document.getElementById('users_block_btn');
    var setting_block_btn=document.getElementById('setting_block_btn');
    switch(name){
        case 'chat':
            chat_block.classList.remove('undisplay');
            chess_manual_block.classList.add('undisplay');
            users_block.classList.add('undisplay');
            setting_block.classList.add('undisplay');
            chat_block_btn.classList.add('is-active');
            chess_manual_block_btn.classList.remove('is-active');
            users_block_btn.classList.remove('is-active');
            setting_block_btn.classList.remove('is-active');
            break;
        case 'chess':
            chat_block.classList.add('undisplay');
            chess_manual_block.classList.remove('undisplay');
            users_block.classList.add('undisplay');
            setting_block.classList.add('undisplay');
            chat_block_btn.classList.remove('is-active');
            chess_manual_block_btn.classList.add('is-active');
            users_block_btn.classList.remove('is-active');
            setting_block_btn.classList.remove('is-active');
            break;
        case 'users':
            chat_block.classList.add('undisplay');
            chess_manual_block.classList.add('undisplay');
            users_block.classList.remove('undisplay');
            setting_block.classList.add('undisplay');
            chat_block_btn.classList.remove('is-active');
            chess_manual_block_btn.classList.remove('is-active');
            users_block_btn.classList.add('is-active');
            setting_block_btn.classList.remove('is-active');
            break;
        case 'setting':
            chat_block.classList.add('undisplay');
            chess_manual_block.classList.add('undisplay');
            users_block.classList.add('undisplay');
            setting_block.classList.remove('undisplay');
            chat_block_btn.classList.remove('is-active');
            chess_manual_block_btn.classList.remove('is-active');
            users_block_btn.classList.remove('is-active');
            setting_block_btn.classList.add('is-active');
            break;
        default:
            break;
    }
}

 function close_modal(){
    document.getElementById("modal").classList.add('undisplay')
 }

 function scroll() {  
    if(window.pageYOffset != null) { 
        return {
            left: window.pageXOffset,
            top: window.pageYOffset
        }
    }
    else if(document.compatMode === "CSS1Compat") { 
        return {
            left: document.documentElement.scrollLeft,
            top: document.documentElement.scrollTop
        }
    }
    return { 
        left: document.body.scrollLeft,
        top: document.body.scrollTop
    }
}