function sign_out() {
    $.removeCookie('mytoken', {path: '/'}); // path : 경로설정이다. 이 사이트의 모든 페이지가 해당된다면 / 이렇게 슬러시만 둔다. 그렇지 않고 특정 폴더라면 경로를 넣으면 된다.
}