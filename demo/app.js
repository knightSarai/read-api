const API_URL = 'http://localhost:8000';

async function login() {
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;

    try {
        const response = await fetch(`${API_URL}/api/auth/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ username, password })
        });
        const data = await response.json();
        localStorage.setItem('user', JSON.stringify(data));
        getUser();
    } catch (error) {
        console.log(error);
    }

}

async function getUser() {
    const user = JSON.parse(localStorage.getItem('user'));
    if (!user?.token) {
        alert('You are not logged in');
        return;
    }

    try {
        const response = await fetch(`${API_URL}/api/auth/me`, {
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Token ${user.token}`
            }
        })
        const data = await response.json();
        const h1 = document.querySelector('h1');
        h1.innerHTML = `Hello ${data.username}`;
    } catch (error) {
        console.log(error);
    }
}

async function logout() {
    const user = JSON.parse(localStorage.getItem('user'));
    if (!user?.token) {
        alert('You are not logged in');
        return;
    }

    try {
        await fetch(`${API_URL}/api/auth/logout/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Token ${user.token}`
            }
        })
    } catch (error) {
        console.log(error);
    }

    localStorage.removeItem('user');
    const h1 = document.querySelector('h1');
    h1.innerHTML = 'Anonymous User'; 
}

async function checkAuth() {
    const user = JSON.parse(localStorage.getItem('user'));
    if (!user?.token) {
        return;
    }

    getUser();
}

const loginBtn = document.getElementById('submit');
const userBtn = document.getElementById('user');
const logoutBtn = document.getElementById('logout');

loginBtn.addEventListener('click', login);
userBtn.addEventListener('click', getUser);
logoutBtn.addEventListener('click', logout);

checkAuth();

