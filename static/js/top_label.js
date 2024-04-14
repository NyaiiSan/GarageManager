// 创建一个顶部栏
var top_label = document.createElement('div');
top_label.id = 'top_label';
top_label.innerHTML = `
<div class="top_side">
    <a class="top_fun" href="/">主页</a>
    <a class="top_fun" href="/parking">车库状态</a>
    <a class="top_fun" href="/user">我的信息</a>
    <a class="top_fun" href="/wallet">我的钱包</a>
</div>
<div class="top_side">
    <a id="login" class="top_fun" href="/login">登录</a>
    <a id="signup" class="top_fun" href="javascript: alert('请联系管理员完成注册');">注册</a>
</div>
`

document.body.insertBefore(top_label, document.body.firstChild);

// 向服务器验证登录
fetch('/user/verify', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json'
    }
})
.then(response => response.json())
.then(data => {
    username = data['name'];
    if (username == 'guest'){
        login = document.getElementById('login');
        signup = document.getElementById('signup');
        login.innerHTML = '登录';
        signup.innerHTML = '注册';
        login.href = '/login';
        signup.href = 'javascript: alert("请联系管理员完成注册");';
    }else{
        login = document.getElementById('login');
        signup = document.getElementById('signup');
        login.innerHTML = username;
        signup.innerHTML = "注销";
        signup.href = "/logout";
    }
});
